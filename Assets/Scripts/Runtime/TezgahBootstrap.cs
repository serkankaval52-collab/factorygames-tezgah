using FactoryGames.Core;
using UnityEngine;

namespace Game.Runtime
{
    /// <summary>Palet dosyasinin okunabilir yuzeyi (G1 zorunlu rolleri).</summary>
    [System.Serializable]
    public sealed class PaletRoller
    {
        public string arka_plan;
        public string ana_ozne;
        public string vurgu;
        public string tehlike;
        public string ui_metin;
        public string ui_zemin;
    }

    /// <summary>StreamingAssets/palette.json govdesi.</summary>
    [System.Serializable]
    public sealed class PaletDosyasi
    {
        public PaletRoller roller;
    }

    /// <summary>
    /// Kod-oncelikli kurulum (kural 7/8): sahne dosyasi sablon varsayilaninda KALIR,
    /// hiyerarsi burada dogar. GameObject.Find / FindFirstObjectByType / Camera.main
    /// kullanilmaz; referanslar kurulum aninda acikca atanir.
    ///
    /// KAPSAM (Asama 2): bu iskelet yalnizca ZINCIRIN kanitidir — sablon + UPM
    /// cekirdegi + runtime kurulumu calisiyor. Oyun dongusu Asama 4'te buraya
    /// baglanir; simdilik oyuncu yuzeyi yoktur.
    /// </summary>
    public static class TezgahBootstrap
    {
        public const string ROOT_NAME = "TezgahRoot";
        private const float WORLD_HALF_HEIGHT = 5f;

        /// <summary>Palet okunamazsa kullanilan notr zemin — sessiz varsayim DEGIL,
        /// gorunur yedek: durum gelistirme yuzeyine yazilir (kural 6).</summary>
        private const string YEDEK_ZEMIN = "#808080";

        public static GameObject Root { get; private set; }

        /// <summary>Palet okunamadiysa kaynagi burada durur (beyan degil, artefakt).</summary>
        public static string PaletKaynagi { get; private set; }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        public static void Boot()
        {
            if (Root != null) return;   // idempotent

            Root = RuntimeInitBootstrap.CreateRoot(ROOT_NAME);
            RuntimeInitBootstrap.CreateOrthographicCamera(
                Root.transform, WORLD_HALF_HEIGHT, ArkaPlan());

#if UNITY_EDITOR || DEVELOPMENT_BUILD
            Debug.Log($"[tezgah] boot ok — kok={ROOT_NAME} palet={PaletKaynagi}");
#endif
        }

        /// <summary>
        /// Kamera zemini palet rolunden gelir. Deger BURADA YAZILMAZ: kaynak
        /// StreamingAssets/palette.json (G1), o da sanat yonu paketinden alintidir.
        /// </summary>
        private static Color ArkaPlan()
        {
            PaletDosyasi palet = JsonLoader.Load<PaletDosyasi>("palette.json", out string kaynak);
            PaletKaynagi = kaynak;

            string hex = palet?.roller?.arka_plan;
            if (string.IsNullOrEmpty(hex) || !ColorUtility.TryParseHtmlString(hex, out Color renk))
            {
#if UNITY_EDITOR || DEVELOPMENT_BUILD
                Debug.LogWarning($"[tezgah] arka_plan cozumlenemedi (kaynak: {kaynak}) — yedek zemin");
#endif
                ColorUtility.TryParseHtmlString(YEDEK_ZEMIN, out renk);
            }
            return renk;
        }

        /// <summary>Testlerin temiz baslamasi icin (PlayMode).</summary>
        internal static void Sifirla() => Root = null;
    }
}
