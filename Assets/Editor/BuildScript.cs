using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Game.EditorTools
{
    /// <summary>
    /// C+ duzeni: Unity CI runner'inda KOSMAZ. Android APK'si ve iOS Xcode projesi
    /// YERELDE uretilir; kanit metin olarak depoya girer, xcodeproj ise macOS
    /// runner'a GECICI bir Release asset'i uzerinden tasinir (git tarihine girmez).
    ///
    /// Sablonun productName'i rakamla baslayabildigi icin (sonda bulgusu) uygulama
    /// kimligi burada KODDA verilir - kaynagi olan durum.
    /// </summary>
    public static class BuildScript
    {
        private const string SCENE = "Assets/Scenes/SampleScene.unity";
        private const string APPLICATION_ID = "com.factorygames.tezgah";

        [MenuItem("FactoryGames/Build Android")]
        public static void BuildAndroid()
        {
            string cikti = Hazirla("android");
            string apk = Path.Combine(cikti, "tezgah.apk");

            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, APPLICATION_ID);

            // arm64 tek mimari: 0B hedefi (Ek A) - 32 bit tasinmaz.
            // SIRA ONEMLI (olculdu): ARM64 yalnizca IL2CPP ile secilebilir; backend
            // Mono kalirsa mimari atamasi sessizce dusuyor ve BuildPlayer
            // "Target architecture not specified" ile kiriliyor.
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            if (PlayerSettings.Android.targetArchitectures != AndroidArchitecture.ARM64)
                throw new Exception("mimari atamasi tutmadi: " + PlayerSettings.Android.targetArchitectures);

            BuildReport rapor = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { SCENE },
                locationPathName = apk,
                target = BuildTarget.Android,
                targetGroup = BuildTargetGroup.Android,
                options = BuildOptions.None
            });

            Ozetle("android", rapor);
            if (rapor.summary.result != BuildResult.Succeeded)
                throw new Exception("Android build basarisiz: " + rapor.summary.result);
            if (!File.Exists(apk))
                throw new Exception("build 'Succeeded' dedi ama APK yok - kanit yok");

            Debug.Log($"[tezgah-build] APK boyut={new FileInfo(apk).Length} bayt yol={apk}");
        }

        [MenuItem("FactoryGames/Build iOS Xcode Project")]
        public static void BuildIos()
        {
            string cikti = Hazirla("ios");

            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.iOS, APPLICATION_ID);
            BuildReport rapor = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { SCENE },
                locationPathName = cikti,
                target = BuildTarget.iOS,
                targetGroup = BuildTargetGroup.iOS,
                options = BuildOptions.None
            });

            Ozetle("ios", rapor);
            if (rapor.summary.result != BuildResult.Succeeded)
                throw new Exception("iOS proje uretimi basarisiz: " + rapor.summary.result);

            string[] proj = Directory.GetDirectories(cikti, "*.xcodeproj", SearchOption.AllDirectories);
            if (proj.Length == 0)
                throw new Exception("build 'Succeeded' dedi ama *.xcodeproj yok - kanit yok");

            Debug.Log($"[tezgah-build] xcodeproj={string.Join(";", proj.Select(Path.GetFileName))}");
        }

        private static string Hazirla(string ad)
        {
            if (!File.Exists(SCENE)) throw new FileNotFoundException("sahne yok: " + SCENE);
            string dizin = Path.Combine(Directory.GetCurrentDirectory(), "Build", ad);
            if (Directory.Exists(dizin)) Directory.Delete(dizin, true);
            Directory.CreateDirectory(dizin);
            return dizin;
        }

        private static void Ozetle(string ad, BuildReport rapor)
        {
            BuildSummary s = rapor.summary;
            Debug.Log($"[tezgah-build] {ad}: sonuc={s.result} sure={s.totalTime} " +
                      $"boyut={s.totalSize} hata={s.totalErrors} uyari={s.totalWarnings}");
        }
    }
}
