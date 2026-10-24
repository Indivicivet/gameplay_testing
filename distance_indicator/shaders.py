"""GLSL post-processing shaders for camera effects.

Includes high-quality optical radial zoom blur and peripheral vignette.
"""

from ursina.shader import Shader
from ursina import Vec2

# High-performance screen-space post-processing shader
POST_PROCESS_SHADER = Shader(
    fragment="""
#version 430

uniform sampler2D tex;
in vec2 uv;
out vec4 fragColor;

uniform float blur_intensity;       // Radial optical zoom blur strength
uniform float vignette_intensity;   // Peripheral edge darkening
uniform vec2 center;                // Blur center (screen UV coordinates)

void main() {
    vec2 to_uv = uv - center;
    float dist = length(to_uv);
    vec2 dir = (dist > 0.0001) ? normalize(to_uv) : vec2(0.0);

    // 1. High-Quality Optical Radial Zoom Blur
    // Center is crisp and clear; blur smoothly radiates outward towards screen edges
    vec4 sum = vec4(0.0);
    float total_weight = 0.0;
    const int SAMPLES = 16;

    // Edge falloff: keep center viewing area crisp
    float edge_falloff = smoothstep(0.12, 0.85, dist);
    float max_blur_dist = blur_intensity * 0.048 * edge_falloff;

    for (int i = 0; i < SAMPLES; i++) {
        float t = float(i) / float(SAMPLES - 1);
        vec2 sample_uv = uv - dir * (t * max_blur_dist);
        float weight = 1.0 - t * 0.55; // Natural smooth attenuation
        sum += texture(tex, clamp(sample_uv, 0.0, 1.0)) * weight;
        total_weight += weight;
    }
    vec4 blurred = sum / total_weight;

    // 2. Peripheral Vignette (Subtle edge contrast framing)
    float vig = smoothstep(0.35, 0.95, dist);
    vec3 col = mix(blurred.rgb, blurred.rgb * (1.0 - vignette_intensity * 0.75), vig);

    fragColor = vec4(col, 1.0);
}
""",
    default_input=dict(
        blur_intensity=0.0,
        vignette_intensity=0.0,
        center=Vec2(0.5, 0.5),
    ),
)
