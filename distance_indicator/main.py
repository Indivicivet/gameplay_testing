"""Distance Indicator Prototype.

A 3D third-person prototype testing distance-based visual indicators
and stepped response curves (Image 1) with motion/anime speed lines (Image 2).
"""

import math
from ursina import (
    Ursina,
    Entity,
    Vec2,
    Vec3,
    camera,
    window,
    color,
    mouse,
    time,
    held_keys,
    Sky,
    DirectionalLight,
    AmbientLight,
)

from config import CONFIG
from math_curves import DistanceTracker
from fx_manager import FXManager, FXPreset
from characters import Arena, Player, Opponent
from hud import HUD


class DistanceIndicatorGame(Entity):
    """Core game application coordinating player, opponent, camera, and visual fx.

    Inherits from Entity so Ursina's engine automatically calls update() every tick.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Lighting & environment (clean light high-contrast aesthetic)
        Sky(color=color.rgb(0.85, 0.88, 0.92))
        DirectionalLight(y=8, z=-5, x=5, rotation=(50, -35, 0), shadows=False)
        AmbientLight(color=color.rgba(0.68, 0.70, 0.74, 1.0))

        # 3D Scene Entities
        self.arena = Arena(CONFIG.thresholds)
        self.player = Player(position=(0, 0, -3.5))
        self.opponent = Opponent(position=(0, 0, 0))

        # Standard FPS/TPS Camera Boom Rig (clean spherical orbit with zero roll/jitter)
        self.camera_pivot = Entity(name="camera_pivot")
        camera.parent = self.camera_pivot
        self.cam_distance = 3.6
        self.camera_yaw = 0.0
        self.camera_pitch = 14.0
        self.mouse_sensitivity = 40.0
        self.cam_modes = ["3rd Person Follow", "Over-The-Shoulder", "1st Person"]
        self.cam_mode_idx = 0

        # Subsystems (Procedural textures generated directly in memory on launch ~120ms)
        self.distance_tracker = DistanceTracker(
            thresholds=CONFIG.thresholds,
            pulse_duration=CONFIG.cross_pulse_duration,
        )
        self.fx_manager = FXManager()
        self.hud = HUD()

        # Capture mouse for camera look
        mouse.locked = True

        # Immediately prime camera and first frame state
        self.update_camera(0.016)
        self.update_game(0.016)

    def reset_positions(self):
        """Resets player and opponent to default testing positions."""
        self.player.position = Vec3(0, 0, -3.5)
        self.player.rotation_y = 0
        self.opponent.position = Vec3(0, 0, 0)
        self.opponent.rotation_y = 180
        self.camera_yaw = 0.0
        self.camera_pitch = 14.0
        self.cam_distance = 3.6
        self.update_camera(0.016)

    def update_camera(self, dt: float):
        """Updates camera position and orientation using a standard FPS/TPS boom rig."""
        # 1. Pivot smoothly anchors to player chest level
        self.camera_pivot.position = self.player.position + Vec3(0, 1.4, 0)

        # 2. Mouse Look (when locked or right-mouse dragging)
        if mouse.locked:
            dx = max(-0.25, min(0.25, mouse.velocity[0]))
            dy = max(-0.25, min(0.25, mouse.velocity[1]))
            self.camera_yaw += dx * self.mouse_sensitivity
            self.camera_pitch -= dy * self.mouse_sensitivity
            self.camera_pitch = max(-35.0, min(65.0, self.camera_pitch))
        elif held_keys["right mouse"]:
            dx = max(-0.25, min(0.25, mouse.velocity[0]))
            dy = max(-0.25, min(0.25, mouse.velocity[1]))
            self.camera_yaw += dx * (self.mouse_sensitivity * 1.5)
            self.camera_pitch -= dy * (self.mouse_sensitivity * 1.5)
            self.camera_pitch = max(-35.0, min(65.0, self.camera_pitch))

        # 3. Keyboard Orbit Fallback (Q / E keys)
        if held_keys["q"]:
            self.camera_yaw -= 80.0 * dt
        if held_keys["e"]:
            self.camera_yaw += 80.0 * dt

        # 4. Apply clean Euler rotations to the pivot
        self.camera_pivot.rotation_y = self.camera_yaw
        self.camera_pivot.rotation_x = self.camera_pitch
        self.camera_pivot.rotation_z = 0.0

        # 5. Position Camera relative to pivot boom
        if self.cam_mode_idx == 0:
            # Standard 3rd Person Follow Camera
            camera.position = Vec3(0, 0, -self.cam_distance)
            camera.rotation = Vec3(0, 0, 0)
        elif self.cam_mode_idx == 1:
            # Over-The-Shoulder Camera
            camera.position = Vec3(0.55, 0.1, -2.0)
            camera.rotation = Vec3(0, 0, 0)
        elif self.cam_mode_idx == 2:
            # 1st Person Camera
            camera.position = Vec3(0, 0.28, 0.1)
            camera.rotation = Vec3(0, 0, 0)

    def input(self, key):
        """Processes key presses and mouse clicks."""
        # Mouse capture click
        if key == "left mouse down" and not mouse.locked:
            mouse.locked = True

        # Mouse Wheel Camera Zoom
        elif key == "scroll up":
            self.cam_distance = max(1.5, self.cam_distance - 0.35)
        elif key == "scroll down":
            self.cam_distance = min(6.5, self.cam_distance + 0.35)

        # Preset selection (1-5)
        elif key == "1":
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

        # Toggle floor distance rings (spoilers)
        elif key == "z":
            self.arena.toggle_rings()

        # Cycle camera mode
        elif key == "c":
            self.cam_mode_idx = (self.cam_mode_idx + 1) % len(self.cam_modes)
            self.update_camera(0.016)

        # Adjust ZOOM_CONST (Field of View modulation)
        elif key == "[":
            self.fx_manager.zoom_const = max(-30.0, self.fx_manager.zoom_const - 4.0)
        elif key == "]":
            self.fx_manager.zoom_const = min(50.0, self.fx_manager.zoom_const + 4.0)

        # Reset positions
        elif key == "r":
            self.reset_positions()

        # Mouse toggle / exit
        elif key == "escape":
            mouse.locked = not mouse.locked

    def update(self):
        """Standard Ursina Entity update tick called automatically each frame."""
        self.update_game(time.dt)

    def update_game(self, dt: float):
        """Main game loop update tick."""
        # Clamp dt to prevent teleporting on frame stutter
        dt = min(0.05, max(0.001, dt))

        # 1. Update Entities
        strafe_mode = self.cam_mode_idx in (1, 2)
        self.player.update_movement(dt, self.camera_yaw, strafe_mode=strafe_mode)
        self.opponent.update_ai(dt, self.player.position)
        self.arena.update_rings_position(self.opponent.position)

        # 2. Update Camera
        self.update_camera(dt)

        # 3. Calculate 3D Distance
        diff = self.player.position - self.opponent.position
        distance = diff.length()

        # 4. Compute Distance Indicator Response & Crossing Pulse
        steady_fx, zone, pulse = self.distance_tracker.update(distance, dt)

        # 5. Determine screen UV center
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
            current_fov=camera.fov,
            rings_visible=self.arena.show_rings,
        )


# Global game instance and module-level Ursina hooks
app = Ursina(
    title="Distance Indicator Prototype",
    borderless=False,
    size=(1280, 720),
)
window.color = color.rgb(0.80, 0.82, 0.86)

game = DistanceIndicatorGame()


def update():
    """Top-level module update hook called by Ursina's main loop."""
    game.update_game(time.dt)


def input(key):
    """Top-level module input hook called by Ursina's input handler."""
    game.input(key)


if __name__ == "__main__":
    app.run()
