using System;
using Game.Core;
using NUnit.Framework;

namespace Game.Core.Tests
{
    /// <summary>
    /// Cekirdek kural testleri - Unity OLMADAN kosar (C+ ilkesi). Ayni kaynak
    /// dosyalar Unity EditMode'da da derlenir; iki taraf tek gercegi surer.
    ///
    /// Bu testler kural BICIMINI sinar, denge SAYISINI degil: sayilar
    /// config.json'da yasar ve tools/denge_sim.py ciktisiyla dolar (B8).
    ///
    /// NUnit 4 stili: klasik Assert.AreEqual kaldirildi, kisit modeli kullanilir.
    /// </summary>
    public sealed class TezgahRulesTests
    {
        [Test]
        public void StokDus_AsagiTasmaz()
        {
            Assert.That(TezgahRules.StokDus(3, 10), Is.EqualTo(0));
            Assert.That(TezgahRules.StokDus(10, 3), Is.EqualTo(7));
        }

        [Test]
        public void StokDus_NegatifGirdiyiReddeder()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => TezgahRules.StokDus(-1, 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => TezgahRules.StokDus(0, -1));
        }

        [Test]
        public void SezonBitti_StokSifirdaVeAltinda()
        {
            Assert.That(TezgahRules.SezonBittiMi(0), Is.True);
            Assert.That(TezgahRules.SezonBittiMi(1), Is.False);
        }

        [Test]
        public void Karsilanan_RaftakiylenSinirli()
        {
            Assert.That(TezgahRules.Karsilanan(4, 9), Is.EqualTo(4));
            Assert.That(TezgahRules.Karsilanan(6, 2), Is.EqualTo(2));
        }

        [Test]
        public void GeriCevrilen_KarsilananinTumleyeni()
        {
            Assert.That(TezgahRules.GeriCevrilen(4, 9), Is.EqualTo(5));
            Assert.That(TezgahRules.GeriCevrilen(6, 2), Is.EqualTo(0));
        }

        [Test]
        public void TabelaliTalep_TalebiCarpar_StokVermez()
        {
            // K3 kisiti: tabela yalnizca TALEBI etkiler; stok fonksiyona hic girmez.
            Assert.That(TezgahRules.TabelaliTalep(10, 1.5), Is.EqualTo(15));
            Assert.That(TezgahRules.TabelaliTalep(10, 1.0), Is.EqualTo(10));
        }

        [Test]
        public void TabelaliTalep_BirdenKucukCarpaniReddeder()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => TezgahRules.TabelaliTalep(10, 0.9));
        }
    }
}
