#!/usr/bin/env python3
"""FactoryGames varlik/manifest lint'i — gorsel sozlesme + premium (bassiz kisim).

Kapsam (Asama 7 CI kapisi satirinin varlik tarafi):
  G1 palet rampasi (palette.json)          G4 kontrast (WCAG, saf hesap)
  G6 renk korlugu ayrimi (saf matematik)   G5 tutarlilik ucslusu (manifest alanlari)
  G7 animasyon bandi (manifest)            G8 yeniden uretilebilirlik (manifest satiri)
  G2 sprite geometrisi (manifest)          S1 ses (manifest + FFmpeg olcumu)
  P2 geri bildirim doygunlugu  P4 bos kare yok  P5 ham hata yok (lint tarafi)
  P7 hareket imzasi            P9(a) ses tamponu yapilandirmasi

TASARIM: piksel/dalga formu tarayan kapilar (G1 piksel orani, G2 alpha sacagi,
G3 siluet, S1 LUFS) VARLIK MANIFESTINDEN okur; manifest satiri olcumu tasir
(G8 gerekcesi: satirdan ayni cikti yeniden uretilebilmeli). Boylece lint hem
CI'da hizli kosar hem de olcumun kaynagi tek yerde toplanir.

"VERI-YOK" sessizce gecmez (ilk-kosu.md §1): girdi yoksa satir ARTEFAKT KANITIYLA
(aranan yol + bulunan sayi) raporlanir; kapi "gecti" SAYILMAZ.

Cikis: 0 = kirmizi yok; 1 = en az bir kirmizi.
"""
import argparse
import json
import math
import os
import sys

# Renk korlugu simulasyon matrisleri (Brettel/Vienot yaklasimi — lint ici sabit, G6)
CVD = {
    "protanopi":  ((0.567, 0.433, 0.0), (0.558, 0.442, 0.0), (0.0, 0.242, 0.758)),
    "doteranopi": ((0.625, 0.375, 0.0), (0.700, 0.300, 0.0), (0.0, 0.300, 0.700)),
    "tritanopi":  ((0.950, 0.050, 0.0), (0.0, 0.433, 0.567), (0.0, 0.475, 0.525)),
}
# G6 (v1.4.1): iki farkli olcu. Arka plan ciftleri OKUNABILIRLIK sorusudur -> WCAG orani.
# tehlike<->vurgu ise SINYAL AYRIMI sorusudur -> CIEDE2000 (oran metrigi bu ciftte
# okunabilirlik vekiliydi ve paleti zorla desature ediyordu; 0A-3 olcumu).
ORAN_CIFTLERI = [("tehlike", "arka_plan"), ("ana_ozne", "arka_plan")]
SINYAL_CIFTI = ("tehlike", "vurgu")
ZORUNLU_ROLLER = ["arka_plan", "ana_ozne", "vurgu", "tehlike", "ui_metin", "ui_zemin"]
G5_ALANLARI = ["perspektif", "cizgi_kalinligi_bandi", "golge_yonu"]
P4_DURUMLARI = ["yukleme", "izin_isteme", "ag_hatasi", "bos_icerik", "hata"]


class Rapor:
    def __init__(self):
        self.satirlar, self.kirmizi = [], 0

    def ekle(self, kapi, durum, mesaj, kanit=""):
        self.satirlar.append((kapi, durum, mesaj, kanit))
        if durum == "KIRMIZI":
            self.kirmizi += 1

    def yaz(self):
        print(f"{'KAPI':<14} {'DURUM':<9} ACIKLAMA")
        print("-" * 92)
        for kapi, durum, mesaj, kanit in self.satirlar:
            print(f"{kapi:<14} {durum:<9} {mesaj}")
            if kanit:
                print(f"{'':<24}kanit: {kanit}")
        print("-" * 92)
        print(f"kirmizi: {self.kirmizi} / satir: {len(self.satirlar)}")


def oku_json(yol):
    try:
        # utf-8-sig: Windows araclari BOM ekleyebilir (0A saha bulgusu)
        with open(yol, encoding="utf-8-sig") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "dosya yok"
    except (ValueError, OSError) as ex:
        return None, f"{type(ex).__name__}: {ex}"


def hex_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"gecersiz hex: {h}")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def gorece_parlaklik(rgb):
    def kanal(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (kanal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontrast(rgb1, rgb2):
    l1, l2 = gorece_parlaklik(rgb1), gorece_parlaklik(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def cvd_uygula(rgb, tur):
    m = CVD[tur]
    return tuple(min(1.0, max(0.0, sum(m[i][j] * rgb[j] for j in range(3)))) for i in range(3))


# --------------------------------------------------------------------- CIEDE2000
# sRGB -> XYZ (D65) -> CIELab -> dE00. Harici bagimlilik YOK (kurulum tablosu disi
# paket kurulmaz). Referans: CIE 142-2001 / Sharma-Wu-Dalal (2005) test verisiyle
# test_lint.py'de dogrulanir.

D65 = (0.95047, 1.00000, 1.08883)


def _srgb_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb_lab(rgb):
    r, g, b = (_srgb_lin(c) for c in rgb)
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    def f(t):
        return t ** (1.0 / 3.0) if t > 216.0 / 24389.0 else (841.0 / 108.0) * t + 4.0 / 29.0

    fx, fy, fz = (f(v / w) for v, w in zip((x, y, z), D65))
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def ciede2000(lab1, lab2, kL=1.0, kC=1.0, kH=1.0):
    """CIE 2000 renk farki (dE00). k carpanlari 1 (gorsel-sozlesme G6)."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    Cbar = (C1 + C2) / 2.0
    C7 = Cbar ** 7
    G = 0.5 * (1.0 - math.sqrt(C7 / (C7 + 25.0 ** 7))) if C7 else 0.5

    a1p, a2p = (1.0 + G) * a1, (1.0 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)

    def hp(ap, bp):
        if ap == 0.0 and bp == 0.0:
            return 0.0
        h = math.degrees(math.atan2(bp, ap))
        return h + 360.0 if h < 0.0 else h

    h1p, h2p = hp(a1p, b1), hp(a2p, b2)

    dLp = L2 - L1
    dCp = C2p - C1p

    if C1p * C2p == 0.0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180.0:
        dhp = h2p - h1p
    elif h2p - h1p > 180.0:
        dhp = h2p - h1p - 360.0
    else:
        dhp = h2p - h1p + 360.0
    dHp = 2.0 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2.0)

    Lbarp = (L1 + L2) / 2.0
    Cbarp = (C1p + C2p) / 2.0

    if C1p * C2p == 0.0:
        hbarp = h1p + h2p
    elif abs(h1p - h2p) <= 180.0:
        hbarp = (h1p + h2p) / 2.0
    elif h1p + h2p < 360.0:
        hbarp = (h1p + h2p + 360.0) / 2.0
    else:
        hbarp = (h1p + h2p - 360.0) / 2.0

    T = (1.0
         - 0.17 * math.cos(math.radians(hbarp - 30.0))
         + 0.24 * math.cos(math.radians(2.0 * hbarp))
         + 0.32 * math.cos(math.radians(3.0 * hbarp + 6.0))
         - 0.20 * math.cos(math.radians(4.0 * hbarp - 63.0)))

    dtheta = 30.0 * math.exp(-(((hbarp - 275.0) / 25.0) ** 2))
    Cbarp7 = Cbarp ** 7
    RC = 2.0 * math.sqrt(Cbarp7 / (Cbarp7 + 25.0 ** 7)) if Cbarp7 else 0.0
    SL = 1.0 + (0.015 * (Lbarp - 50.0) ** 2) / math.sqrt(20.0 + (Lbarp - 50.0) ** 2)
    SC = 1.0 + 0.045 * Cbarp
    SH = 1.0 + 0.015 * Cbarp * T
    RT = -math.sin(math.radians(2.0 * dtheta)) * RC

    tL = dLp / (kL * SL)
    tC = dCp / (kC * SC)
    tH = dHp / (kH * SH)
    return math.sqrt(tL * tL + tC * tC + tH * tH + RT * tC * tH)


def delta_e(rgb1, rgb2):
    return ciede2000(rgb_lab(rgb1), rgb_lab(rgb2))


# --------------------------------------------------------------------------- kapilar

def kapi_palet(kok, esikler, r):
    yol = os.path.join(kok, "Assets", "StreamingAssets", "palette.json")
    palet, hata = oku_json(yol)
    if palet is None:
        r.ekle("G1/G4/G6", "VERI-YOK", f"palette.json okunamadi ({hata})",
               f"aranan: Assets/StreamingAssets/palette.json")
        return None

    roller = palet.get("roller", {})
    eksik = [x for x in ZORUNLU_ROLLER if x not in roller]
    if eksik:
        r.ekle("G1", "KIRMIZI", f"palette.json'da eksik rol: {', '.join(eksik)}",
               f"zorunlu: {', '.join(ZORUNLU_ROLLER)}")
        return None

    kademe = esikler.get("gorsel_palet_kademe", 5)
    taban = {}
    for ad, deger in roller.items():
        try:
            if isinstance(deger, dict):
                taban[ad] = hex_rgb(deger["taban"])
                n = len(deger.get("kademeler", []))
                if n and n != kademe:
                    r.ekle("G1", "KIRMIZI", f"{ad}: {n} kademe, beklenen {kademe}",
                           "Ek C gorsel_palet_kademe")
            else:
                taban[ad] = hex_rgb(str(deger))
        except (ValueError, KeyError) as ex:
            r.ekle("G1", "KIRMIZI", f"{ad}: renk cozumlenemedi ({ex})", yol)
            return None
    r.ekle("G1", "YESIL", f"{len(taban)} rol tabani ve kademe sayisi gecerli")

    # G4 — WCAG kontrast (saf hesap, harici arac yok)
    ana = esikler.get("gorsel_kontrast_ana_ozne", 3.0)
    ui = esikler.get("gorsel_kontrast_ui_metin", 4.5)
    for a, b, esik, ad in [("ana_ozne", "arka_plan", ana, "ana ozne/arka plan"),
                           ("ui_metin", "ui_zemin", ui, "UI metin/zemin"),
                           ("vurgu", "arka_plan", ana, "vurgu/arka plan"),
                           ("tehlike", "arka_plan", ana, "tehlike/arka plan")]:
        oran = kontrast(taban[a], taban[b])
        if oran < esik:
            r.ekle("G4", "KIRMIZI", f"{ad}: {oran:.2f} < {esik}", "WCAG gorece parlaklik")
        else:
            r.ekle("G4", "YESIL", f"{ad}: {oran:.2f} >= {esik}")

    # G6 (a) — arka plan ciftleri: okunabilirlik, her simulasyonda WCAG orani
    for tur in CVD:
        for a, b in ORAN_CIFTLERI:
            oran = kontrast(cvd_uygula(taban[a], tur), cvd_uygula(taban[b], tur))
            if oran < ana:
                r.ekle("G6", "KIRMIZI", f"{tur}: {a}/{b} oran {oran:.2f} < {ana}",
                       "renk TEK BASINA bilgi tasiyamaz (G6)")
            else:
                r.ekle("G6", "YESIL", f"{tur}: {a}/{b} oran {oran:.2f} >= {ana}")

    # G6 (b) — sinyal cifti (tehlike<->vurgu): CIEDE2000, normal + 3 simulasyon
    de_min = esikler.get("gorsel_sinyal_deltae_min")
    a, b = SINYAL_CIFTI
    if de_min is None:
        r.ekle("G6-dE", "VERI-YOK", "gorsel_sinyal_deltae_min esiklerde yok",
               "kural 28: Ek C'de olmayan sayi kapida kullanilamaz; kapi 'gecti' SAYILMAZ")
    else:
        for ad, c1, c2 in [("normal", taban[a], taban[b])] + \
                          [(t, cvd_uygula(taban[a], t), cvd_uygula(taban[b], t)) for t in CVD]:
            de = delta_e(c1, c2)
            if de < de_min:
                r.ekle("G6-dE", "KIRMIZI", f"{ad}: {a}/{b} dE00 {de:.2f} < {de_min}",
                       "sinyal cifti ayirt edilemiyor; biçim/ikon destegi zorunlu (G6 ek kurali)")
            else:
                r.ekle("G6-dE", "YESIL", f"{ad}: {a}/{b} dE00 {de:.2f} >= {de_min}")
    return taban


def kapi_varlik_manifest(kok, esikler, r):
    yol = os.path.join(kok, "Assets", "StreamingAssets", "asset-manifest.json")
    man, hata = oku_json(yol)
    if man is None:
        r.ekle("G2/G5/G7/G8", "VERI-YOK", f"asset-manifest.json okunamadi ({hata})",
               "aranan: Assets/StreamingAssets/asset-manifest.json, bulunan varlik: 0")
        r.ekle("S1", "VERI-YOK", "ses manifesti yok — LUFS/tepe olculemedi",
               "ayni dosya; olcum FFmpeg ebur128 ile manifest satirina yazilir")
        return

    # G5 — tutarlilik ucslusu tek deger olmali
    ucslu = man.get("stil", {})
    eksik = [a for a in G5_ALANLARI if not ucslu.get(a)]
    if eksik:
        r.ekle("G5", "KIRMIZI", f"stil ucslusunde eksik alan: {', '.join(eksik)}",
               "degerler sanat yonu paketinden gelir; beyanin DOGRULUGU Asama 8'de")
    else:
        r.ekle("G5", "YESIL", f"stil ucslusu tam: {ucslu}")

    varliklar = man.get("varliklar", [])
    if not varliklar:
        r.ekle("G2/G7/G8", "VERI-YOK", "manifestte varlik yok", f"{yol}: varliklar=[]")
        return

    ppu = {v.get("pixels_per_unit") for v in varliklar if v.get("tur") == "sprite"}
    if len(ppu) > 1:
        r.ekle("G2", "KIRMIZI", f"birden fazla pixels-per-unit: {sorted(ppu)}",
               "tum sprite'lar tek ppu (G2)")
    elif ppu:
        r.ekle("G2", "YESIL", f"tek pixels-per-unit: {ppu.pop()}")

    alpha_tavan = esikler.get("gorsel_alpha_sacak_yuzde", 2)
    atlas_min = esikler.get("gorsel_atlas_doluluk_yuzde", 70)
    kare_alt, kare_ust = esikler.get("gorsel_anim_kare_band", [4, 12])
    ortusme_min = esikler.get("gorsel_anim_dongu_ortusme", 90)

    for v in varliklar:
        ad = v.get("ad", "<adsiz>")
        if "alpha_sacak_yuzde" in v and v["alpha_sacak_yuzde"] > alpha_tavan:
            r.ekle("G2", "KIRMIZI", f"{ad}: alpha sacagi {v['alpha_sacak_yuzde']} > {alpha_tavan}")
        if "atlas_doluluk_yuzde" in v and v["atlas_doluluk_yuzde"] < atlas_min:
            r.ekle("G2", "KIRMIZI", f"{ad}: atlas doluluk {v['atlas_doluluk_yuzde']} < {atlas_min}")
        if v.get("tur") == "animasyon":
            kare = v.get("kare_sayisi")
            if kare is None or not (kare_alt <= kare <= kare_ust):
                r.ekle("G7", "KIRMIZI", f"{ad}: kare {kare} bandin ({kare_alt}-{kare_ust}) disinda")
            if v.get("dongu") and v.get("dongu_ortusme_yuzde", 0) < ortusme_min:
                r.ekle("G7", "KIRMIZI",
                       f"{ad}: dongu ortusmesi {v.get('dongu_ortusme_yuzde')} < {ortusme_min}")
        # G8 — satir donusumu PARAMETRELERIYLE tasimali
        eksik8 = [k for k in ("kaynak_hash", "donusum", "parametreler", "arac_surumu")
                  if k not in v]
        if eksik8:
            r.ekle("G8", "KIRMIZI", f"{ad}: yeniden uretim alanlari eksik: {', '.join(eksik8)}",
                   "satirdan ayni cikti uretilebilmeli (G8)")

    if not any(s[0] in ("G2", "G7", "G8") and s[1] == "KIRMIZI" for s in r.satirlar):
        r.ekle("G2/G7/G8", "YESIL", f"{len(varliklar)} varlik satiri kurallara uygun")

    # S1 — ses olcumleri manifest satirindan
    sesler = [v for v in varliklar if v.get("tur") == "ses"]
    if not sesler:
        r.ekle("S1", "VERI-YOK", "manifestte ses varligi yok", f"varlik sayisi: {len(varliklar)}")
    else:
        lufs_alt, lufs_ust = esikler.get("ses_lufs_band", [-17, -15])
        tepe = esikler.get("ses_tepe_dbtp", -1)
        sure_tavan = esikler.get("ses_sfx_sure_tavan_sn", 2)
        for v in sesler:
            ad = v.get("ad", "<adsiz>")
            if "lufs" not in v:
                r.ekle("S1", "KIRMIZI", f"{ad}: lufs olcumu yok (FFmpeg ebur128 bekleniyor)")
                continue
            if not (lufs_alt <= v["lufs"] <= lufs_ust):
                r.ekle("S1", "KIRMIZI", f"{ad}: {v['lufs']} LUFS bandin ({lufs_alt}..{lufs_ust}) disinda")
            if v.get("tepe_dbtp", -99) > tepe:
                r.ekle("S1", "KIRMIZI", f"{ad}: tepe {v['tepe_dbtp']} > {tepe} dBTP")
            if v.get("sure_sn", 0) > sure_tavan:
                r.ekle("S1", "KIRMIZI", f"{ad}: sure {v['sure_sn']} sn > {sure_tavan} sn")
        if not any(s[0] == "S1" and s[1] == "KIRMIZI" for s in r.satirlar):
            r.ekle("S1", "YESIL", f"{len(sesler)} ses varligi bandda")


def kapi_premium(kok, esikler, r):
    yol = os.path.join(kok, "Assets", "StreamingAssets", "premium-manifest.json")
    man, hata = oku_json(yol)
    if man is None:
        r.ekle("P2/P4/P7/P9a", "VERI-YOK", f"premium-manifest.json okunamadi ({hata})",
               "aranan: Assets/StreamingAssets/premium-manifest.json")
        return

    # P2 — her oyuncu eylemi >=1 gorsel karsilik
    eylemler = man.get("eylemler", [])
    if not eylemler:
        r.ekle("P2", "VERI-YOK", "eylem listesi bos", f"{yol}: eylemler=[]")
    else:
        karsiliksiz = [e.get("ad", "<adsiz>") for e in eylemler
                       if not e.get("gorsel_karsilik")]
        if karsiliksiz:
            r.ekle("P2", "KIRMIZI", f"gorsel karsiligi olmayan eylem: {', '.join(karsiliksiz)}",
                   "kritik geri bildirim yalniz sese baglanamaz (B6)")
        else:
            r.ekle("P2", "YESIL", f"{len(eylemler)} eylemin tamami gorsel karsilikli")

    # P4 — sayilabilir durum listesi
    durumlar = set(man.get("durumlar", []))
    eksik = [d for d in P4_DURUMLARI if d not in durumlar]
    if eksik:
        r.ekle("P4", "KIRMIZI", f"tanimsiz durum: {', '.join(eksik)}",
               f"zorunlu liste: {', '.join(P4_DURUMLARI)}")
    else:
        r.ekle("P4", "YESIL", f"{len(P4_DURUMLARI)} durumun tamami tanimli")

    # P5 (lint tarafi) — sessiz toparlanma olayi beyan edilmis mi
    if man.get("sessiz_toparlanma_olayi") is True:
        r.ekle("P5", "YESIL", "sessiz_toparlanma analitik olayi beyan edildi")
    else:
        r.ekle("P5", "KIRMIZI", "sessiz_toparlanma olayi beyan edilmedi",
               "oyuncudan gizlenen bizden gizlenmez (P5)")

    # P7 — easing seti sinirli liste
    izinli = set(man.get("easing_seti", []))
    kullanilan = {a.get("easing") for a in man.get("animasyonlar", []) if a.get("easing")}
    disari = sorted(kullanilan - izinli)
    if not izinli:
        r.ekle("P7", "VERI-YOK", "easing seti tanimsiz", f"{yol}: easing_seti=[]")
    elif disari:
        r.ekle("P7", "KIRMIZI", f"liste disi egri: {', '.join(disari)}", "tek hareket dili (P7)")
    else:
        r.ekle("P7", "YESIL", f"{len(kullanilan)} animasyon egrisi listede")

    # P9(a) — ses tamponu yapilandirmasi (ikili)
    if man.get("ses_tamponu") == "best_latency":
        r.ekle("P9a", "YESIL", "DSP tamponu 'best latency' tarafinda")
    else:
        r.ekle("P9a", "KIRMIZI", f"ses tamponu: {man.get('ses_tamponu')!r} — 'best_latency' bekleniyor",
               "elle ayar Sozlesme-2 ihlali; deger surumlu presette sabit")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kok", default=".")
    ap.add_argument("--esikler", default=None)
    args = ap.parse_args()
    kok = os.path.abspath(args.kok)

    esik_yol = args.esikler or os.path.join(kok, "tools", "lint", "esikler.json")
    esikler, hata = oku_json(esik_yol)
    if esikler is None:
        print(f"HATA: esikler okunamadi ({hata}): {esik_yol} — Ek C'de olmayan sayi "
              f"kapida kullanilamaz (Sozlesme-8), lint kosmaz", file=sys.stderr)
        return 2

    r = Rapor()
    kapi_palet(kok, esikler, r)
    kapi_varlik_manifest(kok, esikler, r)
    kapi_premium(kok, esikler, r)
    r.yaz()
    return 1 if r.kirmizi else 0


if __name__ == "__main__":
    sys.exit(main())
