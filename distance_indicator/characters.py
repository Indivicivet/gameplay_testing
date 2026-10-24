"""Player, Opponent, and Arena 3D entities for distance testing."""

import math
import random
from ursina import (
    Entity,
    Vec3,
    color,
    held_keys,
    mouse,
    time,
    destroy,
)
from config import CONFIG


class Arena(Entity):
    """Clean sparring grid floor with concentric distance rings around opponent."""

    def __init__(self, thresholds=None):
        super().__init__()
        if thresholds is None:
            thresholds = CONFIG.thresholds

        # Ground plane (clean, light sparring mat for maximum visual contrast)
        self.floor = Entity(
            model="plane",
            scale=(30, 1, 30),
            color=color.rgb(0.74, 0.77, 0.82),
            texture="white_cube",
            texture_scale=(30, 30),
            y=0,
        )

        # Pillars / bounding bounds for depth perception
        pillar_positions = [
            (-10, -10),
            (-10, 10),
            (10, -10),
            (10, 10),
            (0, 12),
            (0, -12),
        ]
        for px, pz in pillar_positions:
            Entity(
                model="cube",
                position=(px, 1.5, pz),
                scale=(0.4, 3, 0.4),
                color=color.rgb(0.32, 0.36, 0.44),
            )

        # Concentric distance rings on floor (rendered as flat circles)
        self.rings = []
        self.show_rings = True
        ring_colors = [
            color.rgba(0.12, 0.50, 0.95, 0.65),  # 2.5m Alert (Azure Blue)
            color.rgba(0.92, 0.70, 0.10, 0.72),  # 2.0m Threat (Amber Gold)
            color.rgba(0.98, 0.40, 0.08, 0.80),  # 1.5m Danger (Vivid Orange)
            color.rgba(0.95, 0.12, 0.16, 0.88),  # 1.0m Clinch (Crimson Red)
        ]

        # Draw rings from largest (2.5m) to smallest (1.0m)
        for i, radius in enumerate(thresholds):
            col = ring_colors[i % len(ring_colors)]
            ring_entity = Entity(
                model="circle",
                rotation_x=90,
                scale=(radius * 2.0, radius * 2.0, 1),
                color=col,
                y=0.01 + i * 0.002,
            )
            self.rings.append((ring_entity, radius))

    def toggle_rings(self) -> bool:
        """Toggles floor rings visibility on/off (distance spoiler toggle)."""
        self.show_rings = not self.show_rings
        for ring, _ in self.rings:
            ring.enabled = self.show_rings
        return self.show_rings

    def update_rings_position(self, target_pos: Vec3):
        """Keep distance rings centered under the opponent."""
        if not self.show_rings:
            return
        for ring, _ in self.rings:
            ring.x = target_pos.x
            ring.z = target_pos.z


class Mannequin(Entity):
    """Stylized humanoid placeholder model with head, visor, torso, and limbs."""

    def __init__(self, main_color, visor_color, **kwargs):
        super().__init__(**kwargs)

        # Torso
        self.torso = Entity(
            parent=self,
            model="cube",
            scale=(0.5, 0.7, 0.3),
            y=1.05,
            color=main_color,
        )

        # Head
        self.head = Entity(
            parent=self,
            model="sphere",
            scale=(0.35, 0.38, 0.35),
            y=1.65,
            color=main_color,
        )

        # Visor (indicates facing direction)
        self.visor = Entity(
            parent=self.head,
            model="cube",
            scale=(0.85, 0.3, 0.35),
            z=0.45,
            y=0.05,
            color=visor_color,
        )

        # Shoulders / Arms
        self.left_arm = Entity(
            parent=self,
            model="cube",
            scale=(0.14, 0.65, 0.16),
            position=(-0.35, 0.95, 0),
            color=main_color,
        )
        self.right_arm = Entity(
            parent=self,
            model="cube",
            scale=(0.14, 0.65, 0.16),
            position=(0.35, 0.95, 0),
            color=main_color,
        )

        # Legs
        self.left_leg = Entity(
            parent=self,
            model="cube",
            scale=(0.18, 0.7, 0.2),
            position=(-0.16, 0.35, 0),
            color=main_color * 0.85,
        )
        self.right_leg = Entity(
            parent=self,
            model="cube",
            scale=(0.18, 0.7, 0.2),
            position=(0.16, 0.35, 0),
            color=main_color * 0.85,
        )


class Player(Mannequin):
    """Third-person controllable player with slow walking pace."""

    def __init__(self, **kwargs):
        super().__init__(
            main_color=color.rgb(65 / 255, 130 / 255, 225 / 255),
            visor_color=color.rgb(90 / 255, 230 / 255, 255 / 255),
            **kwargs,
        )
        self.speed = CONFIG.player_walk_speed
        self.walk_phase = 0.0
        self.camera_mode = (
            0  # 0: Follow Third-Person, 1: Over-Shoulder, 2: First-Person
        )

    def update_movement(self, dt: float, camera_yaw: float, strafe_mode: bool = False):
        """Processes standard FPS/TPS WASD movement relative to camera yaw."""
        rad = math.radians(camera_yaw)
        cam_forward = Vec3(math.sin(rad), 0, math.cos(rad))
        cam_right = Vec3(math.cos(rad), 0, -math.sin(rad))

        # Standard forward/back and left/right strafing input
        input_forward = (held_keys["w"] or held_keys["up arrow"]) - (
            held_keys["s"] or held_keys["down arrow"]
        )
        input_right = (held_keys["d"] or held_keys["right arrow"]) - (
            held_keys["a"] or held_keys["left arrow"]
        )

        world_dir = cam_forward * input_forward + cam_right * input_right

        is_moving = world_dir.length_squared() > 0.001
        if is_moving:
            world_dir = world_dir.normalized()
            self.position += world_dir * self.speed * dt

            if strafe_mode:
                # In strafe / FPS / over-shoulder mode, player body faces camera look direction
                self.rotation_y = camera_yaw
            else:
                # In standard TPS mode, player turns smoothly to face movement heading
                target_rot = math.degrees(math.atan2(world_dir.x, world_dir.z))
                angle_diff = (target_rot - self.rotation_y + 180) % 360 - 180
                self.rotation_y += angle_diff * min(1.0, dt * 14.0)

            # Procedural walking animation (scaled to 30% slower pace)
            self.walk_phase += dt * 5.8
            self.left_leg.rotation_x = math.sin(self.walk_phase) * 28.0
            self.right_leg.rotation_x = -math.sin(self.walk_phase) * 28.0
            self.left_arm.rotation_x = -math.sin(self.walk_phase) * 24.0
            self.right_arm.rotation_x = math.sin(self.walk_phase) * 24.0
            self.torso.y = 1.05 + abs(math.sin(self.walk_phase)) * 0.04
        else:
            if strafe_mode:
                self.rotation_y = camera_yaw
            # Idle damping
            self.left_leg.rotation_x *= 0.8
            self.right_leg.rotation_x *= 0.8
            self.left_arm.rotation_x *= 0.8
            self.right_arm.rotation_x *= 0.8
            self.torso.y = 1.05 + math.sin(time.time() * 2.0) * 0.015


class Opponent(Mannequin):
    """Sparring opponent entity with slow milling AI."""

    STATE_MILLING = "Milling Around"
    STATE_IDLE = "Standing Still"
    STATE_FOLLOW = "Slow Advance"

    def __init__(self, **kwargs):
        super().__init__(
            main_color=color.rgb(205 / 255, 55 / 255, 65 / 255),
            visor_color=color.rgb(255 / 255, 220 / 255, 90 / 255),
            **kwargs,
        )
        self.state = Opponent.STATE_MILLING
        self.speed = CONFIG.opponent_speed
        self.wander_timer = 0.0
        self.wander_heading = 0.0
        self.is_paused = False
        self.walk_phase = 0.0

    def toggle_state(self):
        """Cycles opponent AI behavior mode."""
        if self.state == Opponent.STATE_MILLING:
            self.state = Opponent.STATE_IDLE
        elif self.state == Opponent.STATE_IDLE:
            self.state = Opponent.STATE_FOLLOW
        else:
            self.state = Opponent.STATE_MILLING
        return self.state

    def update_ai(self, dt: float, player_pos: Vec3):
        """Updates milling movement or idle behavior."""
        if self.state == Opponent.STATE_IDLE:
            # Stand still, gently face player
            diff = player_pos - self.position
            if diff.length_squared() > 0.01:
                target_rot = math.degrees(math.atan2(diff.x, diff.z))
                self.rotation_y += (target_rot - self.rotation_y) * min(1.0, dt * 4.0)
            self.left_leg.rotation_x = 0
            self.right_leg.rotation_x = 0
            return

        if self.state == Opponent.STATE_FOLLOW:
            diff = player_pos - self.position
            dist = diff.length()
            if dist > 0.6:
                dir_vec = diff.normalized()
                self.position += dir_vec * (self.speed * 0.7) * dt
                self.rotation_y = math.degrees(math.atan2(dir_vec.x, dir_vec.z))
                self.walk_phase += dt * 4.2
                self.left_leg.rotation_x = math.sin(self.walk_phase) * 22.0
                self.right_leg.rotation_x = -math.sin(self.walk_phase) * 22.0
            return

        # STATE_MILLING: Wanders slowly within bounds, occasionally pausing
        self.wander_timer -= dt
        if self.wander_timer <= 0.0:
            self.wander_timer = random.uniform(2.5, 5.0)
            self.is_paused = (
                random.random() < 0.35
            )  # 35% chance to pause and look around
            if not self.is_paused:
                # Pick a wander angle, keeping roughly within 5m radius of origin
                dist_from_center = math.hypot(self.x, self.z)
                if dist_from_center > 4.5:
                    # Head back towards origin
                    self.wander_heading = math.degrees(math.atan2(-self.x, -self.z))
                else:
                    self.wander_heading = random.uniform(0, 360)

        if not self.is_paused:
            rad = math.radians(self.wander_heading)
            move_vec = Vec3(math.sin(rad), 0, math.cos(rad))
            self.position += move_vec * self.speed * dt

            # Smoothly face heading
            self.rotation_y += (self.wander_heading - self.rotation_y) * min(
                1.0, dt * 5.0
            )

            self.walk_phase += dt * 4.2
            self.left_leg.rotation_x = math.sin(self.walk_phase) * 22.0
            self.right_leg.rotation_x = -math.sin(self.walk_phase) * 22.0
        else:
            self.left_leg.rotation_x *= 0.8
            self.right_leg.rotation_x *= 0.8
