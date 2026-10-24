"""GLSL post-processing shaders for camera effects.

Includes radial zoom blur, chromatic aberration, vignette, and boundary flash.
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

uniform float blur_intensity;       // Radial blur strength
uniform float chromatic_amount;     // Chromatic aberration (RGB shift)
uniform float vignette_intensity;   // Edge darkening
uniform float flash_intensity;      // Bright edge/vignette flash on threshold cross
uniform vec2 center;                // Blur center (screen UV coordinates)

void main() {
    vec2 to_uv = uv - center;
    float dist = length(to_uv);
    vec2 dir = normalize(to_uv);

    // 1. Radial / Zoom Blur
    vec4 sum = vec4(0.0);
    const int SAMPLES = 10;
    float step_scale = (blur_intensity * 0.05 * smoothstep(0.1, 0.9, dist)) / float(SAMPLES);

    for (int i = 0; i < SAMPLES; i++) {
        vec2 sample_uv = uv - dir * (float(i) * step_scale);
        sum += texture(tex, clamp(sample_uv, 0.0, 1.0));
    }
    vec4 blurred = sum / float(SAMPLES);

    // 2. Chromatic Aberration on edge pixels
    float ca = chromatic_amount * dist * 0.035;
    float r = texture(tex, clamp(uv + dir * ca, 0.0, 1.0)).r;
    float g = blurred.g;
    float b = texture(tex, clamp(uv - dir * ca, 0.0, 1.0)).b;
    vec3 col = mix(blurred.rgb, vec3(r, g, b), clamp(chromatic_amount * 1.5, 0.0, 1.0));

    // 3. Vignette (Edge Darkening)
    float vig = smoothstep(0.4, 0.95, dist);
    col = mix(col, col * (1.0 - vignette_intensity * 0.8), vig);

    // 4. Boundary Flash / Edge Pulse (White glow around periphery on threshold crossing)
    float flash_edge = smoothstep(0.35, 0.9, dist) * flash_intensity;
    col = mix(col, vec3(1.0, 0.95, 0.9), clamp(flash_edge, 0.0, 0.85));

    fragColor = vec4(col, 1.0);
}
""",
    default_input=dict(
        blur_intensity=0.0,
        chromatic_amount=0.0,
        vignette_intensity=0.0,
        flash_intensity=0.0,
        center=Vec2(0.5, 0.5),
    ),
)
