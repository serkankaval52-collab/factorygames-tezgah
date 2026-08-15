#!/usr/bin/env python3
"""FactoryGames sablon lint'i — kod/dosya duzlemindeki kapilar.

Kapsam (Asama 7 CI kapisi satirinin kod tarafi):
  1. SAHNE-BASELINE  : sahne dosyasi sablon varsayilanindan sapamaz (Sozlesme-2, P1 ikilisi)
  2. TEK-KAYNAK      : EditorBuildSettings tek sahne tasir
  3. PRESET-SAPMA    : motor ayarlari sablon setinden birebir (preset kararinin mekanik savunmasi)
  4. SECRET-SCAN     : depoya sir girmez (kural 25)
  5. HAM-ARTEFAKT    : goruntu/video/log dokumu depoya girmez (Sozlesme-4) + boyut tavani
  6. DIL-KAPISI      : koda gomulu kullanici-gorunur dize yasak (A3.6)

Varlik duzlemi (G1-G8, S1, P2/P4/P5/P7/P9a) `lint_varlik.py`dedir.

Cikis: 0 = tum kapilar yesil; 1 = en az bir kirmizi.
"VERI-YOK" sessizce gecmez: girdi kumesi bossa satir raporda ARTEFAKT KANITIYLA
(yol + bulunan dosya sayisi) yazilir (ilk-kosu.md §1).
"""
import argparse
import hashlib
import json
import os
import re
import sys

IZINLI_PREFAB_KOK = "Assets/Prefabs/"
HAM_UZANTILAR = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff",
                 ".psd", ".mp4", ".mov", ".wav", ".aiff"}
KOD_UZANTILARI = {".cs"}

SECRET_DESENLERI = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("Google API anahtari", re.compile(r"AIza[0-9A-Za-z_\-]{30,}")),
    ("Google OAuth token", re.compile(r"ya29\.[0-9A-Za-z_\-]{20,}")),
    ("AWS erisim anahtari", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Slack token", re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}")),
    ("Ozel anahtar blogu", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Genel sir atamasi", re.compile(
        r"(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']")),
]

# A3.6: kullaniciya gorunen metin yerellestirmededir, koda gomulmez.
# Vekil: harf iceren ve >=2 kelimeli dize; teknik dizeler (yol, ad, sabit) elenir.
KULLANICI_METNI = re.compile(r"\"([^\"\\]{4,})\"")
TEKNIK_DIZE = re.compile(
    r"^[A-Za-z0-9_./\\:#\-\+\*\(\)\[\]{}<>=,;%@!&|^~$?]*$|^\s*$")


class Rapor:
    def __init__(self):
        self.satirlar = []
        self.kirmizi = 0

    def ekle(self, kapi, durum, mesaj, kanit=""):
        self.satirlar.append((kapi, durum, mesaj, kanit))
        if durum == "KIRMIZI":
            self.kirmizi += 1

    def yaz(self):
        print(f"{'KAPI':<18} {'DURUM':<9} ACIKLAMA")
        print("-" * 92)
        for kapi, durum, mesaj, kanit in self.satirlar:
            print(f"{kapi:<18} {durum:<9} {mesaj}")
            if kanit:
                print(f"{'':<28}kanit: {kanit}")
        print("-" * 92)
        print(f"kirmizi: {self.kirmizi} / satir: {len(self.satirlar)}")


def dosyalar(kok, uzantilar=None, alt="Assets"):
    taban = os.path.join(kok, alt) if alt else kok
    if not os.path.isdir(taban):
        return []
    out = []
    for dirpath, dirnames, filenames in os.walk(taban):
        dirnames[:] = [d for d in dirnames if d not in
                       ("Library", "Temp", "Logs", "obj", "Build", ".git")]
        for fn in filenames:
            if uzantilar is None or os.path.splitext(fn)[1].lower() in uzantilar:
                out.append(os.path.join(dirpath, fn))
    return out


def rel(kok, yol):
    return os.path.relpath(yol, kok).replace("\\", "/")


def gameobject_sayisi(yol):
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            return sum(1 for ln in f if ln.startswith("GameObject:"))
    except OSError:
        return -1


def sha256(yol):
    """Satir sonu NORMALIZE edilmis sha256 (CRLF/CR -> LF).

    Gerekce (0A adim 4 saha bulgusu): ham sha256 platformlar arasi calismiyordu.
    Hash'ler Windows'ta CRLF'li calisma kopyasindan uretilmis, CI (Linux) ise ayni
    dosyalari LF ile checkout etmisti — 7 preset dosyasi "sapti" gorundu. Dosyalar
    AYNIYDI; sapan sey satir sonuydu. Preset dosyalarinin tamami metindir; normalize
    hash hem yanlis pozitifi keser hem gercek icerik degisikligini yakalamaya devam eder.
    """
    try:
        with open(yol, "rb") as f:
            veri = f.read()
    except OSError:
        return None
    veri = veri.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(veri).hexdigest()


# --------------------------------------------------------------------------- kapilar

def kapi_sahne_baseline(kok, r):
    bl_yol = os.path.join(kok, "scene-baseline.json")
    if not os.path.exists(bl_yol):
        r.ekle("SAHNE-BASELINE", "KIRMIZI",
               "scene-baseline.json yok — P1 referansi olculemez",
               f"aranan: {rel(kok, bl_yol)}")
        return
    try:
        with open(bl_yol, encoding="utf-8-sig") as f:
            bl = json.load(f)
        limit = int(bl["nesne_sayisi"])
    except (ValueError, KeyError, OSError) as ex:
        r.ekle("SAHNE-BASELINE", "KIRMIZI", f"baseline okunamadi: {type(ex).__name__}", bl_yol)
        return

    sahneler = dosyalar(kok, {".unity"})
    prefablar = dosyalar(kok, {".prefab"})
    if not sahneler:
        r.ekle("SAHNE-BASELINE", "VERI-YOK", "hic .unity dosyasi yok",
               f"taranan: Assets/**, bulunan: 0")
    for s in sahneler:
        n = gameobject_sayisi(s)
        p = rel(kok, s)
        if n > limit:
            r.ekle("SAHNE-BASELINE", "KIRMIZI",
                   f"{p}: {n} GameObject > baseline {limit}",
                   "sahne sablon varsayilanindan sapmis (Sozlesme-2)")
        else:
            r.ekle("SAHNE-BASELINE", "YESIL", f"{p}: {n} <= {limit}")

    for pf in prefablar:
        n = gameobject_sayisi(pf)
        p = rel(kok, pf)
        izinli = p.startswith(IZINLI_PREFAB_KOK)
        if n > 0 and not izinli:
            r.ekle("SAHNE-BASELINE", "KIRMIZI",
                   f"{p}: izinli kok disinda {n} GameObject",
                   f"varlik prefabi yalniz {IZINLI_PREFAB_KOK} altinda (kod-standardi §10)")
        else:
            r.ekle("SAHNE-BASELINE", "YESIL", f"{p}: prefab kurali saglandi")


def kapi_tek_kaynak(kok, r):
    yol = os.path.join(kok, "ProjectSettings", "EditorBuildSettings.asset")
    if not os.path.exists(yol):
        r.ekle("TEK-KAYNAK", "VERI-YOK", "EditorBuildSettings.asset yok", f"aranan: {rel(kok, yol)}")
        return
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            metin = f.read()
    except OSError as ex:
        r.ekle("TEK-KAYNAK", "KIRMIZI", f"okunamadi: {type(ex).__name__}", yol)
        return
    sahneler = re.findall(r"path:\s*(\S+\.unity)", metin)
    if len(sahneler) > 1:
        r.ekle("TEK-KAYNAK", "KIRMIZI",
               f"build listesinde {len(sahneler)} sahne var — tek sahne bekleniyor",
               "; ".join(sahneler))
    else:
        r.ekle("TEK-KAYNAK", "YESIL", f"build listesi sahne sayisi: {len(sahneler)}")


def kapi_preset_sapma(kok, r):
    ref_yol = os.path.join(kok, "tools", "lint", "preset-hashes.json")
    if not os.path.exists(ref_yol):
        r.ekle("PRESET-SAPMA", "VERI-YOK", "preset-hashes.json yok — sapma olculemez",
               f"aranan: {rel(kok, ref_yol)}")
        return
    try:
        # utf-8-sig: Windows araclari (PowerShell Out-File -Encoding utf8) BOM ekler;
        # BOM'lu JSON duz utf-8 okuyucuyu kirar. Lint her iki hali de kabul eder.
        with open(ref_yol, encoding="utf-8-sig") as f:
            ref = json.load(f)
    except (ValueError, OSError) as ex:
        r.ekle("PRESET-SAPMA", "KIRMIZI", f"referans okunamadi: {type(ex).__name__}", ref_yol)
        return

    sapan, eksik = [], []
    for p, beklenen in sorted(ref.get("dosyalar", {}).items()):
        tam = os.path.join(kok, p.replace("/", os.sep))
        if not os.path.exists(tam):
            eksik.append(p)
            continue
        if sha256(tam) != beklenen:
            sapan.append(p)

    if sapan or eksik:
        r.ekle("PRESET-SAPMA", "KIRMIZI",
               f"{len(sapan)} dosya sablon setinden sapti, {len(eksik)} dosya eksik",
               "; ".join(sapan[:5] + [f"EKSIK:{e}" for e in eksik[:5]]))
    else:
        r.ekle("PRESET-SAPMA", "YESIL",
               f"{len(ref.get('dosyalar', {}))} preset dosyasi sablonla birebir")


def kapi_secret(kok, r):
    hedefler = [y for y in dosyalar(kok, None, alt=None)
                if os.path.splitext(y)[1].lower() not in HAM_UZANTILAR
                and ".git" + os.sep not in y]
    bulgu = []
    for y in hedefler:
        try:
            with open(y, encoding="utf-8", errors="replace") as f:
                metin = f.read()
        except OSError:
            continue
        for ad, desen in SECRET_DESENLERI:
            m = desen.search(metin)
            if m:
                # Sirrin KENDISI rapora GIRMEZ (kural 25) — yalniz yer ve tur.
                satir = metin[:m.start()].count("\n") + 1
                bulgu.append(f"{rel(kok, y)}:{satir} ({ad})")
    if bulgu:
        r.ekle("SECRET-SCAN", "KIRMIZI", f"{len(bulgu)} olasi sir",
               "; ".join(bulgu[:6]) + "  [icerik raporlanmaz — kural 25]")
    else:
        r.ekle("SECRET-SCAN", "YESIL", f"{len(hedefler)} dosya tarandi, bulgu yok")


def kapi_ham_artefakt(kok, r, boyut_tavan_mb):
    """Sozlesme-4: KANIT ham dosyasi depoya girmez, cihazda kalir.

    Kapsam ayrimi (bilincli): `Assets/` altindaki gorseller OYUN VARLIGIDIR ve
    G1-G2 kapilarina tabidir — burada kirmizi degildir. Yasak olan, kanit/dokuman
    duzlemine (Assets disi) ham goruntu/video/log dokumu birakmaktir.
    """
    disaridakiler = [y for y in dosyalar(kok, HAM_UZANTILAR, alt=None)
                     if ".git" + os.sep not in y
                     and not rel(kok, y).startswith("Assets/")]
    if disaridakiler:
        detay = [f"{rel(kok, y)} ({os.path.getsize(y)/1048576:.2f} MB)" for y in disaridakiler[:6]]
        r.ekle("HAM-ARTEFAKT", "KIRMIZI",
               f"{len(disaridakiler)} ham artefakt Assets disinda (Sozlesme-4: cihazda kalir)",
               "; ".join(detay))
    else:
        r.ekle("HAM-ARTEFAKT", "YESIL", "Assets disinda ham goruntu/video artefakti yok")

    # Varlik butcesi: APK tavaninin (Ek C) on gostergesi. Tek dosya icin ayri esik
    # YOKTUR — Ek C'de olmayan sayi kapida kullanilamaz (kural 28), bu yuzden olcu
    # Assets toplamidir.
    assets = [y for y in dosyalar(kok, None) if ".git" + os.sep not in y]
    toplam_mb = sum(os.path.getsize(y) for y in assets) / 1048576 if assets else 0.0
    if boyut_tavan_mb is None:
        # Kural 28: Ek C'de deger yoksa TAHMIN URETILMEZ. Kapi atlanir ama "gecti"
        # SAYILMAZ (ilk-kosu.md §1) — satir artefakt kanitiyla raporlanir.
        r.ekle("BOYUT", "VERI-YOK",
               "uygulama_boyut_tavan_mb esiklerde yok — butce olculemez",
               f"olculen Assets toplami: {toplam_mb:.1f} MB ({len(assets)} dosya); "
               f"esik kullanicinin Ek C form donusunden gelecek")
    elif toplam_mb > boyut_tavan_mb:
        r.ekle("BOYUT", "KIRMIZI",
               f"Assets toplami {toplam_mb:.1f} MB > tavan {boyut_tavan_mb} MB",
               f"{len(assets)} dosya (Ek C uygulama_boyut_tavan_mb)")
    else:
        r.ekle("BOYUT", "YESIL",
               f"Assets toplami {toplam_mb:.1f} MB <= tavan {boyut_tavan_mb} MB")


def kapi_dil(kok, r):
    """A3.6 — kullaniciya GORUNEN metin koda gomulmez.

    Kapsam ayrimi (0A adim 4 saha bulgusu): ilk hali `Assets/Editor/` ve
    `Assets/Tests/` altindaki dosyalari da kirmizi yakiyordu. Ikisi de OYUNCUYA
    ULASMAZ — Editor kodu build'e girmez, test takimlari `UNITY_INCLUDE_TESTS`
    kisitiyla derlenmez. Ayni sekilde `throw` mesajlari ve attribute metinleri
    gelistirici yuzeyidir. Kapi artik yalnizca CALISMA ZAMANI kodunu arar.

    BILINEN SINIR (kayitli): tek kelimelik gorunur dizeler ("Skor", "Basla")
    elenmez — cok kelime kurali teknik dizeleri (yol, tur adi, sabit) yanlis
    pozitiften korumak icin var. Bu bosluk kabul edilmis ve rapora yazilmistir.
    """
    kod = [y for y in dosyalar(kok, KOD_UZANTILARI)
           if "/Editor/" not in "/" + rel(kok, y)
           and "/Tests/" not in "/" + rel(kok, y)]
    if not kod:
        r.ekle("DIL-KAPISI", "VERI-YOK",
               "taranacak runtime .cs dosyasi yok",
               "taranan: Assets/** (Editor/ haric), bulunan: 0")
        return
    bulgu = []
    for y in kod:
        try:
            with open(y, encoding="utf-8", errors="replace") as f:
                satirlar = f.read().splitlines()
        except OSError:
            continue
        for i, satir in enumerate(satirlar, 1):
            s = satir.strip()
            if s.startswith("//") or s.startswith("*") or s.startswith("///"):
                continue
            # Gelistirici yuzeyi — oyuncuya gorunmez: attribute metni, istisna
            # mesaji, gelistirme logu, nameof, Tooltip.
            if s.startswith("[") or "throw new" in s or "Exception(" in s:
                continue
            if "nameof(" in s or "[Tooltip" in s or "Debug.Log" in s or "Assert" in s:
                continue
            for m in KULLANICI_METNI.finditer(satir):
                metin = m.group(1)
                if TEKNIK_DIZE.match(metin):
                    continue
                if len(metin.split()) >= 2 and any(c.isalpha() for c in metin):
                    bulgu.append(f"{rel(kok, y)}:{i} -> \"{metin[:40]}\"")
    if bulgu:
        r.ekle("DIL-KAPISI", "KIRMIZI",
               f"{len(bulgu)} koda gomulu kullanici-gorunur dize (A3.6)",
               "; ".join(bulgu[:5]))
    else:
        r.ekle("DIL-KAPISI", "YESIL", f"{len(kod)} kod dosyasinda gomulu metin yok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kok", default=".", help="oyun reposu koku")
    ap.add_argument("--esikler", default=None)
    args = ap.parse_args()
    kok = os.path.abspath(args.kok)

    esik_yol = args.esikler or os.path.join(kok, "tools", "lint", "esikler.json")
    try:
        with open(esik_yol, encoding="utf-8-sig") as f:
            esikler = json.load(f)
    except (ValueError, OSError):
        print(f"HATA: esikler okunamadi: {esik_yol} — Ek C'de olmayan sayi kullanilamaz "
              f"(Sozlesme-8), lint kosmaz", file=sys.stderr)
        return 2

    r = Rapor()
    kapi_sahne_baseline(kok, r)
    kapi_tek_kaynak(kok, r)
    kapi_preset_sapma(kok, r)
    kapi_secret(kok, r)
    # get(...) varsayilani YOK: eksik esik "tahmin" degil VERI-YOK uretir (kural 28)
    kapi_ham_artefakt(kok, r, esikler.get("uygulama_boyut_tavan_mb"))
    kapi_dil(kok, r)
    r.yaz()
    return 1 if r.kirmizi else 0


if __name__ == "__main__":
    sys.exit(main())
