"""In-memory procedural texture generation for distance indicators.

Generates manga speed lines (Image 2 style) directly into memory at startup.
No disk file generation or committed image assets needed (~120ms total).
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
    seed: int = 42,
) -> Image.Image:
    """Generates an action speed-lines PIL Image matching Image 2 in memory."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size / 2.0

    rng = np.random.RandomState(seed)

    for i in range(num_lines):
        angle = (i / float(num_lines)) * 2.0 * math.pi + rng.uniform(-0.02, 0.02)
        inner_r = size * (inner_radius_ratio + rng.uniform(-0.06, 0.08))
        outer_r = size * 0.98

        x1 = center + inner_r * math.cos(angle)
        y1 = center + inner_r * math.sin(angle)

        perp = angle + math.pi / 2.0
        width = rng.uniform(3.5, 11.5)

        x2_base = center + outer_r * math.cos(angle)
        y2_base = center + outer_r * math.sin(angle)

        p1 = (x1, y1)
        p2 = (x2_base + math.cos(perp) * width, y2_base + math.sin(perp) * width)
        p3 = (x2_base - math.cos(perp) * width, y2_base - math.sin(perp) * width)

        alpha = int(line_color[3] * rng.uniform(0.75, 1.0))
        color = (line_color[0], line_color[1], line_color[2], alpha)
        draw.polygon([p1, p2, p3], fill=color)

    return img


def generate_in_memory_textures() -> dict:
    """Creates in-memory Ursina Textures for all visual presets (~100-150ms)."""
    img_black = create_speed_lines_image(
        line_color=(6, 8, 12, 255),
        num_lines=230,
        inner_radius_ratio=0.26,
        seed=101,
    )
    img_white = create_speed_lines_image(
        line_color=(255, 255, 255, 235),
        num_lines=200,
        inner_radius_ratio=0.28,
        seed=202,
    )
    img_dense = create_speed_lines_image(
        line_color=(8, 10, 16, 255),
        num_lines=300,
        inner_radius_ratio=0.20,
        seed=303,
    )

    return {
        "black": Texture(img_black),
        "white": Texture(img_white),
        "dense": Texture(img_dense),
    }
