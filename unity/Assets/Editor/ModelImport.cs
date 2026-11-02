using UnityEditor;
using UnityEngine;

namespace Usrah.EditorTools
{
    /// <summary>Import rules for the FBX models exported by tools/blender/export_game.py.</summary>
    public class ModelImport : AssetPostprocessor
    {
        const string ModelsPath = "Assets/Art/Models/";

        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(ModelsPath)) return;
            var importer = (ModelImporter)assetImporter;
            importer.globalScale = 1f;
            importer.useFileScale = true;
            importer.bakeAxisConversion = true;
            importer.importNormals = ModelImporterNormals.Import;
            importer.importTangents = ModelImporterTangents.None;
            importer.importCameras = false;
            importer.importLights = false;
            importer.importAnimation = false;
            importer.animationType = ModelImporterAnimationType.None;
            importer.meshCompression = ModelImporterMeshCompression.Medium;
            importer.isReadable = false;
            // Only the room is lightmapped
            importer.generateSecondaryUV = assetPath.EndsWith("room.fbx");
            importer.secondaryUVPackMargin = 8f;
        }

        void OnPostprocessMaterial(Material material)
        {
            if (!assetPath.StartsWith(ModelsPath)) return;
            // Names look like "vinyl_F6E9CF": the kit, then the exact sRGB colour
            if (material.name == "rug") return; // Built by HomeSceneBuilder, with its texture
            var parts = material.name.Split('_');
            var kind = parts[0];
            Color color = Color.white;
            if (parts.Length > 1) ColorUtility.TryParseHtmlString("#" + parts[1].Substring(0, 6), out color);

            // glow_* and sky are swapped for unlit materials by HomeSceneBuilder
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Smoothness", kind switch
            {
                "vinyl" => .58f,
                "soft" => .38f,
                "pearl" => .66f,
                "screen" => .82f,
                _ => .25f, // ink, plaster
            });
            material.SetFloat("_Metallic", kind == "pearl" ? .18f : 0f);
            material.SetFloat("_EnvironmentReflections", 0f);
        }
    }
}
