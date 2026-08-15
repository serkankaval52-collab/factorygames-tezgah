# 0B / Aşama 2 — preset baseline taşıma (platform sonrası ilk durum)

**Damga (ham):** `1786828441403` · **İnsan-okur (UTC):** `2026-08-15T21:14:01Z`
**Dal@HEAD:** `feat/0b-asama2-iskelet@bb8d36a` · **Yapan:** executor (mimar kararı v1.4.10, madde 2-i)
**Unity pini:** `6000.3.16f1` (`a56f230f6470`) · **Çekirdek:** `com.factorygames.core#v0.1.8`

## Neden taşındı

Kanonik preset (factory.core `templates~/`) **ilk açılışı** çözüyordu ve bu ölçüldü:

| ölçüm anı | PRESET-SAPMA |
|---|---|
| scaffold sonrası, Unity açılmadan **önce** | **YEŞİL** — 39/39 dosya birebir |
| headless ilk açılıştan **sonra** | **YEŞİL** — 39/39 dosya birebir |
| Android platform ayarları + build **sonrası** | **KIRMIZI** — 5 dosya saptı |

Yani "pinli sürümde ilk açılış yükseltmesine izin yok" şartı sağlanmıştı; sapmayı
üreten şey **platform hedefine geçiş**tir. Referans anı bu yüzden kaydırıldı.

## Sapan 5 dosya — ayrıştırma

**(a) Meşru oyun kararları** — bir oyun reposu bunlarsız olamaz:

`ProjectSettings/ProjectSettings.asset` (+8/-4)

| alan | değer |
|---|---|
| `applicationIdentifier.Android` | `com.factorygames.tezgah` |
| `overrideDefaultApplicationIdentifier` | `1` |
| `AndroidTargetArchitectures` | `2` (ARM64) |
| `scriptingBackend.Android` | IL2CPP |
| `m_BuildTargetBatching` | platform girişi eklendi |

**(b) Unity'nin otomatik şema tamamlaması** — kod değil, editör yazdı:

| dosya | diff | Unity'nin kendi beyanı |
|---|---|---|
| `Assets/DefaultVolumeProfile.asset` | +3/-0 | log: "modified to ensure all overrides are present" |
| `Assets/Settings/UniversalRP.asset` | +37/-28 | `k_AssetVersion` 13'e yükseldi |
| `Assets/UniversalRenderPipelineGlobalSettings.asset` | +15/-1 | `rid` listesi dolduruldu |
| `ProjectSettings/UnityConnectSettings.asset` | +6/-0 | dashboard / Insights alanları |

## Taşımanın sınırı (kör bölge değil)

- Hash'ler **mekanik** üretildi (`preset-hashes.json`'ın kendi kuralı: elle yazılmaz);
  satır sonu normalize edilmiş sha256 (CRLF/CR → LF).
- **Dosya listesi değişmedi:** 39 dosya aynen; kapsam **daraltılmadı**, yalnız 5 hash
  tazelendi. Bundan sonraki her sapma bu 5 dosyada da yine **KIRMIZI** verir.
- Doğrulama: taşıma sonrası `lint.py` → PRESET-SAPMA **YEŞİL** (39/39), kırmızı 0, exit 0.

## Kuyruğa alınan (bu turun kapsamı DIŞINDA — ayrı GO)

factory.core `v0.1.9`: kanonik preset "scaffold + platform-set + headless ilk açılış"
sonrasından üretilecek. O geldiğinde bu dosyadaki taşıma gereksizleşir ve baseline
yeniden paketten türer.
