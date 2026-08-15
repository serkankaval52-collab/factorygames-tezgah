using System.Collections;
using Game.Runtime;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Game.Tests.PlayMode
{
    /// <summary>
    /// Zincirin ucdan uca kaniti: sablon sahnesi + UPM cekirdegi + kod-oncelikli
    /// kurulum. Sahne dosyasina HIC dokunulmadan hiyerarsi dogmus olmali
    /// (kural 7/8) ve palet StreamingAssets'ten okunmus olmali (G1 tek kaynagi).
    /// </summary>
    public sealed class BootstrapTests
    {
        [UnityTest]
        public IEnumerator Boot_KokNesneyiKodlaKurar()
        {
            yield return null;   // BeforeSceneLoad kancasi kosmus olsun

            Assert.That(TezgahBootstrap.Root, Is.Not.Null,
                        "RuntimeInitializeOnLoadMethod kok nesneyi kurmadi");
            Assert.That(TezgahBootstrap.Root.name, Is.EqualTo(TezgahBootstrap.ROOT_NAME));
        }

        [UnityTest]
        public IEnumerator Boot_KameraKokAltinda_VeOrtografik()
        {
            yield return null;

            Camera kamera = TezgahBootstrap.Root.GetComponentInChildren<Camera>();
            Assert.That(kamera, Is.Not.Null, "kamera kok altinda kurulmadi");
            Assert.That(kamera.orthographic, Is.True, "2D icin ortografik kamera bekleniyor");
        }

        [UnityTest]
        public IEnumerator Palet_StreamingAssetsTenOkundu()
        {
            yield return null;

            // Okunamadiysa kaynak "OKUNAMADI (...)" ile baslar — sessiz varsayim yok (kural 6).
            Assert.That(TezgahBootstrap.PaletKaynagi, Is.Not.Null);
            Assert.That(TezgahBootstrap.PaletKaynagi, Does.Not.StartWith("OKUNAMADI"),
                        "palette.json okunamadi: " + TezgahBootstrap.PaletKaynagi);
            Assert.That(TezgahBootstrap.PaletKaynagi, Does.EndWith("palette.json"));
        }
    }
}
