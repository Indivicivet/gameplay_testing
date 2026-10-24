"""Utility to capture high-resolution verification screenshots across distance zones."""

import sys
from pathlib import Path

# Add distance_indicator directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from panda3d.core import Filename
from ursina import Vec3, window, application, invoke
from main import game, app

# Ensure directory exists
out_dir = Path(__file__).parent / "screenshots"
out_dir.mkdir(exist_ok=True)

# Test cases: (name, player_pos, opponent_pos, preset_id, yaw, show_rings)
scenarios = [
    (
        "01_safe_zone_rings_on.png",
        Vec3(0, 0, -3.1),
        Vec3(0, 0, 0),
        5,  # Hybrid
        0.0,
        True,
    ),
    (
        "02_zone1_alert_manga.png",
        Vec3(0, 0, -2.25),
        Vec3(0, 0, 0),
        2,  # Manga Lines Tier 1
        0.0,
        True,
    ),
    (
        "03_zone2_threat_manga.png",
        Vec3(0, 0, -1.75),
        Vec3(0, 0, 0),
        2,  # Manga Lines Tier 2
        0.0,
        True,
    ),
    (
        "04_zone3_danger_manga.png",
        Vec3(0, 0, -1.25),
        Vec3(0, 0, 0),
        2,  # Manga Lines Tier 3
        0.0,
        True,
    ),
    (
        "05_zone4_clinch_manga.png",
        Vec3(0, 0, -0.85),
        Vec3(0, 0, 0),
        2,  # Manga Lines Tier 4
        0.0,
        True,
    ),
    (
        "06_zone4_pure_optical_blur.png",
        Vec3(0, 0, -0.85),
        Vec3(0, 0, 0),
        1,  # Sprint / Radial Blur (pure optical, no chromatic aberration)
        0.0,
        True,
    ),
    (
        "07_zone4_rings_hidden_spoiler_toggle.png",
        Vec3(0, 0, -0.85),
        Vec3(0, 0, 0),
        5,  # Hybrid Full
        0.0,
        False,  # Ground spoiler rings hidden
    ),
]


def capture_all():
    # Warm up Ursina / Panda3D render pipeline
    for _ in range(10):
        game.update_game(0.016)
        application.base.graphicsEngine.renderFrame()

    for filename, player_p, opp_p, preset, yaw, show_rings in scenarios:
        game.player.position = player_p
        game.opponent.position = opp_p
        game.camera_yaw = yaw
        game.fx_manager.set_preset(preset)
        game.arena.show_rings = show_rings
        for ring, _ in game.arena.rings:
            ring.enabled = show_rings

        # Step multiple ticks to allow smooth dampening and shaders to settle
        for _ in range(35):
            game.update_game(0.016)
            application.base.graphicsEngine.renderFrame()

        application.base.graphicsEngine.renderFrame()
        filepath = out_dir / filename
        ok = application.base.win.saveScreenshot(Filename.fromOsSpecific(str(filepath)))
        print(f"Captured ({ok}): {filepath}")

    print("All captures completed successfully.")
    sys.exit(0)


# Run capture once Ursina is loaded
invoke(capture_all, delay=0.1)
app.run()
