#!/usr/bin/env python3
"""Lint'in KENDI dogrulugunun testi — "kapi gercekten olcuyor mu?"

Gerekce (0A adim 3 / V3): esiklerin gercek bir oyunda tutup tutmadigi ancak gercek
varlikla olculur ve o olcum bu kosuda YAPILAMADI (kullanici karari: elde yalnizca
acemi donem oyunu vardi, yanlis orneklem olurdu — dusuk oran esigi degil o oyunu
yargilardi). Yerine olcum ARACININ dogrulugu kanitlanir: lint bilinen-dogru
degerlerde yesil, bilinen-kotu degerlerde KIRMIZI vermeli.

Once-kirmizi disiplini (Sozlesme-5): her kapi icin hem gecen hem KALAN ornek vardir;
kapi her zaman yesil yanan bir susleme degildir.

Kosum: python tools/lint/test_lint.py   (harici bagimlilik yok)
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

import lint_varlik as LV  # noqa: E402


class KontrastMatematigi(unittest.TestCase):
    """G4 — WCAG formulunun dis kaynakla dogrulanmasi (referans degerler WCAG 2.x)."""

    def test_siyah_beyaz_21e1(self):
        oran = LV.kontrast(LV.hex_rgb("#000000"), LV.hex_rgb("#FFFFFF"))
        self.assertAlmostEqual(oran, 21.0, places=2)

    def test_gri_beyaz_bilinen_deger(self):
        # #767676 uzerinde beyaz: WCAG AA metin esiginin (4.5) hemen ustu — kanonik ornek
        oran = LV.kontrast(LV.hex_rgb("#767676"), LV.hex_rgb("#FFFFFF"))
        self.assertGreaterEqual(oran, 4.5)
        self.assertLess(oran, 5.0)

    def test_ayni_renk_1e1(self):
        oran = LV.kontrast(LV.hex_rgb("#3366CC"), LV.hex_rgb("#3366CC"))
        self.assertAlmostEqual(oran, 1.0, places=6)


class RenkKorluguAyrimi(unittest.TestCase):
    """G6 — simulasyonun GERCEKTEN ayirt ettigi kanit."""

    def test_kirmizi_yesil_orani_dusuk(self):
        """WCAG orani bu cifti PARLAKLIK ekseninde dusuk bulur.

        Kayit: iki metrik farkli sey olcer — oran okunabilirligi (parlaklik farki),
        dE00 algisal ayrimi. Bu cift oranda dusuk, dE00'da yuksek cikar; ikisi de
        dogrudur. G6 bu yuzden ciftleri iki ayri olcuye boldu (v1.4.1).
        """
        kirmizi, yesil = LV.hex_rgb("#D40000"), LV.hex_rgb("#00A000")
        self.assertLess(LV.kontrast(kirmizi, yesil), 3.0)

    def test_zit_doygun_cift_simde_de_ayrik_kalir_GECER(self):
        """Zit doygun ciftler simulasyonda da AYIRT EDILIR — kapi dogru gecirir.

        Ilk okumada bu "kapinin sinir/eksigi" sanilmisti; mimar denetimi (v1.4.1)
        olcumle duzeltti: klasik kirmizi-yesil ailesi hicbir parlaklikta cokusmuyor
        (es-L* ciftlerinde bile protanopi 7-27 bandinda kaliyor). Yani gecirmek
        ALGISAL OLARAK DOGRUDUR; kapinin isi bu aile degil, karisim metamerleridir
        (bkz. test_CVD_KILIDI_...). Machado matrislerine gecis onerisi bu olcume
        dayanarak REDDEDILDI.

        G6'nin ek kurali (renk tek basina bilgi tasiyamaz; bicim/ikon destegi)
        bagimsiz gerekcelerle ZORUNLU kalir.
        """
        kir, yes = LV.hex_rgb("#D40000"), LV.hex_rgb("#00A000")
        for t in ("protanopi", "doteranopi", "tritanopi"):
            self.assertGreaterEqual(
                LV.delta_e(LV.cvd_uygula(kir, t), LV.cvd_uygula(yes, t)), 2.0,
                f"{t}: olcum degisti — CVD modeli veya kayit guncellenmeli")

    def test_es_L_kirmizi_yesil_de_cokusmuyor(self):
        """Mimar denetiminin 1. maddesi: es-parlaklik da cokusu uretmiyor."""
        for a, b in [("#D40000", "#007A00"), ("#C0504D", "#4F9E3F"),
                     ("#AA5A50", "#5E9640")]:
            ra, rb = LV.hex_rgb(a), LV.hex_rgb(b)
            for t in ("protanopi", "doteranopi"):
                self.assertGreater(
                    LV.delta_e(LV.cvd_uygula(ra, t), LV.cvd_uygula(rb, t)), 2.0,
                    f"{a}/{b} {t}: beklenmedik cokus")

    def test_ciede2000_referans_verisi(self):
        """CIEDE2000 dogrulugu — Sharma-Wu-Dalal (2005) yayinlanmis test cifleri.

        Not (durustluk kaydi): ilk denemede Pair 8 ile Pair 12 karistirilarak yanlis
        beklenen deger yazilmis ve implementasyon hatali sanilmisti; dogru esleme ile
        besi de birebir tutuyor.
        """
        for lab1, lab2, beklenen in [
            ((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485), 2.0425),
            ((50.0, 2.49, -0.001), (50.0, -2.49, 0.0009), 7.1792),
            ((50.0, -0.001, 2.49), (50.0, 0.0009, -2.49), 4.8045),
            ((50.0, 0.0, 0.0), (50.0, -1.0, 2.0), 2.3669),
            ((50.0, 2.5, 0.0), (73.0, 25.0, -18.0), 27.1492),
        ]:
            self.assertAlmostEqual(LV.ciede2000(lab1, lab2), beklenen, places=3)

    def test_mavi_sari_protanopide_ayrik_kalir(self):
        mavi, sari = LV.hex_rgb("#0050C8"), LV.hex_rgb("#FFD200")
        prot = LV.kontrast(LV.cvd_uygula(mavi, "protanopi"),
                           LV.cvd_uygula(sari, "protanopi"))
        self.assertGreater(prot, 3.0,
                           "mavi-sari cifti protanopide de ayrik kalmaliydi")


class KapiUctanUca(unittest.TestCase):
    """Kapinin surec olarak once-KIRMIZI, sonra yesil verdigi kanit."""

    ESIKLER = {
        "gorsel_palet_kademe": 5,
        "gorsel_kontrast_ana_ozne": 3.0,
        "gorsel_kontrast_ui_metin": 4.5,
        "gorsel_sinyal_deltae_min": 2.0,
        "gorsel_anim_kare_band": [4, 12],
        "gorsel_anim_dongu_ortusme": 90,
        "gorsel_alpha_sacak_yuzde": 2,
        "gorsel_atlas_doluluk_yuzde": 70,
        "ses_lufs_band": [-17, -15],
        "ses_tepe_dbtp": -1,
        "ses_sfx_sure_tavan_sn": 2,
        "uygulama_boyut_tavan_mb": 150,
    }

    # DOYGUN palet — v1.4.1 kararinin sinavi. Bu palet WCAG-oran kapisinda (eski G6)
    # tehlike/vurgu yuzunden 4/4 DUSUYORDU; dE00 kapisinda GECMELI. Olculdu (0A-3):
    #   tehlike/vurgu dE00 -> normal 49.42 · prot 15.23 · dote 10.70 · trit 2.55
    #   tehlike/arka  oran -> prot 8.79 · dote 10.91 · trit 5.70
    #   ana_ozne/arka oran -> prot 5.46 · dote 4.50 · trit 11.51
    # Yani karar, doygun paleti serbest birakti; desature zorlamasi kalkti.
    IYI_PALET = {"roller": {
        "arka_plan": "#101418", "ana_ozne": "#40D0F0", "vurgu": "#FFD200",
        "tehlike": "#FF5A5A", "ui_metin": "#FFFFFF", "ui_zemin": "#101418"}}

    KOTU_PALET = {"roller": {
        "arka_plan": "#808080", "ana_ozne": "#8A8A8A", "vurgu": "#8F8F8F",
        "tehlike": "#949494", "ui_metin": "#9A9A9A", "ui_zemin": "#808080"}}

    def _kos(self, palet):
        with tempfile.TemporaryDirectory() as kok:
            sa = os.path.join(kok, "Assets", "StreamingAssets")
            os.makedirs(sa)
            with open(os.path.join(sa, "palette.json"), "w", encoding="utf-8") as f:
                json.dump(palet, f)
            r = LV.Rapor()
            LV.kapi_palet(kok, self.ESIKLER, r)
            return r

    def test_iyi_palet_yesil(self):
        r = self._kos(self.IYI_PALET)
        self.assertEqual(r.kirmizi, 0, "gecerli palet kirmizi verdi")

    def test_kotu_palet_KIRMIZI(self):
        r = self._kos(self.KOTU_PALET)
        self.assertGreater(r.kirmizi, 0,
                           "ayirt edilemeyen gri palet YESIL gecti — kapi olcmuyor")

    def test_NORMAL_TABAN_ayirt_edilemeyen_cift_KIRMIZI(self):
        """NORMAL-GORUS TABANI (CVD disleri DEGIL — onun kilidi asagidaki testte).

        Bu test yalnizca sunu olcer: iki rol birbirine cok yakin secilirse kapi
        NORMAL goruste kirmizi verir mi? (dE00 1.20). Kapinin CVD tarafini
        sinamaz; damgasi bu yuzden 'normal taban'dir (mimar denetimi, v0.1.3).
        """
        palet = {"roller": {
            "arka_plan": "#101418", "ana_ozne": "#40D0F0",
            "vurgu": "#E74C3C", "tehlike": "#E85142",   # dE00 = 1.20 (normal)
            "ui_metin": "#FFFFFF", "ui_zemin": "#101418"}}
        r = self._kos(palet)
        de_satirlari = [s for s in r.satirlar if s[0] == "G6-dE"]
        normal = [s for s in de_satirlari if s[2].startswith("normal")]
        self.assertTrue(normal and normal[0][1] == "KIRMIZI",
                        "normal goruste ayirt edilemeyen cift YESIL gecti")

    def test_CVD_KILIDI_karisim_metameri_protanopide_KIRMIZI(self):
        """KAPININ CVD DISLERI — asil kilit (mimar karari, v1.4.1/v0.1.3).

        Karisim metameri: normal goruste APAYRI (dE00 83.13) iken protanopide
        neredeyse AYNI (dE00 1.26) olan cift. Kapi bunu YAKALAMAK ZORUNDA —
        yakalamazsa CVD tarafi fiilen olu demektir.

        Bu, "kirmizi-yesil ailesini yakalamiyor" gozleminin dogru okunusudur:
        zit doygun ciftler simulasyonda da gercekten ayirt edilir (kapi onlari
        gecirir — algisal olarak DOGRU); kapinin isi, normal-gorusun ayirdigi
        ama dikromatin ayiramadigi ciftleri yakalamaktir. Olculdu: yakaliyor.
        """
        palet = {"roller": {
            "arka_plan": "#101418", "ana_ozne": "#40D0F0",
            "vurgu": "#33FF00", "tehlike": "#C64040",
            "ui_metin": "#FFFFFF", "ui_zemin": "#101418"}}
        r = self._kos(palet)
        de = [s for s in r.satirlar if s[0] == "G6-dE"]

        normal = [s for s in de if s[2].startswith("normal")]
        self.assertTrue(normal and normal[0][1] == "YESIL",
                        "cift normal goruste ayrik olmaliydi (dE00 ~83)")

        prot = [s for s in de if s[2].startswith("protanopi")]
        self.assertTrue(prot and prot[0][1] == "KIRMIZI",
                        "protanopide cokusen metamer YESIL gecti — CVD disleri olu")

        # Ham deger de kilitlensin: model degisirse test bunu soyler.
        th, vu = LV.hex_rgb("#C64040"), LV.hex_rgb("#33FF00")
        self.assertGreater(LV.delta_e(th, vu), 50.0)
        self.assertLess(LV.delta_e(LV.cvd_uygula(th, "protanopi"),
                                   LV.cvd_uygula(vu, "protanopi")), 2.0)

    def test_doygun_mavi_turuncu_dort_goruste_YESIL(self):
        """Yanlis-pozitif testi: gercekten ayrik bir doygun cift kapiyi gecmeli."""
        mavi, turuncu = LV.hex_rgb("#1E5AFF"), LV.hex_rgb("#FF7A1E")
        self.assertGreaterEqual(LV.delta_e(mavi, turuncu), 2.0, "normal gorus")
        for t in ("protanopi", "doteranopi", "tritanopi"):
            self.assertGreaterEqual(
                LV.delta_e(LV.cvd_uygula(mavi, t), LV.cvd_uygula(turuncu, t)), 2.0, t)

    def test_deltae_esigi_yoksa_veri_yok(self):
        """Kural 28: esik yoksa tahmin uretilmez, kapi 'gecti' de sayilmaz."""
        esikler = dict(self.ESIKLER)
        esikler.pop("gorsel_sinyal_deltae_min")
        with tempfile.TemporaryDirectory() as kok:
            sa = os.path.join(kok, "Assets", "StreamingAssets")
            os.makedirs(sa)
            with open(os.path.join(sa, "palette.json"), "w", encoding="utf-8") as f:
                json.dump(self.IYI_PALET, f)
            r = LV.Rapor()
            LV.kapi_palet(kok, esikler, r)
            de = [s for s in r.satirlar if s[0] == "G6-dE"]
            self.assertTrue(de and de[0][1] == "VERI-YOK", "eksik esik sessizce gecti")
            self.assertTrue(de[0][3], "VERI-YOK satiri kanitsiz")

    def test_palet_yoksa_veri_yok_ve_kanit(self):
        with tempfile.TemporaryDirectory() as kok:
            r = LV.Rapor()
            LV.kapi_palet(kok, self.ESIKLER, r)
            durumlar = [s[1] for s in r.satirlar]
            self.assertIn("VERI-YOK", durumlar, "eksik girdi sessizce gecti")
            self.assertEqual(r.kirmizi, 0)
            self.assertTrue(any(s[3] for s in r.satirlar), "VERI-YOK satiri kanitsiz")


class LintSurecKontrolu(unittest.TestCase):
    """lint.py'nin ihlali gercekten KIRMIZI yaptigi kanit (surec cikis kodu)."""

    def test_baseline_asimi_kirmizi(self):
        with tempfile.TemporaryDirectory() as kok:
            os.makedirs(os.path.join(kok, "Assets", "Scenes"))
            os.makedirs(os.path.join(kok, "tools", "lint"))
            with open(os.path.join(kok, "scene-baseline.json"), "w", encoding="utf-8") as f:
                json.dump({"pin": "test", "dosya": "x", "sha256": "y", "nesne_sayisi": 2}, f)
            with open(os.path.join(kok, "tools", "lint", "esikler.json"), "w", encoding="utf-8") as f:
                json.dump({"uygulama_boyut_tavan_mb": 150}, f)
            # 40 nesneli sahne — 0A adim 5'in (a) kasitli ihlalinin birebir karsiligi
            with open(os.path.join(kok, "Assets", "Scenes", "S.unity"), "w", encoding="utf-8") as f:
                f.write("GameObject:\n" * 40)

            p = subprocess.run([sys.executable, os.path.join(BURASI, "lint.py"), "--kok", kok],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 1, "baseline asimi kirmizi vermedi\n" + p.stdout)
            self.assertIn("SAHNE-BASELINE", p.stdout)

    def test_temiz_agac_yesil(self):
        with tempfile.TemporaryDirectory() as kok:
            os.makedirs(os.path.join(kok, "Assets", "Scenes"))
            os.makedirs(os.path.join(kok, "tools", "lint"))
            with open(os.path.join(kok, "scene-baseline.json"), "w", encoding="utf-8") as f:
                json.dump({"pin": "test", "dosya": "x", "sha256": "y", "nesne_sayisi": 2}, f)
            with open(os.path.join(kok, "tools", "lint", "esikler.json"), "w", encoding="utf-8") as f:
                json.dump({"uygulama_boyut_tavan_mb": 150}, f)
            with open(os.path.join(kok, "Assets", "Scenes", "S.unity"), "w", encoding="utf-8") as f:
                f.write("GameObject:\nGameObject:\n")

            p = subprocess.run([sys.executable, os.path.join(BURASI, "lint.py"), "--kok", kok],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, "temiz agac kirmizi verdi\n" + p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
