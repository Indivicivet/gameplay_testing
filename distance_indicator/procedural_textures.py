"""In-memory procedural texture generation for distance indicators.

Generates manga speed lines (Image 2 style) across 4 distinct distance tiers
directly into memory at startup (~40ms total).
"""

import math
from PIL import Image, ImageDraw
import numpy as np
from ursina import Texture


def create_speed_lines_image(
    line_color: tuple = (6, 8, 12, 255),
    num_lines: int = 220,
    size: int = 1024,
    inner_radius_ratio: float = 0.28,
    min_width: float = 3.5,
    max_width: float = 11.5,
    seed: int = 42,
) -> Image.Image:
    """Generates an action speed-lines PIL Image matching Image 2 in memory."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size / 2.0

    rng = np.random.RandomState(seed)

    for i in range(num_lines):
        angle = (i / float(num_lines)) * 2.0 * math.pi + rng.uniform(-0.02, 0.02)
        inner_r = size * (inner_radius_ratio + rng.uniform(-0.04, 0.06))
        outer_r = size * 0.98

        x1 = center + inner_r * math.cos(angle)
        y1 = center + inner_r * math.sin(angle)

        perp = angle + math.pi / 2.0
        width = rng.uniform(min_width, max_width)

        x2_base = center + outer_r * math.cos(angle)
        y2_base = center + outer_r * math.sin(angle)

        p1 = (x1, y1)
        p2 = (x2_base + math.cos(perp) * width, y2_base + math.sin(perp) * width)
        p3 = (x2_base - math.cos(perp) * width, y2_base - math.sin(perp) * width)

        alpha = int(line_color[3] * rng.uniform(0.75, 1.0))
        color = (line_color[0], line_color[1], line_color[2], alpha)
        draw.polygon([p1, p2, p3], fill=color)

    return img


def make_white_rush_variant(img: Image.Image) -> Image.Image:
    """Instantly converts black manga line texture to crisp white rush line texture via NumPy."""
    arr = np.array(img)
    arr[:, :, :3] = 255
    return Image.fromarray(arr)


def generate_in_memory_textures() -> dict:
    """Creates in-memory Ursina Textures for 4 distinct distance tiers (~40-60ms)."""
    # Tier 1 (Alert: 2.5m - 2.0m): Visible corner speed marks framing outer screen
    img_t1_black = create_speed_lines_image(
        line_color=(6, 8, 12, 240),
        num_lines=140,
        inner_radius_ratio=0.28,
        min_width=3.0,
        max_width=8.5,
        seed=101,
    )
    # Tier 2 (Threat: 2.0m - 1.5m): Medium speed lines reaching into edges and corners
    img_t2_black = create_speed_lines_image(
        line_color=(6, 8, 12, 248),
        num_lines=210,
        inner_radius_ratio=0.22,
        min_width=3.5,
        max_width=10.0,
        seed=202,
    )
    # Tier 3 (Danger: 1.5m - 1.0m): Dense manga lines penetrating towards character center
    img_t3_black = create_speed_lines_image(
        line_color=(6, 8, 12, 255),
        num_lines=300,
        inner_radius_ratio=0.16,
        min_width=4.5,
        max_width=12.5,
        seed=303,
    )
    # Tier 4 (Clinch: < 1.0m): Full storm lines, tight focus tunnel on combatants
    img_t4_black = create_speed_lines_image(
        line_color=(6, 8, 12, 255),
        num_lines=400,
        inner_radius_ratio=0.10,
        min_width=5.5,
        max_width=15.0,
        seed=404,
    )

    # White rush variants
    img_t1_white = make_white_rush_variant(img_t1_black)
    img_t2_white = make_white_rush_variant(img_t2_black)
    img_t3_white = make_white_rush_variant(img_t3_black)
    img_t4_white = make_white_rush_variant(img_t4_black)

    tex_t1_b = Texture(img_t1_black)
    tex_t2_b = Texture(img_t2_black)
    tex_t3_b = Texture(img_t3_black)
    tex_t4_b = Texture(img_t4_black)

    tex_t1_w = Texture(img_t1_white)
    tex_t2_w = Texture(img_t2_white)
    tex_t3_w = Texture(img_t3_white)
    tex_t4_w = Texture(img_t4_white)

    return {
        "tier1_black": tex_t1_b,
        "tier2_black": tex_t2_b,
        "tier3_black": tex_t3_b,
        "tier4_black": tex_t4_b,
        "tier1_white": tex_t1_w,
        "tier2_white": tex_t2_w,
        "tier3_white": tex_t3_w,
        "tier4_white": tex_t4_w,
        # Aliases for convenience
        "black": tex_t2_b,
        "dense": tex_t4_b,
        "white": tex_t4_w,
    }
