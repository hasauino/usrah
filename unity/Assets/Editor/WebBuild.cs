using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;
using UnityEngine.Rendering;

namespace Usrah.EditorTools
{
    /// <summary>Builds the web PWA. Settings follow docs/DESIGN.md (Q28): GitHub Pages can't set
    /// Content-Encoding, so compressed files need the decompression fallback.</summary>
    public static class WebBuild
    {
        [MenuItem("Usrah/Build Web")]
        public static void Build()
        {
            // The URP template leaves this empty, and then the build strips URP's shaders
            GraphicsSettings.defaultRenderPipeline =
                AssetDatabase.LoadAssetAtPath<RenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset");

            PlayerSettings.companyName = "Usrah";
            PlayerSettings.productName = "Usrah";
            // A new version per build, so the PWA's service worker replaces its cache
            var version = System.Environment.GetEnvironmentVariable("USRAH_VERSION");
            PlayerSettings.bundleVersion = string.IsNullOrEmpty(version) ? System.DateTime.UtcNow.ToString("yyyyMMddHHmm") : version;
            PlayerSettings.WebGL.template = "APPLICATION:PWA";
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Brotli;
            PlayerSettings.WebGL.decompressionFallback = true;
            PlayerSettings.WebGL.nameFilesAsHashes = true;
            PlayerSettings.WebGL.exceptionSupport = WebGLExceptionSupport.None;
            PlayerSettings.WebGL.dataCaching = true;
            PlayerSettings.WebGL.initialMemorySize = 128;
            PlayerSettings.WebGL.memoryGrowthMode = WebGLMemoryGrowthMode.Geometric;
            PlayerSettings.WebGL.maximumMemorySize = 1024;
            PlayerSettings.runInBackground = false;
            PlayerSettings.stripEngineCode = true;
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.WebGL, ManagedStrippingLevel.High);
            PlayerSettings.SetIl2CppCodeGeneration(NamedBuildTarget.WebGL, Il2CppCodeGeneration.OptimizeSize);
            // iPad is the priority target. A desktop (DXT) build comes later, per the design doc.
            EditorUserBuildSettings.webGLBuildSubtarget = WebGLTextureSubtarget.ASTC;

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray(),
                locationPathName = "Build/WebGL",
                target = BuildTarget.WebGL,
                options = BuildOptions.None,
            });
            Debug.Log($"USRAH web build {report.summary.result}, {report.summary.totalSize / 1048576f:F1} MB, " +
                      $"{report.summary.totalErrors} errors, {report.summary.totalTime.TotalMinutes:F1} min");
            if (report.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded) EditorApplication.Exit(1);
        }
    }
}
