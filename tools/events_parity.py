#!/usr/bin/env python3
"""B4 olay haritasi <-> kod sabitleri paritesi (Asama 2 gecis kriterinin CI karsiligi).

Yon: KOD -> DOC. Tek kaynak Assets/Scripts/Core/AnalyticsEvents.cs'tir; plan
belgesi ondan turer. Iki yonlu esitlik aranir:
  (a) kodda tanimli her olay planin B4 tablosunda satir bulmali,
  (b) planin B4 tablosunda koddan gelmeyen olay adi bulunmamali.

P5 zorunlulugu ayrica sinanir: 'sessiz_toparlanma' her GDD'de bulunur (A2.5).

"VERI-YOK" sessizce gecmez (ilk-kosu.md §1): girdi dosyasi yoksa satir aranan
yolla birlikte raporlanir ve kapi KIRMIZI olur — parite olculemeden gecemez.

Cikis: 0 = parite tam; 1 = en az bir kirmizi.
"""
import argparse
import os
import re
import sys

KOD_YOLU = os.path.join("Assets", "Scripts", "Core", "AnalyticsEvents.cs")
DOC_YOLU = os.path.join("docs", "plan.md")
P5_OLAY = "sessiz_toparlanma"

# public const string AD = "deger";
SABIT = re.compile(r'public\s+const\s+string\s+\w+\s*=\s*"([a-z0-9_]+)"\s*;')
# B4 tablosunda olay adi tablonun ILK sutunudur: | `gun_basladi` | ... |
# Yalniz ilk sutun okunur; bolum icindeki diger ters tirnakli teknik adlar
# (dosya, alan, arac) pariteye karismaz — yanlis pozitif kapatildi.
TIRNAKLI = re.compile(r"^\|\s*`([a-z][a-z0-9_]*)`\s*\|", re.MULTILINE)


def oku(yol):
    try:
        with open(yol, encoding="utf-8-sig") as f:
            return f.read(), None
    except OSError as ex:
        return None, f"{type(ex).__name__}: {ex}"


def b4_bolumu(metin):
    """plan.md icinden yalniz B4 bolumunu keser — baska bolumdeki ters tirnakli
    teknik adlar (dosya, alan, arac) pariteye karismasin."""
    bas = re.search(r"^##+\s*B4\b.*$", metin, re.MULTILINE)
    if not bas:
        return None
    son = re.search(r"^##+\s+", metin[bas.end():], re.MULTILINE)
    return metin[bas.end():bas.end() + son.start()] if son else metin[bas.end():]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kok", default=".")
    a = ap.parse_args()

    kirmizi = 0
    kod_yolu = os.path.join(a.kok, KOD_YOLU)
    doc_yolu = os.path.join(a.kok, DOC_YOLU)

    kod_metin, hata = oku(kod_yolu)
    if kod_metin is None:
        print(f"KIRMIZI  olay sabitleri okunamadi ({hata})")
        print(f"         kanit: aranan {KOD_YOLU}")
        return 1

    doc_metin, hata = oku(doc_yolu)
    if doc_metin is None:
        print(f"KIRMIZI  plan belgesi okunamadi ({hata})")
        print(f"         kanit: aranan {DOC_YOLU}")
        return 1

    kod = set(SABIT.findall(kod_metin))
    if not kod:
        print("KIRMIZI  kodda hic olay sabiti bulunamadi")
        print(f"         kanit: {KOD_YOLU} icinde 'public const string ... = \"...\"' eslesmesi 0")
        return 1

    bolum = b4_bolumu(doc_metin)
    if bolum is None:
        print("KIRMIZI  planda B4 bolumu bulunamadi")
        print(f"         kanit: {DOC_YOLU} icinde '## B4' basligi yok")
        return 1

    doc = set(TIRNAKLI.findall(bolum))

    eksik_docta = sorted(kod - doc)
    fazla_docta = sorted(doc - kod)

    if eksik_docta:
        kirmizi += 1
        print(f"KIRMIZI  kodda var, planin B4'unde YOK: {', '.join(eksik_docta)}")
        print("         kanit: tek kaynak koddur; plan ondan turer")
    if fazla_docta:
        kirmizi += 1
        print(f"KIRMIZI  planin B4'unde var, kodda YOK: {', '.join(fazla_docta)}")
        print("         kanit: planda koddan gelmeyen olay adi bulunamaz")
    if P5_OLAY not in kod:
        kirmizi += 1
        print(f"KIRMIZI  P5 zorunlu olayi kodda yok: {P5_OLAY}")
        print("         kanit: A2.5 — her GDD'de bulunur ve pariteye dahildir")

    if kirmizi == 0:
        print(f"YESIL    {len(kod)} olay iki tarafta da tam; P5 satiri yerinde")
    print(f"kod={len(kod)} doc={len(doc)} kirmizi={kirmizi}")
    return 1 if kirmizi else 0


if __name__ == "__main__":
    sys.exit(main())
