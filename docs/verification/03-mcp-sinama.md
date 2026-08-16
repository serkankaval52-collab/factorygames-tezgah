# 0B / Aşama 2 — MCP bilinçli sınaması (`com.unity.ai.assistant`)

**Damga (ham):** `1786828441403` · **UTC:** `2026-08-15T21:14Z` (sınama turu)
**Yapan:** executor (otonom) · **Sonuç:** **TETİKLENDİ** · **Karar:** paket **KALMAZ** (mimar v1.4.12)
**Proje:** `factorygames-tezgah` · **Unity:** `6000.3.16f1`

0A-9'da hello-build için sonuç "TETİKLENMEDİ" idi ve orada paket bilinçli olarak
eklenmemişti. 0B kararı, paketin **eklenip ölçülmesiydi**. Bu kayıt onun sonucudur.

## Ölçüm

| adım | ölçüm | sonuç |
|---|---|---|
| EditorPrefs snapshot — **önce** | `HKCU\Software\Unity Technologies\Unity Editor 5.x` | **610** anahtar |
| Paket manifeste | `com.unity.ai.assistant` `1.6.0-pre.1` | sürüm kayıt defterinden seçildi: `6000.3` hedefleyen en yeni. (`latest` = `2.17.0-pre.1` ama `unity=6000.0`) |
| Paket çözümleme | batchmode `-quit` | **RC 0**, `PackageCache/com.unity.ai.assistant@138707014a09` |
| EditorPrefs snapshot — **sonra** | aynı anahtar | **611** anahtar |
| **Fark (kanıt satırı)** | yeni anahtar | **`Unity.AI.MCP.ProjectSettings_h741869426`** |

**EditorLog kanıtı — köprünün kendisi derlendi:**

```
com.unity.ai.assistant@1.6.0-pre.1 (location: .../PackageCache/com.unity.ai.assistant@138707014a09)
Processing assembly ... Unity.AI.MCP.Runtime.dll   (142 defines, 252 references)
Processing assembly ... Unity.AI.MCP.Editor.dll    (140 defines, 289 references)
```

## Kural 30 denetimi — temiz

Sınama log'unda `MCPForUnity` / `McpUnity` / `mcp-unity` eşleşmesi: **0**.
Hiçbir üçüncü taraf köprüye bağlanılmadı.

**Makine düzeyinde bulgu (kural 26 kapsamı, dokunulmadı):** kullanıcı EditorPrefs'inde
97 adet MCP/AI anahtarı var ve çoğunluğu üçüncü taraftır (`MCPForUnity.SetupCompleted`,
`MCPForUnity.HttpUrl`, `MCPForUnity.ToolEnabled.execute_code`, `McpUnity.*` …). Bunlar
`HKCU` altındadır — **kullanıcı genelinde**, proje bazlı değil; kullanıcının kendi
projelerinden gelir. Salt okundu, değiştirilmedi, silinmedi.

**Ayrım ölçüldü ve önemlidir:** Tezgâh projesinde bu köprülerin izi **yok** —
`manifest.json` 0, `Assets/` 0, `PackageCache` 0. Kural 30 uyumu **proje düzeyinde**
sağlamdır; risk makine düzeyinde durur ve fabrika koşusuna sızmaz.

## Yan bulgular (log)

- `com.unity.ai.generators` **deprecated**: işlevi `ai.assistant` içine alınmış.
- **Duplicate assembly:** `ai.assistant` kendi `System.Runtime.CompilerServices.Unsafe.dll`
  (v6.0.3.0) sürümünü getiriyor ve `com.unity.collections`'ınkini (v6.0.0.0) yok sayıyor.
  Bu, kararın gerekçelerinden biri oldu.

## Karar ve geri alma

Paket **kalıcı olarak eklenmez** (mimar v1.4.12). Gerekçe: 0A-9'un "projeye gereksiz
AI yüzeyi taşınmaz" kararı + yukarıdaki duplicate-assembly riski.

Sınama sonrası paket manifest'ten çıkarıldı; temiz dönüş **RC 0**, `PackageCache`
temizlendi, `Packages/manifest.json` net değişiklik **sıfır** (git diff boş).
Yani bu sınama depoya hiçbir iz bırakmadı — bıraktığı tek şey bu ölçüm kaydıdır.
