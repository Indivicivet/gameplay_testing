"""Distance Indicator Prototype.

A 3D third-person prototype testing distance-based visual indicators
and stepped response curves (Image 1) with motion/anime speed lines (Image 2).
"""

import math
from pathlib import Path
from ursina import (
    Ursina,
    Entity,
    Vec2,
    Vec3,
    camera,
    window,
    color,
    mouse,
    application,
    held_keys,
    Sky,
    DirectionalLight,
    AmbientLight,
)

from config import CONFIG
from math_curves import DistanceTracker
from procedural_textures import generate_all_textures
from fx_manager import FXManager, FXPreset
from characters import Arena, Player, Opponent
from hud import HUD


class DistanceIndicatorGame:
    """Core game application coordinating player, opponent, camera, and visual fx."""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.assets_dir = self.base_dir / "assets"

        # Generate texture assets
        generate_all_textures(self.assets_dir)

        # Ursina window configuration
        window.title = "Distance Indicator Prototype"
        window.borderless = False
        window.size = (1280, 720)
        window.color = color.rgb(18 / 255, 20 / 255, 26 / 255)

        # Lighting & environment
        Sky(color=color.rgb(24 / 255, 28 / 255, 38 / 255))
        DirectionalLight(y=6, z=-3, x=4, rotation=(45, -30, 0), shadows=False)
        AmbientLight(color=color.rgba(140 / 255, 150 / 255, 170 / 255, 1.0))

        # 3D Scene Entities
        self.arena = Arena(CONFIG.thresholds)
        self.player = Player(position=(0, 0, -2.5))
        self.opponent = Opponent(position=(0, 0, 0))

        # Camera control parameters
        self.camera_yaw = 0.0
        self.camera_pitch = 18.0
        self.cam_modes = ["3rd Person Follow", "Over-The-Shoulder", "1st Person"]
        self.cam_mode_idx = 0

        # Subsystems
        self.distance_tracker = DistanceTracker(
            thresholds=CONFIG.thresholds,
            pulse_duration=CONFIG.cross_pulse_duration,
        )
        self.fx_manager = FXManager(self.assets_dir)
        self.hud = HUD(self.assets_dir)

        # Lock mouse for camera control
        mouse.locked = True

    def reset_positions(self):
        """Resets player and opponent to default testing positions."""
        self.player.position = Vec3(0, 0, -2.5)
        self.player.rotation_y = 0
        self.opponent.position = Vec3(0, 0, 0)
        self.opponent.rotation_y = 180
        self.camera_yaw = 0.0
        self.camera_pitch = 18.0

    def update_camera(self, dt: float):
        """Updates camera position and orientation based on selected camera mode."""
        # Mouse look
        if mouse.locked:
            self.camera_yaw += mouse.velocity[0] * 70.0
            self.camera_pitch = max(
                -25.0, min(65.0, self.camera_pitch - mouse.velocity[1] * 70.0)
            )

        rad_yaw = math.radians(self.camera_yaw)
        rad_pitch = math.radians(self.camera_pitch)

        if self.cam_mode_idx == 0:
            # 3rd Person Follow Camera
            cam_dist = 4.2
            cam_height = 1.9
            offset = Vec3(
                -math.sin(rad_yaw) * math.cos(rad_pitch) * cam_dist,
                math.sin(rad_pitch) * cam_dist + cam_height,
                -math.cos(rad_yaw) * math.cos(rad_pitch) * cam_dist,
            )
            target_pos = self.player.position + offset
            camera.position += (target_pos - camera.position) * min(1.0, dt * 15.0)
            look_target = self.player.position + Vec3(0, 1.25, 0)
            camera.look_at(look_target)

        elif self.cam_mode_idx == 1:
            # Over-The-Shoulder Camera
            cam_dist = 2.4
            shoulder_offset = 0.55
            cam_height = 1.6
            right_vec = Vec3(math.cos(rad_yaw), 0, -math.sin(rad_yaw))
            offset = (
                Vec3(
                    -math.sin(rad_yaw) * math.cos(rad_pitch) * cam_dist,
                    math.sin(rad_pitch) * cam_dist + cam_height,
                    -math.cos(rad_yaw) * math.cos(rad_pitch) * cam_dist,
                )
                + right_vec * shoulder_offset
            )
            target_pos = self.player.position + offset
            camera.position += (target_pos - camera.position) * min(1.0, dt * 18.0)
            look_target = self.opponent.position + Vec3(0, 1.3, 0)
            camera.look_at(look_target)

        elif self.cam_mode_idx == 2:
            # 1st Person Camera
            camera.position = self.player.position + Vec3(0, 1.65, 0)
            camera.rotation_y = self.camera_yaw
            camera.rotation_x = self.camera_pitch

    def input(self, key):
        """Processes key presses."""
        # Preset selection (1-5)
        if key == "1":
            self.fx_manager.set_preset(FXPreset.SPRINT_BLUR)
        elif key == "2":
            self.fx_manager.set_preset(FXPreset.MANGA_LINES)
        elif key == "3":
            self.fx_manager.set_preset(FXPreset.COMBAT_VIGNETTE)
        elif key == "4":
            self.fx_manager.set_preset(FXPreset.WHITE_RUSH)
        elif key == "5":
            self.fx_manager.set_preset(FXPreset.HYBRID_FULL)

        # Toggle opponent milling / idle / follow
        elif key == "m":
            self.opponent.toggle_state()

        # Cycle camera mode
        elif key == "c":
            self.cam_mode_idx = (self.cam_mode_idx + 1) % len(self.cam_modes)

        # Adjust ZOOM_CONST
        elif key == "[":
            self.fx_manager.zoom_const = max(0.0, self.fx_manager.zoom_const - 2.0)
        elif key == "]":
            self.fx_manager.zoom_const = min(40.0, self.fx_manager.zoom_const + 2.0)

        # Reset positions
        elif key == "r":
            self.reset_positions()

        # Mouse toggle / exit
        elif key == "escape":
            mouse.locked = not mouse.locked

    def update(self, dt: float):
        """Main game loop update tick."""
        # 1. Update Entities
        self.player.update_movement(dt, self.camera_yaw)
        self.opponent.update_ai(dt, self.player.position)
        self.arena.update_rings_position(self.opponent.position)

        # 2. Update Camera
        self.update_camera(dt)

        # 3. Calculate 3D Distance
        diff = self.player.position - self.opponent.position
        distance = diff.length()

        # 4. Compute Distance Indicator Response & Crossing Pulse
        steady_fx, zone, pulse = self.distance_tracker.update(distance, dt)

        # 5. Determine screen UV of opponent for directional blur centering
        center_uv = Vec2(0.5, 0.5)

        # 6. Update Visual Effects (FOV, Shaders, Speed Lines, Vignette)
        self.fx_manager.update(
            steady_fx=steady_fx,
            zone=zone,
            cross_pulse=pulse,
            dt=dt,
            center_uv=center_uv,
        )

        # 7. Update HUD
        self.hud.update_hud(
            distance=distance,
            steady_fx=steady_fx,
            zone=zone,
            preset_id=self.fx_manager.preset,
            zoom_const=self.fx_manager.zoom_const,
            opponent_state=self.opponent.state,
            cam_mode=self.cam_modes[self.cam_mode_idx],
        )


def main():
    app = Ursina()
    game = DistanceIndicatorGame()

    def update():
        from ursina import time

        game.update(time.dt)

    def input(key):
        game.input(key)

    app.run()


if __name__ == "__main__":
    main()
