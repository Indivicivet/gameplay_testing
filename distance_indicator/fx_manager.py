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

        self.textures = textures
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

        self.lines_overlay.texture = self.textures["tier1_black"]

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
        """Updates all visual effects across 4 consistent distance tiers."""
        # 1. Field of View Modulation across distance zones (tightens as you get closer)
        # - Stepped tightening linked to the bumpy transfer function f(d)
        # - Punchy inward zoom kick when crossing into a closer tier
        # - Subtle breathing cycle when in the infighting clinch zone
        step_zoom = self.zoom_const * steady_fx
        kick_sign = -1.0 if self.zoom_const <= 0 else 1.0
        transition_kick = kick_sign * cross_pulse * 5.0
        breathing = 0.8 * math.sin(time.time() * 4.0) if zone == 4 else 0.0
        target_fov = self.base_fov + step_zoom + transition_kick + breathing
        self.fov_smooth += (target_fov - self.fov_smooth) * min(1.0, dt * 16.0)
        camera.fov = self.fov_smooth

        # 2. Consistent 4-Tier Visual Progression
        tier = max(1, min(4, zone)) if zone > 0 else 1
        tier_alpha_levels = {0: 0.0, 1: 0.55, 2: 0.75, 3: 0.90, 4: 1.0}
        tier_blur_levels = {0: 0.0, 1: 0.25, 2: 0.50, 3: 0.75, 4: 1.0}
        tier_vig_levels = {0: 0.0, 1: 0.20, 2: 0.40, 3: 0.60, 4: 0.80}

        base_alpha = tier_alpha_levels.get(zone, 0.0)
        base_blur = tier_blur_levels.get(zone, 0.0)
        base_vig = tier_vig_levels.get(zone, 0.0)

        blur = 0.0
        vignette = 0.0
        lines_alpha = 0.0
        use_white = False

        if self.preset == FXPreset.SPRINT_BLUR:
            blur = base_blur * 1.0
            vignette = base_vig * 0.75
            lines_alpha = 0.0

        elif self.preset == FXPreset.MANGA_LINES:
            blur = base_blur * 0.25
            vignette = base_vig * 0.35
            lines_alpha = base_alpha * 1.0

        elif self.preset == FXPreset.COMBAT_VIGNETTE:
            blur = base_blur * 0.85
            vignette = min(0.95, base_vig * 1.25)
            lines_alpha = base_alpha * 0.45

        elif self.preset == FXPreset.WHITE_RUSH:
            blur = base_blur * 0.85
            vignette = 0.0
            lines_alpha = base_alpha * 0.95
            use_white = True

        elif self.preset == FXPreset.HYBRID_FULL:
            blur = base_blur * 0.80
            vignette = base_vig * 0.70
            lines_alpha = base_alpha * 0.90

        # Update speed lines texture tier matching active zone (tier 1..4)
        variant = "white" if use_white else "black"
        tex_key = f"tier{tier}_{variant}"
        if tex_key in self.textures:
            self.lines_overlay.texture = self.textures[tex_key]

        # 3. Update GLSL shader uniforms (pure optical radial zoom blur, zero chromatic fringing)
        camera.set_shader_input("blur_intensity", blur)
        camera.set_shader_input("vignette_intensity", vignette)
        camera.set_shader_input("center", center_uv)

        # 4. Update speed-lines overlay
        clamped_alpha = max(0.0, min(1.0, lines_alpha))
        self.lines_overlay.color = color.rgba(1, 1, 1, clamped_alpha)

        # Dynamic anime line breathing/jitter at high intensity
        if clamped_alpha > 0.05:
            self.lines_overlay.rotation_z += dt * (12.0 + steady_fx * 30.0)
            # Center aperture tightens slightly as you get deeper into danger zones
            target_scale = 2.3 * (1.0 + (1.0 - steady_fx) * 0.20)
            self.lines_overlay.scale = target_scale
