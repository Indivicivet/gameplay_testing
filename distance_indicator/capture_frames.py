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

# Test cases: (name, player_pos, opponent_pos, preset_id, yaw)
scenarios = [
    (
        "01_safe_light_arena.png",
        Vec3(0, 0, -3.2),
        Vec3(0, 0, 0),
        2,  # Manga Lines
        0.0,
    ),
    (
        "02_threat_light_arena.png",
        Vec3(0, 0, -1.9),
        Vec3(0, 0, 0),
        2,  # Manga Lines
        0.0,
    ),
    (
        "03_clinch_high_contrast_manga.png",
        Vec3(0, 0, -0.95),
        Vec3(0, 0, 0),
        2,  # Manga Lines
        0.0,
    ),
    (
        "04_clinch_hybrid_all_fx.png",
        Vec3(0, 0, -0.95),
        Vec3(0, 0, 0),
        5,  # Hybrid Full
        0.0,
    ),
]


def capture_all():
    # Warm up Ursina / Panda3D render pipeline
    for _ in range(10):
        game.update_game(0.016)
        application.base.graphicsEngine.renderFrame()

    for filename, player_p, opp_p, preset, yaw in scenarios:
        game.player.position = player_p
        game.opponent.position = opp_p
        game.camera_yaw = yaw
        game.fx_manager.set_preset(preset)

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
