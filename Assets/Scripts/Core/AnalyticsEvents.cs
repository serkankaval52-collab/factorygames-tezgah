namespace Game.Core
{
    /// <summary>
    /// B4 olay haritasinin TEK KAYNAGI. GDD (docs/plan.md B4) bu sabitlerden
    /// turer; CI'daki events-parity isi kod -> doc yonunde karsilastirir:
    /// burada tanimli her sabit planda satir bulmak ZORUNDADIR ve planda
    /// buradan gelmeyen olay adi bulunamaz.
    ///
    /// Ekleme sirasi: once bu dosya, sonra plan. Tersi calismaz - parite kirilir.
    ///
    /// Bu sinif Unity API'sine dokunmaz (kod-standardi 1. bolum): CI'da Unity'siz
    /// derlenir ve pariteyi Python tarafi bu dosyadan okur.
    /// </summary>
    public static class AnalyticsEvents
    {
        // --- oturum / sezon iskeleti ---
        public const string OTURUM_BASLADI = "oturum_basladi";
        public const string SEZON_BASLADI = "sezon_basladi";
        public const string SEZON_BITTI = "sezon_bitti";

        // --- gun dongusu (30 sn tur) ---
        public const string GUN_BASLADI = "gun_basladi";
        public const string GUN_BITTI = "gun_bitti";

        // --- cekirdek kararlar (kart A: stok tahsisi) ---
        public const string URUN_RAFA_YERLESTIRILDI = "urun_rafa_yerlestirildi";
        public const string URUN_ONE_CIKARILDI = "urun_one_cikarildi";
        public const string MUSTERI_KARSILANDI = "musteri_karsilandi";
        public const string MUSTERI_GERI_CEVRILDI = "musteri_geri_cevrildi";

        // --- kisit sinyali (tukenen sezon stogu) ---
        public const string STOK_TUKENDI = "stok_tukendi";

        // --- K3 odul takasi (1 izleme = 1 turluk tabela; STOK VERMEZ) ---
        public const string TABELA_TEKLIF_EDILDI = "tabela_teklif_edildi";
        public const string TABELA_KULLANILDI = "tabela_kullanildi";

        /// <summary>
        /// P5 zorunlu satiri. Deger cekirdekteki
        /// FactoryGames.Core.AnalyticsEvents.SESSIZ_TOPARLANMA ile AYNI olmak
        /// zorundadir; kopya sessiz kalmasin diye EditMode testi esitligi kilitler
        /// (Assets/Tests/EditMode/OlayParitesiTests.cs). Burada yeniden tanimlanma
        /// sebebi: bu dosya Unity'siz derlenir, cekirdege referans veremez.
        /// </summary>
        public const string SESSIZ_TOPARLANMA = "sessiz_toparlanma";
    }
}
