using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using NUnit.Framework;

namespace Game.Core.Tests
{
    /// <summary>
    /// Iskelet testi: esik dosyasinin CI'da GERCEKTEN okunabildigini kanitlar.
    /// Bos bir "Assert.Pass" testi CI'in calistigini gostermez; bu test kapilarin
    /// besledigi tek sayi kaynagini (Ek C kopyasi) dogrular — Sozlesme-8:
    /// "Ek C'de olmayan sayi hicbir kapida kullanilamaz".
    ///
    /// Ayrica 0A saha bulgusu: Windows araclari JSON'a BOM ekleyebiliyor; okuyucu
    /// BOM'u tolere etmeli, aksi halde kapi sessizce kirilir.
    /// </summary>
    public sealed class EsiklerTests
    {
        private static readonly string[] ZORUNLU_ALANLAR =
        {
            "gorsel_kontrast_ana_ozne",
            "gorsel_kontrast_ui_metin",
            "gorsel_palet_kademe",
            "gorsel_anim_kare_band",
            "ses_lufs_band",
            "ses_tepe_dbtp",
            "premium_gecis_sure_band",
            "premium_kare_hizi_secenek",
            "ilk_surum_diller",
            // NOT: `uygulama_boyut_tavan_mb` bu listede DEGILDIR — Ek C'de degeri yok
            // (kural 28). Eksikligi lint tarafinda VERI-YOK satiri uretir; kullanicinin
            // 0A-6 form donusu geldiginde hem esikler.json'a hem buraya eklenir.
        };

        private static string EsiklerYolu()
        {
            var dir = new DirectoryInfo(TestContext.CurrentContext.TestDirectory);
            while (dir != null)
            {
                string aday = Path.Combine(dir.FullName, "tools", "lint", "esikler.json");
                if (File.Exists(aday)) return aday;
                dir = dir.Parent;
            }
            return null;
        }

        [Test]
        public void Esikler_Dosyasi_Bulunur_Ve_Cozumlenir()
        {
            string yol = EsiklerYolu();
            Assert.That(yol, Is.Not.Null, "tools/lint/esikler.json bulunamadi");

            // BOM'lu dosyayi da kabul et (0A bulgusu)
            string metin = File.ReadAllText(yol).TrimStart('﻿');
            Assert.DoesNotThrow(() => JsonDocument.Parse(metin), "esikler.json gecerli JSON degil");
        }

        [Test]
        public void Zorunlu_Esik_Alanlari_Eksiksiz()
        {
            string yol = EsiklerYolu();
            Assert.That(yol, Is.Not.Null);

            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(yol).TrimStart('﻿'));
            var eksik = new List<string>();
            foreach (string alan in ZORUNLU_ALANLAR)
                if (!doc.RootElement.TryGetProperty(alan, out _)) eksik.Add(alan);

            Assert.That(eksik, Is.Empty, "esikler.json'da eksik alan: " + string.Join(", ", eksik));
        }

        [Test]
        public void Kare_Hizi_Secenegi_Sozlesmeye_Uygun()
        {
            string yol = EsiklerYolu();
            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(yol).TrimStart('﻿'));
            var izinli = new HashSet<int> { 30, 60 };

            foreach (JsonElement e in doc.RootElement.GetProperty("premium_kare_hizi_secenek").EnumerateArray())
                Assert.That(izinli, Does.Contain(e.GetInt32()),
                    "premium-sozlesme P6: izinli degerler yalniz 30 veya 60");
        }
    }
}
