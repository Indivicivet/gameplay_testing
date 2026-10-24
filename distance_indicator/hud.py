"""In-game HUD for distance diagnostics and interactive control panel.

Renders real-time distance measurements, active preset info, key controls,
and the live f(d) curve graph matching Image 1 with an animated tracking dot.
"""

from pathlib import Path
from PIL import Image, ImageDraw
from ursina import (
    Entity,
    Text,
    camera,
    color,
    Vec2,
    Texture,
)
from math_curves import calculate_fx
from config import CONFIG
from fx_manager import PRESET_NAMES


def create_curve_texture(width: int = 512, height: int = 256) -> Texture:
    """Renders the bumpy f(d) transfer function curve directly into an in-memory Texture."""
    img = Image.new("RGBA", (width, height), (16, 20, 28, 225))
    draw = ImageDraw.Draw(img)

    margin_l = 50
    margin_r = 30
    margin_t = 35
    margin_b = 45
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    d_min = 0.6
    d_max = 3.0

    # Draw border / background grid
    draw.rectangle(
        [(margin_l, margin_t), (margin_l + plot_w, margin_t + plot_h)],
        outline=(60, 75, 95, 255),
        width=1,
    )

    # Threshold guidelines matching center-to-center distance (1.0m, 1.5m, 2.0m, 2.5m)
    threshold_colors = {
        2.5: (80, 160, 255, 180),
        2.0: (240, 210, 60, 180),
        1.5: (255, 130, 40, 180),
        1.0: (255, 60, 70, 220),
    }

    for thresh in CONFIG.thresholds:
        tx = margin_l + int(((thresh - d_min) / (d_max - d_min)) * plot_w)
        col = threshold_colors.get(thresh, (100, 120, 150, 160))
        for y in range(margin_t, margin_t + plot_h, 8):
            draw.line([(tx, y), (tx, min(y + 4, margin_t + plot_h))], fill=col, width=1)
        draw.text(
            (tx - 12, margin_t + plot_h + 8), f"{thresh}m", fill=(180, 195, 215, 255)
        )

    # Curve f(d)
    points = []
    num_samples = 200
    for i in range(num_samples + 1):
        d = d_min + (i / float(num_samples)) * (d_max - d_min)
        fx, _ = calculate_fx(d)
        px = margin_l + int(((d - d_min) / (d_max - d_min)) * plot_w)
        py = margin_t + plot_h - int(fx * plot_h)
        points.append((px, py))

    draw.line(points, fill=(60, 230, 255, 255), width=3)

    # Title & axis labels
    draw.text(
        (margin_l + 8, margin_t - 24),
        "f(d) Response Curve (Image 1)",
        fill=(240, 245, 255, 255),
    )
    draw.text((margin_l - 35, margin_t - 8), "fx 1.0", fill=(140, 160, 180, 255))
    draw.text(
        (margin_l - 35, margin_t + plot_h - 10), "fx 0.0", fill=(140, 160, 180, 255)
    )

    return Texture(img)


class HUD(Entity):
    """Manages all screen-space text, diagnostic graphs, and status readouts."""

    def __init__(self, curve_texture: Texture = None):
        super().__init__(parent=camera.ui, z=-0.2)

        # Distance & Zone Readout Banner (Top Center with sleek high-contrast backing card)
        self.banner_bg = Entity(
            parent=self,
            model="quad",
            scale=(0.64, 0.15),
            position=(0, 0.42),
            color=color.rgba(12 / 255, 16 / 255, 24 / 255, 0.88),
            z=0.02,
        )
        self.dist_text = Text(
            parent=self,
            text="Distance: -- m",
            position=(0, 0.455),
            origin=(0, 0),
            scale=1.5,
            color=color.white,
            z=-0.05,
        )
        self.zone_text = Text(
            parent=self,
            text="Zone: Safe Range",
            position=(0, 0.385),
            origin=(0, 0),
            scale=0.95,
            color=color.rgb(160 / 255, 200 / 255, 255 / 255),
            z=-0.05,
        )

        # Graph Panel (Top Right)
        if curve_texture is None:
            curve_texture = create_curve_texture()

        self.graph_panel = Entity(
            parent=self,
            model="quad",
            texture=curve_texture,
            scale=(0.42, 0.21),
            position=(0.65, 0.35),
            color=color.white,
            z=0.0,
        )

        # Animated cursor on the curve graph
        self.graph_cursor = Entity(
            parent=self.graph_panel,
            model="circle",
            scale=(0.04, 0.08),
            color=color.rgb(1.0, 40 / 255, 50 / 255),
            z=-0.1,
        )

        # Status & Controls Panel (Bottom Left with high-contrast backing card)
        self.info_bg = Entity(
            parent=self,
            model="quad",
            scale=(0.56, 0.18),
            position=(-0.59, -0.37),
            color=color.rgba(12 / 255, 16 / 255, 24 / 255, 0.88),
            z=0.02,
        )
        self.info_text = Text(
            parent=self,
            text="",
            position=(-0.84, -0.44),
            origin=(-0.5, -0.5),
            scale=0.9,
            color=color.rgb(220 / 255, 230 / 255, 245 / 255),
            z=-0.05,
        )

        # Help overlay (Bottom Right with high-contrast backing card)
        self.help_bg = Entity(
            parent=self,
            model="quad",
            scale=(0.48, 0.30),
            position=(0.64, -0.33),
            color=color.rgba(12 / 255, 16 / 255, 24 / 255, 0.88),
            z=0.02,
        )
        self.help_text = Text(
            parent=self,
            text=(
                "Controls:\n"
                "  [W,A,S,D] Walk slowly\n"
                "  [Mouse Look / Q, E] Orbit Camera\n"
                "  [Left Click] Capture Mouse | [ESC] Free\n"
                "  [1-5] Switch FX Preset\n"
                "  [M] Opponent AI (Milling/Idle/Follow)\n"
                "  [C] Camera View (3rd/Shoulder/1st)\n"
                "  [ [ / ] ] Adjust ZOOM_CONST (FoV Mod)\n"
                "  [R] Reset Positions"
            ),
            position=(0.85, -0.46),
            origin=(0.5, -0.5),
            scale=0.75,
            color=color.rgb(195 / 255, 210 / 255, 230 / 255),
            z=-0.05,
        )

    def update_hud(
        self,
        distance: float,
        steady_fx: float,
        zone: int,
        preset_id: int,
        zoom_const: float,
        opponent_state: str,
        cam_mode: str,
        current_fov: float = 62.0,
    ):
        """Updates text readouts and graph cursor position."""
        # 1. Distance & Zone text
        zone_name = (
            CONFIG.threshold_names[zone - 1]
            if 0 < zone <= len(CONFIG.threshold_names)
            else "Safe / Out of Range"
        )
        self.dist_text.text = f"{distance:4.2f} m"

        # Color-code distance based on zone
        if zone == 4:
            self.dist_text.color = color.rgb(1.0, 60 / 255, 60 / 255)
            self.zone_text.color = color.rgb(1.0, 120 / 255, 120 / 255)
        elif zone == 3:
            self.dist_text.color = color.rgb(1.0, 140 / 255, 40 / 255)
            self.zone_text.color = color.rgb(1.0, 180 / 255, 80 / 255)
        elif zone == 2:
            self.dist_text.color = color.rgb(240 / 255, 220 / 255, 50 / 255)
            self.zone_text.color = color.rgb(250 / 255, 235 / 255, 120 / 255)
        elif zone == 1:
            self.dist_text.color = color.rgb(90 / 255, 180 / 255, 1.0)
            self.zone_text.color = color.rgb(140 / 255, 210 / 255, 1.0)
        else:
            self.dist_text.color = color.rgb(200 / 255, 220 / 255, 240 / 255)
            self.zone_text.color = color.rgb(140 / 255, 160 / 255, 180 / 255)

        self.zone_text.text = (
            f"Zone {zone}: {zone_name} (FX Intensity: {int(steady_fx * 100)}%)"
        )

        # 2. Update Graph Cursor
        # Map d in [0.6, 3.0] to cursor local x in [-0.5, 0.5] with margins
        d_min = 0.6
        d_max = 3.0
        plot_norm_x = (distance - d_min) / (d_max - d_min)
        plot_norm_x = max(0.0, min(1.0, plot_norm_x))
        # Account for margin_l (50/512 ~ 0.097) and margin_r (30/512 ~ 0.058)
        local_x = -0.5 + 0.098 + plot_norm_x * (1.0 - 0.098 - 0.058)
        # Margin_b (45/256 ~ 0.175) and margin_t (35/256 ~ 0.136)
        local_y = -0.5 + 0.175 + steady_fx * (1.0 - 0.175 - 0.136)
        self.graph_cursor.position = Vec2(local_x, local_y)

        # 3. Status info
        preset_label = PRESET_NAMES.get(preset_id, "Unknown")
        self.info_text.text = (
            f"Active FX Preset:  {preset_label}\n"
            f"Field of View:     {current_fov:4.1f}° (Mod: {zoom_const:+.1f}°)\n"
            f"Opponent Mode:     {opponent_state}\n"
            f"Camera Mode:       {cam_mode}"
        )
