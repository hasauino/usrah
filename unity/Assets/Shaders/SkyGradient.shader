// The view through the window: horizon to sky, by world height.
Shader "Usrah/SkyGradient"
{
    Properties
    {
        _Horizon ("Horizon", Color) = (1, 0.914, 0.769, 1)
        _Sky ("Sky", Color) = (0.549, 0.784, 0.91, 1)
        _Bottom ("Horizon height", Float) = 0.7
        _Top ("Sky height", Float) = 2.5
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _Horizon;
                float4 _Sky;
                float _Bottom;
                float _Top;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float height : TEXCOORD0; };

            Varyings vert(Attributes input)
            {
                Varyings output;
                float3 world = TransformObjectToWorld(input.positionOS.xyz);
                output.positionCS = TransformWorldToHClip(world);
                output.height = world.y;
                return output;
            }

            float4 frag(Varyings input) : SV_Target
            {
                return lerp(_Horizon, _Sky, saturate((input.height - _Bottom) / (_Top - _Bottom)));
            }
            ENDHLSL
        }
    }
}
