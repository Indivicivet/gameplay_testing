"""Procedural texture generation for distance indicator visual effects.

Generates manga speed lines (Image 2 style), radial masks, and HUD curve graphics.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np


def generate_speed_lines(
    output_path: Path,
    line_color: tuple = (10, 10, 15, 235),
    num_lines: int = 180,
    size: int = 1024,
    inner_radius_ratio: float = 0.28,
    seed: int = 42,
) -> Path:
    """Generates an action speed-lines texture matching Image 2 with transparent center."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size / 2.0

    rng = np.random.RandomState(seed)

    for i in range(num_lines):
        # Slightly jittered angle around 360 degrees
        angle = (i / float(num_lines)) * 2.0 * math.pi + rng.uniform(-0.02, 0.02)
        inner_r = size * (inner_radius_ratio + rng.uniform(-0.06, 0.08))
        outer_r = size * 0.95

        x1 = center + inner_r * math.cos(angle)
        y1 = center + inner_r * math.sin(angle)

        perp = angle + math.pi / 2.0
        width = rng.uniform(2.5, 8.5)

        x2_base = center + outer_r * math.cos(angle)
        y2_base = center + outer_r * math.sin(angle)

        p1 = (x1, y1)
        p2 = (x2_base + math.cos(perp) * width, y2_base + math.sin(perp) * width)
        p3 = (x2_base - math.cos(perp) * width, y2_base - math.sin(perp) * width)

        # Alpha variation for organic depth
        alpha = int(line_color[3] * rng.uniform(0.7, 1.0))
        color = (line_color[0], line_color[1], line_color[2], alpha)
        draw.polygon([p1, p2, p3], fill=color)

    img.save(output_path, "PNG")
    return output_path


def generate_all_textures(assets_dir: Path) -> dict:
    """Generates all required procedural textures if not already cached."""
    assets_dir = Path(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    black_lines_path = assets_dir / "speed_lines_black.png"
    if not black_lines_path.exists():
        generate_speed_lines(
            black_lines_path,
            line_color=(12, 14, 18, 240),
            num_lines=210,
            inner_radius_ratio=0.26,
            seed=101,
        )

    white_lines_path = assets_dir / "speed_lines_white.png"
    if not white_lines_path.exists():
        generate_speed_lines(
            white_lines_path,
            line_color=(255, 255, 255, 220),
            num_lines=180,
            inner_radius_ratio=0.28,
            seed=202,
        )

    dense_lines_path = assets_dir / "speed_lines_dense.png"
    if not dense_lines_path.exists():
        generate_speed_lines(
            dense_lines_path,
            line_color=(15, 10, 20, 250),
            num_lines=280,
            inner_radius_ratio=0.20,
            seed=303,
        )

    return {
        "black": black_lines_path,
        "white": white_lines_path,
        "dense": dense_lines_path,
    }


if __name__ == "__main__":
    generate_all_textures(Path(__file__).parent / "assets")
    print("Textures generated successfully!")
