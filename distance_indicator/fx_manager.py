"""Visual effects coordinator for distance indicators.

Manages dynamic camera FOV, post-processing shader uniforms, speed lines overlay,
and presets.
"""

import math
from ursina import Entity, camera, Vec2, color, Texture, time
import shaders
from config import CONFIG
from procedural_textures import generate_in_memory_textures


class FXPreset:
    SPRINT_BLUR = 1
    MANGA_LINES = 2
    COMBAT_VIGNETTE = 3
    WHITE_RUSH = 4
    HYBRID_FULL = 5


PRESET_NAMES = {
    FXPreset.SPRINT_BLUR: "1: Sprint / Radial Blur",
    FXPreset.MANGA_LINES: "2: Manga Action Lines (Image 2)",
    FXPreset.COMBAT_VIGNETTE: "3: Combat Tunnel Vignette",
    FXPreset.WHITE_RUSH: "4: White Sprint Rush",
    FXPreset.HYBRID_FULL: "5: Full Hybrid (All FX)",
}


class FXManager:
    """Controls screen shaders, speed-line quads, and FOV transitions."""

    def __init__(self, textures: dict = None):
        if textures is None:
            textures = generate_in_memory_textures()

        self.preset = FXPreset.HYBRID_FULL
        self.zoom_const = CONFIG.zoom_const
        self.base_fov = CONFIG.base_fov
        self.fov_smooth = CONFIG.base_fov

        # Assign post-processing shader to Ursina camera
        camera.shader = shaders.POST_PROCESS_SHADER

        # Speed-lines UI Overlay
        # Oversized square quad so rotation never clips viewport corners
        self.lines_overlay = Entity(
            parent=camera.ui,
            model="quad",
            scale=(2.3, 2.3),
            color=color.rgba(1, 1, 1, 0),
            z=0.5,  # Behind HUD text (z <= 0), in front of 3D scene
        )

        self.texture_black = textures["black"]
        self.texture_white = textures["white"]
        self.texture_dense = textures["dense"]

        self.lines_overlay.texture = self.texture_black

    def set_preset(self, preset_id: int):
        """Switches active visual feedback preset."""
        if preset_id in PRESET_NAMES:
            self.preset = preset_id

    def update(
        self,
        steady_fx: float,
        zone: int,
        cross_pulse: float,
        dt: float,
        center_uv: Vec2 = Vec2(0.5, 0.5),
    ):
        """Updates all visual effects based on distance response curve."""
        # 1. Light Field of View Modulation across distance zones
        # - Stepped widening linked to the bumpy transfer function f(d)
        # - Clean +2.2 deg optical kick when stepping into a closer tier
        # - Subtle 0.5 deg breathing cycle when in the infighting clinch zone
        step_zoom = self.zoom_const * steady_fx
        transition_kick = cross_pulse * 2.2
        breathing = 0.5 * math.sin(time.time() * 3.5) if zone == 4 else 0.0
        target_fov = self.base_fov + step_zoom + transition_kick + breathing
        self.fov_smooth += (target_fov - self.fov_smooth) * min(1.0, dt * 14.0)
        camera.fov = self.fov_smooth

        # 2. Preset-specific visual parameter balancing (smooth transitions, zero screen flash)
        blur = 0.0
        chroma = 0.0
        vignette = 0.0
        lines_alpha = 0.0

        if self.preset == FXPreset.SPRINT_BLUR:
            blur = steady_fx * 0.95
            chroma = steady_fx * 0.8
            vignette = steady_fx * 0.35
            lines_alpha = 0.0
            self.lines_overlay.texture = self.texture_black

        elif self.preset == FXPreset.MANGA_LINES:
            blur = steady_fx * 0.2
            chroma = steady_fx * 0.2
            vignette = steady_fx * 0.2
            lines_alpha = steady_fx * 0.95
            self.lines_overlay.texture = (
                self.texture_dense if zone >= 3 else self.texture_black
            )

        elif self.preset == FXPreset.COMBAT_VIGNETTE:
            blur = steady_fx * 0.6
            chroma = steady_fx * 0.9
            vignette = steady_fx * 0.95
            lines_alpha = steady_fx * 0.25
            self.lines_overlay.texture = self.texture_black

        elif self.preset == FXPreset.WHITE_RUSH:
            blur = steady_fx * 0.8
            chroma = steady_fx * 0.5
            vignette = 0.0
            lines_alpha = steady_fx * 0.9
            self.lines_overlay.texture = self.texture_white

        elif self.preset == FXPreset.HYBRID_FULL:
            blur = steady_fx * 0.75
            chroma = steady_fx * 0.65
            vignette = steady_fx * 0.55
            lines_alpha = steady_fx * 0.85
            self.lines_overlay.texture = (
                self.texture_dense if zone >= 3 else self.texture_black
            )

        # 3. Update GLSL shader uniforms
        camera.set_shader_input("blur_intensity", blur)
        camera.set_shader_input("chromatic_amount", chroma)
        camera.set_shader_input("vignette_intensity", vignette)
        camera.set_shader_input("center", center_uv)

        # 4. Update speed-lines overlay
        clamped_alpha = max(0.0, min(1.0, lines_alpha))
        self.lines_overlay.color = color.rgba(1, 1, 1, clamped_alpha)

        # Dynamic anime line breathing/jitter at high intensity
        if clamped_alpha > 0.05:
            self.lines_overlay.rotation_z += dt * (12.0 + steady_fx * 30.0)
            # Center aperture tightens slightly as you get deeper into danger zones
            target_scale = 2.3 * (1.0 + (1.0 - steady_fx) * 0.25)
            self.lines_overlay.scale = target_scale
