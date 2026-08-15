using System;

namespace Game.Core
{
    /// <summary>
    /// Cekirdek kural yuzeyi — Unity API'si YOK (kod-standardi §1), bu yuzden
    /// hem Unity EditMode'da hem CI'da `dotnet test` ile ayni kaynak kosar.
    ///
    /// KAPSAM UYARISI (Asama 2): burasi ISKELETTIR. Denge SAYILARI bu dosyada
    /// DEGIL, StreamingAssets/config.json'da yasar (Sozlesme-2 tek kaynagi) ve
    /// degerleri tools/denge_sim.py ciktisiyla dolar (B8). Buradaki fonksiyonlar
    /// yalnizca kurallarin BICIMINI sabitler; sabit sayi tasimazlar.
    /// </summary>
    public static class TezgahRules
    {
        /// <summary>Sezon stogu bir kez verilir ve asla yenilenmez (kart A kisiti).</summary>
        public static int StokDus(int kalanStok, int satilanAdet)
        {
            if (kalanStok < 0) throw new ArgumentOutOfRangeException(nameof(kalanStok));
            if (satilanAdet < 0) throw new ArgumentOutOfRangeException(nameof(satilanAdet));
            return Math.Max(0, kalanStok - satilanAdet);
        }

        /// <summary>Stok bitince sezon biter — kisit oyuncuya bu satirda gorunur.</summary>
        public static bool SezonBittiMi(int kalanStok) => kalanStok <= 0;

        /// <summary>
        /// Bir gunde karsilanabilecek musteri sayisi: rafta duran adetle sinirlidir.
        /// Talep raftan buyukse fark GERI CEVRILIR — reddin kendisi bir karardir.
        /// </summary>
        public static int Karsilanan(int raftakiAdet, int talep)
        {
            if (raftakiAdet < 0) throw new ArgumentOutOfRangeException(nameof(raftakiAdet));
            if (talep < 0) throw new ArgumentOutOfRangeException(nameof(talep));
            return Math.Min(raftakiAdet, talep);
        }

        /// <summary>Karsilanamayan talep. Skor/itibar etkisi B3'te sayilanir.</summary>
        public static int GeriCevrilen(int raftakiAdet, int talep)
            => Math.Max(0, talep - Karsilanan(raftakiAdet, talep));

        /// <summary>
        /// K3 takasi: 1 izleme = 1 TURLUK musteri-cekim tabelasi. STOK VERMEZ —
        /// yalnizca o turun talebini carpar. Carpan config.json'dan gelir.
        /// </summary>
        public static int TabelaliTalep(int tabanTalep, double carpan)
        {
            if (tabanTalep < 0) throw new ArgumentOutOfRangeException(nameof(tabanTalep));
            if (carpan < 1.0) throw new ArgumentOutOfRangeException(nameof(carpan));
            return (int)Math.Round(tabanTalep * carpan, MidpointRounding.AwayFromZero);
        }
    }
}
