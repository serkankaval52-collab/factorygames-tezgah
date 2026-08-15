# CLAUDE.md — oyun reposu executor kuralları

**Norm kaynağı:** [FactoryGames/docs/PIPELINE.md](https://github.com/serkankaval52-collab/FactoryGames/blob/arena/019fcd97-factorygames/docs/PIPELINE.md)
— çelişkide PIPELINE.md kazanır. Kod detayı:
[kod-standardi.md](https://github.com/serkankaval52-collab/FactoryGames/blob/arena/019fcd97-factorygames/docs/standards/kod-standardi.md).
Bu dosya ≤30 kuraldır (Sözleşme-3); yeni kural ancak mevcut biri teste/lint'e
çevrilerek girer.

**Okuma kapsamı:** PIPELINE.md + aktif aşama dosyası + gerekli standart. Başka dosya
açılmaz. Fabrika belgelerine **public linkten** bakılır — fabrika klonu bu repoda değildir.

1. Sen bu oyunun otonom executor'ısın; kanıt olmadan "bitti/yeşil" denmez: her iddia
   koşmuş komut + çıktı taşır.
2. **Sahne dosyası şablon varsayılanından sapamaz.** Hiyerarşi kodda kurulur
   (`[RuntimeInitializeOnLoadMethod(BeforeSceneLoad)]`); referans `scene-baseline.json`,
   bekçi `tools/lint/lint.py`.
3. Veri `StreamingAssets/*.json`'dadır. **ScriptableObject / `.asset` yok** (GUID'li YAML
   diff'i insan-okunamaz, CI yeniden üretemez).
4. Inspector'dan sahne referansı bağlamak YOK; `GameObject.Find` /
   `FindFirstObjectByType` / `Camera.main` **yasak** — bağlama kurulum anında açık atamayla.
5. Prefab yalnız varlık olarak ve yalnız `Assets/Prefabs/` altında (kod-standardi §10:
   idempotent Dump→Apply; elle YAML yok).
6. Motor ayarları `factory.core/templates` preset setinden **kopyadır**; elle ayar
   "kaynağı olmayan durum"dur ve `PRESET-SAPMA` kapısı onu kırmızı yakar.
7. Saf mantık Unity API'siz yazılır (`Assets/Scripts/Core/`) — CI'da Unity olmadan
   `dotnet test` ile koşar. Sahneye/UI'a yazan sınıf iş kuralı içermez.
8. Gevşek bağlılık C# `event`/`Action` ile; `UnityEvent` yasak.
9. `Update`'te allokasyon yok; `GetComponent*` cache'lenir; runtime reflection yasak.
10. `Debug.Log*` yalnız `#if UNITY_EDITOR || DEVELOPMENT_BUILD`.
11. Uyarı yok sayılmaz: giderilir veya `#pragma` + gerekçeyle bastırılır.
12. Kullanıcıya görünen metin **koda gömülmez** (yerelleştirmede yaşar) — `DIL-KAPISI`
    lint'i bunu denetler (A3.6).
13. Ham Pos X/Y tek cihazdan yazılmaz: güvenli alan + en-boy matrisinden türetilir
    (`RuntimeInitBootstrap.SafeAreaNormalized`).
14. Depoya **sır girmez**; kanıt "secret VAR" satırıdır, içeriği asla loglanmaz.
15. Kanıt/doküman düzlemine ham artefakt (görüntü, log dökümü, dışa aktarım) girmez —
    `Assets/` altındaki oyun varlıkları bunun dışındadır ve G1–G2 kapılarına tabidir.
16. Sayılar `docs/appendix/C.md`'den gelir (yerel kopya `tools/lint/esikler.json`);
    **Ek C'de olmayan sayı hiçbir kapıda kullanılamaz**.
17. Kültür-bağımsızlık zorunlu: sayı/tarih ayrıştıran her yerde `InvariantCulture`
    (saha bulgusu: tr-TR ondalık ayıracı ölçüm alanlarına sızıyordu).
18. **CI runner'ında Unity koşmaz** (C+ ilkesi): Unity gerektiren kanıt yerelde
    üretilir, metin olarak depoya girer. CI'da lint + saf-C# test + iOS `xcodebuild`.
19. Unity batchmode öncesi `Temp/UnityLockfile` yokluğu kanıtlanır; **kalıntı ayrımı**
    yapılır (süreç yok + dosya exclusive açılabiliyor ⇒ kalıntı, silinebilir).
20. Editor GUI'sinde elle iş yok; MCP yalnız gözlemci ve yalnız **resmî** Unity MCP
    köprüsü kullanılır — üçüncü taraf köprülere bağlanılmaz.
21. Kök neden > yama: belirti (a) zamanlama/sıra, (b) durum makinesi varsayımı,
    (c) referans yaşam döngüsü kategorilerine indirilir; indirilemiyorsa yama yazılmaz,
    önce gözlem eklenir.
22. En küçük güvenli adım: tek seferde tek değişken; geri dönüşü zor iş onaydan önce
    uygulanmaz.
23. Sessiz varsayım yok: varsayım ya test edilir ya yazılı sorulur.
24. Kapı reddi/post-mortem bulgusu → önce lint/test (önce-kırmızı kanıtlı), sonra
    kontrol listesi satırı, en son çare kural.
25. "Veri yok" **geçti sayılmaz**: kapı atlanırsa artefakt kanıtıyla (yol + sayı)
    raporlanır.
26. Hiçbir metrik beyana dayanmaz: damga, dosya, CI çıktısı (Sözleşme-10).
27. İnsan kapısı TEK cümledir: hangi pencere, hangi buton, hangi hesap.
28. BAŞARISIZ'da hat DURUR; karar insanındır. Sessiz geçiş ve kural esnetme yok.
29. Oyunlar arası çapraz tanıtım her koşulda yasaktır.
30. Kullanıcının diğer projelerine ve mevcut oyununa erişilmez.
