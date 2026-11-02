using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Usrah.EditorTools
{
    /// <summary>Builds the Home scene from the exported models, so the scene is reproducible.</summary>
    public static class HomeSceneBuilder
    {
        const string ScenePath = "Assets/Scenes/Home.unity";
        const string Models = "Assets/Art/Models/";
        const string Materials = "Assets/Art/Materials/";
        const string LightingAsset = "Assets/Scenes/HomeLighting.lighting";
        const int CharacterLayer = 6;
        const float RoomHeight = 2.78f;

        // Matches tools/blender/usrah/room.py: camera straight along the room, lens shift for the horizon
        const float BackY = 4f, CamDist = 8.64f, CamHeight = 2.3f, Lens = 35f;
        const float PxW = 1600f;
        static float FocalPx => PxW * Lens / 36f;
        static float HorizonPx => 560f - FocalPx * CamHeight / CamDist;

        [MenuItem("Usrah/Build Home Scene")]
        public static void Build()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var room = Spawn("room");
            room.name = "Room";
            Report(room);

            UseUnlitForGlow(room);
            MarkRoomStatic(room);
            Place("nabeeh", room, "spot_host", 8f);
            Place("cat", room, "spot_cat", 20f);

            MakeCamera();
            MakeLights();

            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
        }

        static GameObject Spawn(string model)
        {
            var asset = AssetDatabase.LoadAssetAtPath<GameObject>(Models + model + ".fbx");
            return (GameObject)PrefabUtility.InstantiatePrefab(asset);
        }

        /// <summary>The view outside the window ignores the room's lights.</summary>
        static void UseUnlitForGlow(GameObject room)
        {
            Directory.CreateDirectory(Materials);
            foreach (var renderer in room.GetComponentsInChildren<Renderer>())
            {
                var source = renderer.sharedMaterial;
                if (source == null) continue;
                if (source.name == "sky")
                    renderer.sharedMaterial = SavedMaterial("sky", "Usrah/SkyGradient", null);
                else if (source.name == "rug")
                {
                    var rug = SavedMaterial("rug", "Universal Render Pipeline/Lit", Color.white);
                    rug.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Textures/rug.png"));
                    rug.SetFloat("_Smoothness", .3f);
                    rug.SetFloat("_EnvironmentReflections", 0f);
                    renderer.sharedMaterial = rug;
                }
                else if (source.name.StartsWith("glow_"))
                    renderer.sharedMaterial = SavedMaterial(source.name, "Universal Render Pipeline/Unlit",
                        source.GetColor("_BaseColor"));
            }
        }

        /// <summary>See-through glasses lens: nearly clear, with a soft highlight.</summary>
        static Material LensMaterial()
        {
            var lens = SavedMaterial("lens", "Universal Render Pipeline/Lit", new Color(1f, 1f, 1f, .12f));
            lens.SetFloat("_Surface", 1f);
            lens.SetFloat("_Blend", 0f);
            lens.SetFloat("_SrcBlend", (float)UnityEngine.Rendering.BlendMode.SrcAlpha);
            lens.SetFloat("_DstBlend", (float)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            lens.SetFloat("_ZWrite", 0f);
            lens.SetFloat("_Smoothness", .9f);
            lens.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            lens.renderQueue = (int)UnityEngine.Rendering.RenderQueue.Transparent;
            lens.SetOverrideTag("RenderType", "Transparent");
            EditorUtility.SetDirty(lens);
            return lens;
        }

        static Material SavedMaterial(string name, string shader, Color? color)
        {
            var path = Materials + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(Shader.Find(shader));
                AssetDatabase.CreateAsset(material, path);
            }
            if (color.HasValue) material.SetColor("_BaseColor", color.Value);
            return material;
        }

        static void Place(string model, GameObject room, string spot, float yaw)
        {
            var target = room.GetComponentsInChildren<Transform>().First(t => t.name == spot);
            // A wrapper at the spot, so the model's own root transform stays untouched
            var holder = new GameObject(model + "_spot").transform;
            holder.SetPositionAndRotation(target.position, Quaternion.Euler(0f, yaw, 0f));
            holder.localScale = target.lossyScale;
            var character = Spawn(model);
            character.name = model;
            character.transform.SetParent(holder, false);
            foreach (var t in character.GetComponentsInChildren<Transform>()) t.gameObject.layer = CharacterLayer;
            foreach (var renderer in character.GetComponentsInChildren<Renderer>())
                if (renderer.sharedMaterial != null && renderer.sharedMaterial.name == "lens")
                {
                    renderer.sharedMaterial = LensMaterial();
                    renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                }
        }

        static void Report(GameObject room)
        {
            var bounds = new Bounds(room.transform.position, Vector3.zero);
            foreach (var r in room.GetComponentsInChildren<Renderer>()) bounds.Encapsulate(r.bounds);
            Debug.Log($"USRAH room bounds {bounds}");
            foreach (var name in new[] { "wall_left", "wall_right", "wall_below", "spot_host", "low_table" })
            {
                var t = room.GetComponentsInChildren<Transform>().FirstOrDefault(x => x.name == name);
                Debug.Log($"USRAH {name} at {(t ? t.position.ToString("F2") : "missing")}");
            }
        }

        static void MakeCamera()
        {
            var go = new GameObject("Camera");
            go.tag = "MainCamera";
            var cam = go.AddComponent<Camera>();
            go.AddComponent<UniversalAdditionalCameraData>();
            go.AddComponent<AudioListener>();
            // The FBX import maps Blender (x, y, z) to Unity (x, z, y)
            go.transform.position = new Vector3(0f, CamHeight, BackY - CamDist);
            go.transform.rotation = Quaternion.identity;
            cam.usePhysicalProperties = true;
            cam.focalLength = Lens;
            cam.sensorSize = new Vector2(36f, 36f * 9f / 16f);
            cam.gateFit = Camera.GateFitMode.Vertical;
            cam.lensShift = new Vector2(0f, -(450f - HorizonPx) / 900f);
            cam.nearClipPlane = .3f;
            cam.farClipPlane = 30f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color32(0xF2, 0xD9, 0xB4, 0xFF);
        }

        static void MakeLights()
        {
            // The room is lightmapped: sky and bounce come from the bake. Characters aren't static,
            // so they get this same ambient plus their own soft key light (see below).
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(.66f, .63f, .58f);

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.lightmapBakeType = LightmapBakeType.Baked;
            sun.color = new Color32(0xFF, 0xCF, 0x96, 0xFF);
            sun.intensity = 5f;
            sun.shadows = LightShadows.Soft;
            sun.shadowAngle = 1f;
            // Blender's sun direction is (.16, -.8, -.58)
            sun.transform.rotation = Quaternion.LookRotation(new Vector3(.16f, -.58f, -.8f));

            var fill = new GameObject("Fill").AddComponent<Light>();
            fill.type = LightType.Rectangle;
            fill.lightmapBakeType = LightmapBakeType.Baked;
            fill.color = new Color32(0xFF, 0xF6, 0xE8, 0xFF);
            fill.areaSize = new Vector2(7f, 4f);
            fill.intensity = 2.1f;
            fill.range = 14f;
            fill.transform.SetPositionAndRotation(new Vector3(0f, 4.2f, -2.8f),
                Quaternion.LookRotation(new Vector3(0f, .4f, 2.2f) - new Vector3(0f, 4.2f, -2.8f)));

            // The left wall faces away from the sun, so it gets its own quiet fill
            var side = new GameObject("FillLeft").AddComponent<Light>();
            side.type = LightType.Rectangle;
            side.lightmapBakeType = LightmapBakeType.Baked;
            side.color = new Color32(0xFF, 0xF1, 0xE0, 0xFF);
            side.areaSize = new Vector2(3f, 3f);
            side.intensity = 1.3f;
            side.range = 8f;
            side.transform.SetPositionAndRotation(new Vector3(2.4f, 2.2f, 0.5f), Quaternion.LookRotation(Vector3.left));

            // Only for the room's bake: stops sun coming over the top of the back wall
            var blocker = GameObject.CreatePrimitive(PrimitiveType.Cube);
            blocker.name = "SunBlocker";
            Object.DestroyImmediate(blocker.GetComponent<Collider>());
            blocker.transform.position = new Vector3(0f, RoomHeight + 4.05f, BackY + .1f);
            blocker.transform.localScale = new Vector3(30f, 8f, .1f);
            var blockerRenderer = blocker.GetComponent<MeshRenderer>();
            blockerRenderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.ShadowsOnly;
            GameObjectUtility.SetStaticEditorFlags(blocker, StaticEditorFlags.ContributeGI);

            // Soft key light on the characters only
            var key = new GameObject("CharacterKey").AddComponent<Light>();
            key.type = LightType.Directional;
            key.lightmapBakeType = LightmapBakeType.Realtime;
            key.color = new Color32(0xFF, 0xF3, 0xE2, 0xFF);
            key.intensity = .62f;
            key.shadows = LightShadows.None;
            key.cullingMask = 1 << CharacterLayer;
            key.transform.rotation = Quaternion.LookRotation(new Vector3(.35f, -.7f, .6f));
        }

        static void MarkRoomStatic(GameObject room)
        {
            foreach (var renderer in room.GetComponentsInChildren<MeshRenderer>())
            {
                var go = renderer.gameObject;
                var flags = StaticEditorFlags.BatchingStatic;
                var size = renderer.bounds.size;
                // Tiny parts (lattice beads, keypad dots) aren't worth lightmap space
                if (Mathf.Max(size.x, size.y, size.z) > .08f) flags |= StaticEditorFlags.ContributeGI;
                GameObjectUtility.SetStaticEditorFlags(go, flags);
                // The sun's lattice pattern lands on the floor and rug, so they get finer lightmaps
                if (go.name == "floor" || go.name == "rug")
                {
                    var so = new SerializedObject(renderer);
                    so.FindProperty("m_ScaleInLightmap").floatValue = 2.5f;
                    so.ApplyModifiedPropertiesWithoutUndo();
                }
                if (go.name.StartsWith("hill") || go.name.StartsWith("tree_") || go.name.StartsWith("trunk_") || go.name == "sky")
                {
                    GameObjectUtility.SetStaticEditorFlags(go, StaticEditorFlags.BatchingStatic);
                    renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                }
            }
        }

        /// <summary>Bake the room's light. Run after Build, from the command line or the menu.</summary>
        [MenuItem("Usrah/Bake Home Lighting")]
        public static void Bake()
        {
            var scene = EditorSceneManager.OpenScene(ScenePath);
            var settings = new LightingSettings
            {
                lightmapper = LightingSettings.Lightmapper.ProgressiveGPU,
                bakedGI = true,
                realtimeGI = false,
                lightmapResolution = 55f,
                lightmapPadding = 2,
                lightmapMaxSize = 2048,
                directSampleCount = 32,
                indirectSampleCount = 256,
                environmentSampleCount = 64,
                maxBounces = 3,
                directionalityMode = LightmapsMode.NonDirectional,
                lightmapCompression = LightmapCompression.NormalQuality,
                ao = true,
                aoMaxDistance = .6f,
                aoExponentDirect = 0f,
                aoExponentIndirect = 1.2f,
                filteringMode = LightingSettings.FilterMode.Auto,
            };
            AssetDatabase.CreateAsset(settings, LightingAsset);
            Lightmapping.lightingSettings = settings;
            var started = System.DateTime.Now;
            var ok = Lightmapping.Bake();
            Debug.Log($"USRAH bake ok={ok} in {(System.DateTime.Now - started).TotalSeconds:F0}s, {LightmapSettings.lightmaps.Length} lightmaps");
            EditorSceneManager.SaveScene(scene);
        }

        /// <summary>Render the Home camera to a PNG, for checking the scene from the command line.</summary>
        [MenuItem("Usrah/Screenshot Home")]
        public static void Screenshot()
        {
            var args = System.Environment.GetCommandLineArgs();
            var i = System.Array.IndexOf(args, "-shot");
            var path = i >= 0 ? args[i + 1] : "home.png";
            EditorSceneManager.OpenScene(ScenePath);
            var cam = Camera.main;
            const int w = 1600, h = 900;
            var rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = 4 };
            cam.targetTexture = rt;
            // The first frames upload material data, so let a few go by before capturing
            for (var frame = 0; frame < 4; frame++) cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            File.WriteAllBytes(path, tex.EncodeToPNG());
            cam.targetTexture = null;
            RenderTexture.active = null;
            Debug.Log($"USRAH screenshot {path}");
        }
    }
}
