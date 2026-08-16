# Tezgâh — Aşama 2 plan belgesi (GDD)

**Oyun:** Tezgâh (FactoryGames 0B pilot, kart A) · **Aile:** `duz-geometrik` · **Yön:** NET-SOKAK
**Kart kaynağı:** FactoryGames `docs/factory/kavram/2026-08/secim.md` + `kartlar.md` (KART A)
**Sanat paketi:** FactoryGames `docs/standards/sanat-yonu/duz-geometrik.md` (v1.4.9) — hex ve
G5 üçlüsü oradan **birebir alıntıdır**, burada yeniden karar verilmez.
**Motor:** Unity 6000.3.16f1 (changeset `a56f230f6470`), URP + 2D Renderer.
**Çekirdek:** `com.factorygames.core` `#v0.1.8` (UPM, git `#tag`).

> **SIM-BEKLIYOR damgası (tek desen).** B3'ün her sayısı `tools/denge_sim.py`
> çıktısından gelir (B8). Araç bu koşuda **henüz teslim edilmedi** (mimar beyanı;
> v1.4.10'da gelecek). O güne kadar her sayısal hücre şu tek deseni taşır:
> **`SIM-BEKLIYOR | gerekçe: <neden bu banda inanıyoruz> | beklenen aralık: <alt>–<üst>`**
> Bu bir TBD **değildir**: kaynağı bilinen, ölçüm aracı belli, bandı gerekçeli bir
> boşluktur. Aşama 2 kapanış kapısı (TBD=0) sim işlenene kadar **beklemededir**;
> bu belgenin geri kalanı beklemez.

---

## B0 — Kanıtla başlama

GDD konseptle değil kanıtla açılır: ilk bölüm **B8'in simülasyon çıktı tablosudur**
ve B3'ün sayıları buradan alıntılanır.

**Simülasyon:** `denge_sim v1.4.12`, model `tezgah-v1`, `tohum=42`, `seeds=200`.
Rapor: [`docs/verification/02-denge-sim.json`](verification/02-denge-sim.json).

| ne ölçüldü | sonuç (orta · p10 / p50 / p90) | tasarıma etkisi / hangi kilitli karar |
|---|---|---|
| Gün başarısızlık oranı | **0,5004** · 0,3636 / 0,50 / 0,60 | hedef bandın (%35–60) tam ortası; tahsis kararı her gün ısırıyor — **B3'ün merkez sayısı buradan geldi** |
| Oturum süresi | **492,0 sn** (8,2 dk) · 450 / 500 / 500 | hedef 6–10 dk bandında; `sezon_gun_sayisi` bu ölçümle 12'ye sabitlendi |
| Oynanan gün | **9,84** · 9 / 10 / 10 | agresif oyuncu sezonu ~10. günde tüketiyor |
| Tamamlanma oranı | **0,000** · 0 / 0 / 0 | **kilitli kararı doğruladı:** simülasyondaki "hep sat" oyuncusu sezonu ASLA bitiremiyor. Sezonu bitirmek (kart A: "kalan stokla bitirmek skor getirir") ancak **tahsis yaparak** mümkün — yani oyunun vaadi matematiksel olarak gerçek |
| Toplam satış | **150,0** · 150 / 150 / 150 | stok her koşuda tamamen tükeniyor; "kaynak azalır, yenilenmez" ekseni sayıyla doğrulandı |
| Tohum kararlılığı | tohum 7: başarısızlık 0,5088 · oturum 491,5 sn | **yön değişmedi** — iki tohumda da her iki hedef bandın içinde (fark 0,0084 ve −0,5 sn) |
| Determinizm | aynı config + aynı tohum → aynı JSON (sha256 eşit) | rapor yeniden üretilebilir; beyan değil artefakt |

**Sabitle oynamaya kalkan uygulayıcı ilk okuduğu şeyde neden değiştiremeyeceğini görür:**
palet kilitli (sanat paketi), preset kilitli (kanonik hash), **sayılar sim'e bağlı** —
sabit değişirse `denge_sim` yeniden koşar (B8 değişim kontrolü).

### Ayrıca ölçülmüş olanlar (görsel/iskelet düzlemi)

| ne ölçüldü | sonuç | tasarıma etkisi |
|---|---|---|
| Palet G6 sinyal ayrımı (ΔE00, 4 görüş) | 56,51 / 48,47 / 62,26 / 48,72 ≥ 2,0 | `tehlike`↔`vurgu` renk ayrımı güvenli; biçim eşliği yine de zorunlu tutuldu |
| Palet G6 oran ayağı, `tehlike`/`arka_plan` | ölçüm kırmızı verdi (2,88 < 3,0), **eşik değişmedi — renk değişti** | **kilitli karar geri alındı:** `tehlike` `#B4341F` → `#A82E1A` (mimar kararı v1.4.10). Yeni ölçüm 5,39 / 4,03 / **3,29** / 5,71; biçim eşliği oranın yerine geçmez, üstüne çıkar |
| Türev tonlar (paket Bölüm 3 çarpanları), `tehlike`/`arka_plan` | ×0,86 → 4,26 · ×0,72 → 5,58 · ×0,60 → 7,07 (en dar değerler) | türevler koyulaştıkça pay artıyor; G6 tavanı **ana rolde** (3,29), türevlerde değil |
| Kanonik preset sapması (Unity açılışı öncesi/sonrası) | 39/39 dosya birebir, iki ölçümde de yeşil | pinli sürümde ilk açılış yükseltmesi **olmuyor**; iskelet bu preset üstünde büyür |
| Sahne baseline | `SampleScene.unity` 2 nesne ≤ 2 | sahne şablon varsayılanında kalıyor; hiyerarşi kodda kuruluyor (kural 7/8) |

Sabitle oynamaya kalkan uygulayıcı ilk okuduğu şeyde neden değiştiremeyeceğini görür:
**palet kilitli** (sanat paketi), **preset kilitli** (kanonik hash), **sayılar sim'e bağlı**.

## B1 — FTUE (ilk 60 saniye)

Metin diyeti (A3.6): kullanıcıya görünen metin ekran başına asgari; sayı ve ikon tercih
edilir. İlk sürüm dilleri Ek C `ilk_surum_diller` = **en, tr**.

| # | adım | süre | metinsiz anlaşılır mı | not |
|---|---|---|---|---|
| 1 | Sezon stoğu tezgâhın yanına yığın olarak düşer, sayaç dolar | 0–5 sn | evet | sayı + yığın hacmi; kısıt daha ilk karede görünür |
| 2 | Tek boş raf yanıp söner, stok kübü sürüklenebilir | 5–12 sn | evet | tek serbestlik derecesi; başka etkileşim kapalı |
| 3 | İlk müşteri gelir, raftaki ürünü alır, sayaç düşer | 12–22 sn | evet | girdi-çıktı ilişkisi tek harekette görünür |
| 4 | İkinci müşteri gelir ama raf boş — geri çevrilir | 22–32 sn | evet | ilk **kayıp** deneyimi; ret öğretilir, anlatılmaz |
| 5 | Gün biter, gün-sonu kartı: satılan / kalan stok | 32–45 sn | evet | iki sayı, üçüncü yok |
| 6 | İkinci gün başlar; artık iki raf açık, seçim gerçek | 45–60 sn | evet | ilk gerçek tahsis kararı |

**Okuma gerektiren adım yok.** Gerekçe (E2): her adım tek serbestlik derecesi açıyor ve
sonucu aynı karede gösteriyor; öğretici metin yerine kısıtlı etkileşim kullanılıyor.

## B2 — Ekran listesi + wireframe + durum sütunu

Zorunlu ekranlar (5 MVP ekranı + zorunlu alt yüzeyler):

| ekran | tek-kutu wireframe | geçiş |
|---|---|---|
| **Oyun sahnesi** | üst: gün sayacı + kalan stok · orta: izometrik tezgâh + raflar · alt: sürüklenebilir stok şeridi | → gün-sonu (30 sn dolunca) · → duraklat |
| **Gün sonu** | başlık + iki sayı (satılan / kalan) + tek birincil düğme | → oyun sahnesi (ertesi gün) · → sezon haritası (sezon bitti) |
| **Sezon haritası** | gün düğümleri şeridi + puanla açılan raf yeri / tabela | → oyun sahnesi |
| **Ana menü** | oyun adı + tek başlat düğmesi + ayarlar ikonu | → oyun sahnesi · → ayarlar |
| **Ayarlar** | ses anahtarı, müzik anahtarı, dil, **gizlilik politikası bağlantısı** | → geri |
| **Duraklat** (üst katman) | devam / ana menü + ses anahtarları | → oyun sahnesi |
| **Oyun sonu (sezon finali)** | kalan stok skoru + tekrar dene | → ana menü |

**Durum sütunu (P4 kapısı — A2.6):** her ekranda tanımlıdır ve
`Assets/StreamingAssets/premium-manifest.json` `durumlar` alanında sayılabilir hâlde durur.

| durum | ekranda ne görünür |
|---|---|
| `yukleme` | tezgâh silueti + belirsiz ilerleme; sayaçlar boş değil **gizli** |
| `izin_isteme` | sistem penceresi açıkken arkada sahne **donuk ve etkileşimsiz**; kısmi görünen sayaç yok |
| `ag_hatasi` | yalnız ödüllü tabela akışında; teklif düğmesi pasifleşir, oyun döngüsü **kesilmez** |
| `bos_icerik` | sezon haritasında henüz açılmamış düğüm: boş çerçeve + kilit ikonu |
| `hata` | tek satır hata yüzeyi + geri dönüş; oyun durumu son gün sonuna geri sarılır |

**Kayıt dayanıklılığı beyanı (E7):** ilerleme **yalnız yerel**; bulut kaydı yok. Sezon
durumu her gün sonunda yazılır; uygulama öldürülürse son tamamlanan gün geri yüklenir.
**Renk-yalnız-bilgi beyanı (G6):** `tehlike` daima **üçgen**, `vurgu` daima **yatay tente**
biçimiyle gelir; renk hiçbir yerde tek başına bilgi taşımaz (sanat paketi "sabitlenen
dizginlemeler" satırından alıntı).

## B3 — Matematik modeli

**TBD yok, SIM-BEKLIYOR yok.** Her sayı ya simülasyon çıktısıdır ya gerekçeli
"simüle edilemez" satırıdır (B8 kaynak denetimi). Sim kaynağının kısaltması:

> **[SIM]** = `denge_sim v1.4.12`, `docs/verification/02-denge-sim.json`, `tohum=42`, `seeds=200`

Sim **girdisi** olan altı değer `Assets/StreamingAssets/config.json`'da kök seviyede
yaşar — sim ile oyun **aynı dosyayı** okur, ikinci bir kopya yoktur.

| # | büyüklük | değer | kaynak |
|---|---|---|---|
| 1 | Tur (gün) süresi | **30 sn** | kart A kura ekseni — **sabit**, sim'e tabi değil (`kura.json`) |
| 2 | Sezon uzunluğu | **12 gün** | **[SIM]** girdi · oturum 492 sn ile 6–10 dk bandına oturdu |
| 3 | Başlangıç sezon stoğu | **150 adet** | **[SIM]** girdi · toplam satış 150,0 → stok her koşuda tükeniyor |
| 4 | Gün başına taban talep | **10 müşteri** | **[SIM]** girdi |
| 5 | Talep artış eğrisi | **gün başına %10** (üstel: `taban × 1,10^(g-1)`) | **[SIM]** girdi · model `tezgah-v1` üstel seçti |
| 6 | Raf kapasitesi | **3 raf** (raf başı 6 adet/gün → günlük tavan 18) | **[SIM]** girdi · raf başı kapasite motor sabiti |
| 7 | Tabela çarpanı (K3 ödülü) | **×1,5** | **[SIM]** girdi · beklenen ×1,3–×1,8 bandının ortası |
| 8 | Gün başarısızlık oranı (geri çevrilen ≥1) | **%50,0** (p10 %36,4 · p50 %50 · p90 %60) | **[SIM]** çıktı · hedef %35–60 bandının ortası |
| 9 | Oturum uzunluğu | **492 sn ≈ 8,2 dk** (p10 450 · p90 500) | **[SIM]** çıktı · hedef 6–10 dk |
| 10 | Ekonomi: stok giriş–çıkış | Giriş **tek seferlik** (sezon başı), sonrasında giriş **yok**. Çıkış = karşılanan müşteri. | **kilitli tasarım kararı** — sim değiştiremez; kart A'nın kısıt ruhu. Sim bunu doğruladı: tamamlanma oranı 0,000 |
| 11 | Oturum/gün hedefi | **1,5–3 oturum** | **simüle edilemez, gerekçe:** oyuncunun geri-dönüş davranışıdır; ekonomi motorunun konusu değil. **Kanıt yolu:** Aşama 8–9 telemetri ölçümü — `oturum_basladi` / `sezon_basladi` olayları B4 paritesinin zaten parçası |
| 12 | Doğal reklam anı yoğunluğu | **oturum başına 2–4 an** | **ölçüm değil karar** (B5): tek yerleşim = gün-sonu kartı, `menu-sonu-tek-dugme` matrisi + `secim.md` K3. Ek C `reklam_siklik_tavan`=3 tavanını aşamaz |

**Not (2 ↔ 9 çapraz tutarlılığı):** sezon 12 gün, ama sim'in "hep sat" oyuncusu
ortalama **9,84** günde stoğu tüketiyor. İkisi çelişmez: 12 **üst sınırdır** ve
tahsis yapan oyuncunun ulaşabileceği hedeftir; agresif oyuncu göremez. Sezon
uzunluğunu 12'nin üstüne çıkarmak hedefi ulaşılamaz kılardı (tarama: 12–20 arası
tüm değerler aynı metrikleri veriyor, çünkü sezon zaten dolmadan bitiyor).

## B4 — Analitik olay haritası

**Tek kaynak:** `Assets/Scripts/Core/AnalyticsEvents.cs`. Bu tablo ondan türer; CI'daki
`events-parity` işi iki yönlü eşitliği zorlar (kod→doc). Yeni olay önce koda, sonra buraya.

| olay | hangi B3 iddiasını ölçer |
|---|---|
| `oturum_basladi` | oturum/gün hedefi |
| `sezon_basladi` | sezon başına oyuncu sayısı (tekrar oynanabilirlik) |
| `sezon_bitti` | sezon uzunluğu; hipotezin 3. tura ulaşma ölçümünün paydası |
| `gun_basladi` | gün sayısı dağılımı; talep artış eğrisinin gerçek karşılığı |
| `gun_bitti` | hedef oturum uzunluğu; gün başına süre sapması |
| `urun_rafa_yerlestirildi` | raf kapasitesi kullanımı; tahsis kararının hacmi |
| `urun_one_cikarildi` | öne çıkarma kararının kullanım oranı |
| `musteri_karsilandi` | gün başına taban talep; ekonomi çıkış tarafı |
| `musteri_geri_cevrildi` | hedef başarısızlık oranı — B3'ün merkez sayısı |
| `stok_tukendi` | başlangıç sezon stoğu kalibrasyonu |
| `tabela_teklif_edildi` | doğal reklam anı yoğunluğu (teklif tarafı) |
| `tabela_kullanildi` | tabela çarpanı; K3 takasının gerçek çekiciliği |
| `sessiz_toparlanma` | **P5 zorunlu satırı** — oyuncudan gizlenen hata bizden gizlenmez |

## B5 — Reklam planı

**K1 = 13+ (genel kitle),** Families/Kids kapsamı **değil**. Stil ailesi (`duz-geometrik`,
serin-nötr palet) bu beyanla tutarlıdır — çocuk-hedefli görsel dil yok.

| yerleşim | tür | tetikleyici | sıklık sınırı |
|---|---|---|---|
| Gün-sonu kartı | ödüllü video (opt-in, tek düğme) | yalnız gün-sonu kartı açıkken; oyuncu basarsa | Ek C `reklam_siklik_tavan` = **3**/oturum; `reklam_arasi_min_sn` = **90 sn** |

- **İlk gün reklam YOK** (kart A K1 beyanı) — ilk oturumda teklif hiç gösterilmez.
- **Geçiş reklamı (interstitial) YOK**, banner YOK. Tek biçim ödüllü videodur.
- **K3 takası:** 1 izleme = **1 turluk** müşteri-çekim tabelası. **STOK VERİLMEZ** —
  ödül kısıt ruhunu delmez, yalnız o günün talebini çarpar.
- Yerleşim matrisi tohumu: `menu-sonu-tek-dugme` (kart A).

## B6 — Ses listesi + boyut bütçesi

| ses | biçim | süre tavanı |
|---|---|---|
| Ürün rafa oturdu (çekirdek geri bildirim) | OGG Vorbis | Ek C `ses_sfx_sure_tavan_sn` = 2 sn |
| Müşteri karşılandı | OGG Vorbis | ≤ 2 sn |
| Müşteri geri çevrildi | OGG Vorbis | ≤ 2 sn |
| Gün sonu (kazanç sayacı) | OGG Vorbis | ≤ 2 sn |
| Sezon finali | OGG Vorbis | ≤ 2 sn |
| UI dokunuşu | OGG Vorbis | ≤ 2 sn |
| Fon müziği (tek döngü) | OGG Vorbis | — |

Seviye hedefleri Ek C'den: `ses_lufs_band` **[-17, -15] LUFS**, `ses_tepe_dbtp` **-1 dBTP**.
**Toplam ses MB tavanı: 6 MB.** Kaynak: **bütçe kararı — üst sınır**; ölçüm değil.
Ölçülmüş karşılığı Aşama 6'da artefaktla gelir (S1 kapısı: FFmpeg `ebur128` çıktısı
manifest satırına yazılır). Gerekçe: uygulama boyut tavanı Ek C'de henüz yok (form
bekliyor); tavan gelince ses payı ondan **türetilir** ve bu sayı aşağı revize edilebilir.
Ölçülen APK gövdesi şu an 29,16 MB — 6 MB'lık ses payı bu gövdenin %20'sinin altındadır.
**Sessizde oynama notu (F5):** kritik geri bildirimlerin hiçbiri yalnız sese bağlanmaz —
her biri `premium-manifest.json` `eylemler` listesinde görsel karşılığıyla eşleşir.

## B7 — Cihaz / çözünürlük matrisi

Sayısal içerik Ek C'den (A3.7): en-boy aralığı **1,78 – 2,33**; asgari test hücresi
**3**; asgari dokunma hedefi **9 mm**. Hedef kare hızı: Ek C `premium_kare_hizi_secenek`
**[30, 60]** → bu oyun **60**'ı hedefler (düz renk, gradyan yok; P6 bütçesi buna göre).

| hücre | en-boy | not |
|---|---|---|
| dar telefon | 2,33 | en dar güvenli alan; gün-sonu kartı burada taşmadan çizilmeli |
| standart telefon | 2,00 | referans yerleşim |
| geniş / tablet | 1,78 | izometrik sahne genişler, UI kenara yapışmaz |

Her ekran üç hücrede de taşmadan çizilir; kanıt Aşama 7 red-flag R9'da verilir.
Ham Pos X/Y tek cihazdan yazılmaz — güvenli alan + en-boy matrisi formülü (kod-standardi §3).

## B8 — Denge doğrulayıcısı

**Araç:** `denge_sim.py` **v1.4.12**, model `tezgah-v1`. Araç **fabrikada durur**
(FactoryGames `tools/`), oyun reposuna kopyalanmaz — tek kaynak orasıdır.

Yapı dört şartı da karşılıyor:

| şart | karşılığı |
|---|---|
| (i) ürünü etkileyen sabitler tek yerde, en üstte | `MODEL`, `TUR_SANIYE=30`, `ARA_SANIYE=20`, `VARSAYILAN{tabela_p, jitter}` dosyanın başında |
| (ii) çekirdek kuralı modelleyen minimal fonksiyon | `kostur()` — `satis = min(talep, stok, raf × raf_basi)`; `TezgahRules.Karsilanan` ile **aynı biçim** |
| (iii) ≥3 alternatif değerin yan-yana karşılaştırması | **4 500 kombinasyon** tarandı; 734'ü her iki hedef bandına oturdu; seçilen aday band **merkezine** en yakın olandır (uçlarda değil) |
| (iv) açık eşikli PASS/FAIL + GDD'ye atıf | eşikler: başarısızlık %35–60, oturum 360–600 sn. Seçilen config **ikisinde de PASS**; rapor `docs/verification/02-denge-sim.json`, bu belgeden B3 ile atıflı |

**Yeniden üretilebilirlik:** aynı config + aynı tohum → **aynı JSON** (sha256 eşitliğiyle
doğrulandı). Kararlılık: tohum 7 ile yön değişmedi (başarısızlık 0,5088 · oturum 491,5 sn
— ikisi de bandda).

**VERİ-YOK sessiz geçmez:** araç, config'te null hücre bulursa `exit 2` + eksik alan
listesi verir. Bu koşuda çıkış **0**.

**Değişim kontrolü:** sabit değişirse sim yeniden koşar; sayının hangi bantta kalması
gerektiği B3'te yazılıdır; kapı Aşama 7 CI listesinde ve Aşama 9 gönderim öncesinde
tekrar koşar.

---

## MVP kapsamı

**5 ekran:** oyun sahnesi · gün sonu · sezon haritası · ana menü · ayarlar
(+ duraklat ve oyun-sonu alt yüzeyleri, B2'de tanımlı).
**Kapsam dışı (MVP değil):** bulut kaydı, sosyal özellik, günlük görev, mağaza,
birden çok sezon tipi, çoklu tezgâh türü.

## İş kalemleri (ölçülebilir kabul kriteriyle)

| # | iş | kabul kriteri (ölçüm) |
|---|---|---|
| 1 | `denge_sim.py` entegrasyonu + B3 doldurma | B3'te SIM-BEKLIYOR hücresi **0**; her sayı sim çıktısına atıflı |
| 2 | Çekirdek döngü (30 sn gün, talep dalgası, stok düşümü) | EditMode + `dotnet test` yeşil; `TezgahRules` dalları **%100** kapsanır |
| 3 | Tahsis etkileşimi (sürükle-bırak raf) | 3 en-boy hücresinde dokunma hedefi ≥ **9 mm**; taşma yok |
| 4 | Gün-sonu kartı + sezon haritası | iki ekran da 3 hücrede taşmadan çizilir; geçiş süresi Ek C `premium_gecis_sure_band` **[150, 400] ms** içinde |
| 5 | Palet + varlık üretimi (Aşama 4 girdisi) | `lint_varlik.py` G1/G2/G4/G6/G7/G8 **kırmızı 0**; `asset-manifest.json` `varliklar[]` dolu |
| 6 | Analitik bağlama | `events-parity` yeşil; 13 olayın hepsi gerçek gönderimle eşleşir |
| 7 | Ödüllü video (AppLovin MAX) | ilk oturumda teklif **0** gösterim; sıklık ≤ 3 ve aralar ≥ 90 sn (telemetri ile) |
| 8 | Yerelleştirme (en + tr) | DIL-KAPISI yeşil: runtime kodunda kullanıcı metni **0** |
| 9 | Ses seti + bütçe | S1 kapısı yeşil (LUFS bandı, tepe, süre); toplam MB tavan içinde |
| 10 | Kayıt dayanıklılığı | uygulama öldürüldüğünde son tamamlanan gün geri yüklenir; 10/10 deneme |

## Araç / SDK listesi (Aşama 3 girdisi)

| ihtiyaç | seçim | not |
|---|---|---|
| Reklam | **AppLovin MAX** — tek ağ, tek aggregation | başka ağ eklenmez; K1 13+ ile uyumlu |
| Analitik | **kendi şemamız** | FactoryGames `docs/factory/standartlar/04-telemetri-semasi.md` (TASLAK) referans; 3. taraf analitik SDK'sı **yok** |
| Ses aracı | **harici ses aracı YOK** | ses varlıkları Aşama 4'te üretilir; ölçüm FFmpeg `ebur128` ile (araç, SDK değil) |
| Çekirdek | `com.factorygames.core` `#v0.1.8` | UPM git `#tag` |
| Yerelleştirme | Unity yerleşik + JSON tablo | ScriptableObject yasak (kural 9) → `StreamingAssets` JSON |

## Varlık listesi + T1 aile/transform manifesti

**Manifest:** `Assets/StreamingAssets/asset-manifest.json`. G5 üçlüsü sanat paketinden
**birebir alıntı** (`stil` alanı):

| alan | değer |
|---|---|
| `perspektif` | `izometrik 2:1` |
| `cizgi_kalinligi_bandi` | `0 px (konturusuz)` — **STRING**; sayısal `0` JSON'da falsy'dir ve G5 kapısını kırmızı yakar |
| `golge_yonu` | `sag-ust` (basamak detayı paket Bölüm 3'te kalır) |

Varlık listesi (Aşama 4'te üretilecek; `varliklar[]` şu an **boş** ve bu bilinçlidir):
tezgâh gövdesi · tente + direk · stok kübü · raf hücresi · müşteri silueti · yol şeridi ·
uyarı üçgeni · gün-sonu kartı çerçevesi · birincil düğme · sezon düğümü · tabela.

## Palet — `StreamingAssets/palette.json`

8 rol sanat paketi Bölüm 1'den birebir; **ek rol `ui_zemin` = `#E8E4DA`**. Eşleşme notu:
paket Bölüm 1'de `ui_zemin` ayrı satır değildir — kart zemini `arka_plan` ile aynı tondur
ve paketin G6 ölçümleri bu eşleşmeyle koşuldu. G1 zorunlu rol listesi `ui_zemin` istediği
için burada açık satır olarak yazılır: **sapma değil, aynı değerin adlandırılmasıdır.**

## Pre-mortem — "bu oyun nasıl batar" (10 madde)

Taksonomi: FactoryGames `docs/factory/standartlar/05-pre-mortem-taksonomisi.md`.

| # | kök | senaryo | erken sinyal | yakalayan kapı | durum |
|---|---|---|---|---|---|
| 1 | T2 | Sezon stoğu yanlış kalibre; oyun 3. günden önce bitiyor veya hiç ısırmıyor | `stok_tukendi` gün dağılımı tek tepe | B8 `denge_sim.py` | **açık** — sim beklemede |
| 2 | T1 | Tahsis kararı hissedilmiyor; oyuncu rafı doldurup bekliyor | `musteri_geri_cevrildi` oranı ≈ 0 | Aşama 8 rubriği eksen 1–2 | **açık** — B3 hedef aralığı (%35–60) önlem |
| 3 | T3 | Ödüllü tabela kısıt ruhunu deliyor; oyuncu ödülle stok kazandığını sanıyor | `tabela_kullanildi` sonrası stok beklentisi şikâyeti | R1/R4 (red-flag) | **kapatıldı** — K3 "STOK VERİLMEZ" B5'te ve `TezgahRules.TabelaliTalep` imzasında (stok parametresi **yok**) |
| 4 | T4 | İzometrik derinlik sıralaması bozuluyor; kübler yanlış sırada çiziliyor | sprite z-fighting, tente gövdenin altında | CI PlayMode + kod-standardi §9 | **açık** — Aşama 4 iş kalemi 5 |
| 5 | T6 | B3 sayıları sim yerine "makul görünen" tahminle doluyor | GDD'de gerekçesiz sayı | B8 kaynak denetimi (gerekçesiz tahmin = kırmızı) | **kapatıldı** — 12 hücrenin 9'u `denge_sim` çıktısı/girdisi, 1'i kilitli karar, 1'i gerekçeli "simüle edilemez", 1'i B5 kararı; gerekçesiz sayı **0** |
| 6 | T5 | `factory.core` etiketi veya Unity pini kayıyor; iskelet yeniden kurulamıyor | PRESET-SAPMA kırmızı, paket çözümlenmiyor | CI lint + `standartlar/FALLBACK.md` | **kapatıldı** — `#v0.1.8` pinli, preset 39/39 birebir ölçüldü |
| 7 | T3 | İlk gün reklam yasağı kodda değil yalnız planda kalıyor | ilk oturumda teklif gösterimi > 0 | R1 + iş kalemi 7 kabul kriteri | **açık** — Aşama 4'te telemetriyle doğrulanacak |
| 8 | T8 | Ek C form dönüşü gecikiyor; BOYUT ve ses bütçesi ölçülemiyor | BOYUT kapısı VERİ-YOK kalıyor | `insan-yuku.md` + Ek C `insan_yanit_tavan_*` | **kabul edilmiş risk** — gerekçe: kapı RAPOR modunda ölçüp kaydediyor, kırmıyor; kural 28 gereği uydurma eşik yazılamaz |
| 9 | T6 | Renk-yalnız-bilgi ihlali; `tehlike` yalnız renkle anlatılıyor | G6 kırmızı veya CVD şikâyeti | `lint_varlik.py` G6 | **kapatıldı** — kapı gerçekten kırmızı yandı (döteranopi 2,88), renk `#A82E1A`'ya koyulaştı → 3,29. Eşik gevşetilmedi; biçim eşliği oranın **üstüne** ek önlem |
| 10 | T7 | İkinci oyun aynı aileyi kullanınca görsel tekrar hissi | defter ekseni farkı yetersiz | `appendix/A.md` + R6 | **kabul edilmiş risk** — gerekçe: Ek A aile başına ≤2 canlı oyuna zaten izin veriyor; paket yeniden kullanımı maliyet kararıdır, ikinci oyunda eksen farkı kart düzeyinde aranacak |

**Tekrar taraması (zorunlu yazılı sonuç):** **önceki kayıt yok — bu defterin ilk
pre-mortem'idir.** Taranan küme: FactoryGames `docs/factory/` altında önceki koşu
pre-mortem dosyası **0 adet**. Bu VERİ-YOK'tur, "tarandı, bulgu yok" değildir
(`ilk-kosu.md` §2). Üç koşuda üst üste kabul edilen aynı etiket otomatik Sözleşme-5
yükseltmesine gider; sayaç bu koşuyla **1**'den başlar (kabul edilenler: T8, T7).

## DoD — "bitmiş" tanımı

| ölçüt | ölçüm |
|---|---|
| Kapılar | `lint.py` + `lint_varlik.py` + `events_parity.py` **kırmızı 0**; VERİ-YOK satırları artefakt kanıtlı |
| Testler | `dotnet test` yeşil; Unity EditMode + PlayMode yerelde yeşil |
| B3 | SIM-BEKLIYOR hücresi **0**, her sayı `denge_sim.py` çıktısına veya gerekçeli "simüle edilemez" satırına atıflı |
| B1–B8 | eksiksiz ve çapraz tutarlı; TBD **0** |
| Çözünürlük | 3 matris hücresinde 7 ekranın hepsi taşmadan çizilir |
| Yerelleştirme | en + tr tam; runtime kodunda kullanıcı metni 0 |
| Yapı | Android arm64 APK + iOS xcodeproj yerelde üretilir; iOS derleme kanıtı CI'da yeşil |
| Boyut | Ek C `uygulama_boyut_tavan_mb` gelince BOYUT kapısı yeşil; gelene kadar ölçülür ve kaydedilir |

## Kapı durumu

| # | madde | durum |
|---|---|---|
| 1 | ~~B8 / `denge_sim.py` teslim edilmedi~~ | **KAPANDI (v1.4.12).** Araç fabrikada; B3'te SIM-BEKLIYOR hücresi **0**. 4 500 kombinasyon tarandı, seçilen config iki hedef bandında da PASS, iki tohumda kararlı, çıktı deterministik |
| 2 | ~~G6 döteranopi oranı kırmızı~~ | **KAPANDI (v1.4.10).** `tehlike` `#B4341F` → `#A82E1A`; eşik değişmedi, renk koyulaştırıldı: 2,88 → **3,29**. Türevler (×0,86 / ×0,72 / ×0,60) da geçiyor |
| 3 | ~~PRESET-SAPMA (platform sonrası)~~ | **KAPANDI (v1.4.10 madde 2-i).** Baseline "platform-sonrası ilk durum"a taşındı; kapsam daraltılmadı (39/39), meşru alanlar + şema-tamamlama diff'i `docs/verification/01-preset-baseline.md`'de damgalı |
| 4 | **Ek C `uygulama_boyut_tavan_mb` yok** | **AÇIK — kabul edilmiş risk.** BOYUT kapısı RAPOR modunda: ölçer (APK 29,16 MB), kaydeder, **kırmaz** (kural 28: Ek C'de olmayan sayı kapıda kullanılamaz). Form dönünce kapı yeşile bağlanır |

Madde 4 Aşama 2'yi bloke etmez: kural 28 gereği uydurma eşik yazılamaz ve kapı
sessizce geçmiyor — ölçümü artefaktıyla raporluyor.

## MCP / AI paket kararı (kayıt)

`com.unity.ai.assistant` bu projeye **kalıcı olarak eklenmez** (mimar kararı v1.4.12).
Bilinçli sınama koşuldu ve köprünün **tetiklendiği kanıtlandı** (EditorPrefs'e
`Unity.AI.MCP.ProjectSettings` yazıldı; `Unity.AI.MCP.Runtime.dll` + `Unity.AI.MCP.Editor.dll`
derlendi). Gerekçe: 0A-9'un "projeye gereksiz AI yüzeyi taşınmaz" kararı + sınamada
görülen duplicate-assembly riski (`System.Runtime.CompilerServices.Unsafe.dll`).
Sınama sonrası paket geri çıkarıldı; `Packages/manifest.json` net değişiklik **sıfır**.
**Kural 30 uyumu:** hiçbir üçüncü taraf köprüye bağlanılmadı; sınama log'unda
`MCPForUnity` / `McpUnity` eşleşmesi **0**. Ayrıntı: `docs/verification/03-mcp-sinama.md`.
