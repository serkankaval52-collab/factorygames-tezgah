using NUnit.Framework;

namespace Game.Tests.EditMode
{
    /// <summary>
    /// P5 kopya kilidi. Game.Core.AnalyticsEvents Unity'siz derlendigi icin
    /// cekirdege referans veremez ve SESSIZ_TOPARLANMA degerini TEKRAR yazar.
    /// Kopya sessiz kalmasin diye esitlik burada kilitlenir: cekirdek degeri
    /// degisirse bu test kirmizi yanar.
    /// </summary>
    public sealed class OlayParitesiTests
    {
        [Test]
        public void SessizToparlanma_CekirdekDegeriyleAyni()
        {
            Assert.That(Game.Core.AnalyticsEvents.SESSIZ_TOPARLANMA,
                        Is.EqualTo(FactoryGames.Core.AnalyticsEvents.SESSIZ_TOPARLANMA));
        }
    }
}
