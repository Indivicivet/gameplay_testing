"""Mathematical transfer functions for distance-based indicators.

Implements the bumpy/stepped multi-plateau response curve drawn in Image 1,
along with threshold crossing detection for transient impact pulses.
"""

import math
from typing import List, Tuple
from config import CONFIG


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Hermite interpolation smoothstep between edge0 and edge1."""
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def calculate_fx(
    distance: float,
    thresholds: List[float] = None,
    step_width: float = None,
) -> Tuple[float, int]:
    """Calculates f(d) matching the hand-drawn bumpy multi-terrace curve.

    Args:
        distance: 3D distance between player and opponent in meters.
        thresholds: Descending list of thresholds [1.6, 1.4, 1.2, 1.0].
        step_width: Half-width of the sharp transition zone in meters.

    Returns:
        (fx_intensity in [0.0, 1.0], zone_index from 0 to 4)
    """
    if thresholds is None:
        thresholds = CONFIG.thresholds
    if step_width is None:
        step_width = CONFIG.step_width

    # Thresholds are ordered descending: [1.6, 1.4, 1.2, 1.0]
    # Zone 0: d > thresholds[0] + step_width (Safe / No FX)
    # Zone 1: thresholds[1] < d <= thresholds[0] (Alert plateau ~ 0.25)
    # Zone 2: thresholds[2] < d <= thresholds[1] (Threat plateau ~ 0.50)
    # Zone 3: thresholds[3] < d <= thresholds[2] (Danger plateau ~ 0.75)
    # Zone 4: d <= thresholds[3] (Clinch plateau ~ 1.00)

    num_tiers = len(thresholds)
    tier_height = 1.0 / num_tiers  # 0.25 each for 4 tiers

    # Determine base tier index
    current_zone = 0
    for i, thresh in enumerate(thresholds):
        if distance <= thresh:
            current_zone = i + 1

    # Compute continuous bumpy function
    fx = 0.0
    for i, thresh in enumerate(thresholds):
        # As distance drops below (thresh + step_width), transition from 0 to 1
        t = 1.0 - _smoothstep(thresh - step_width, thresh + step_width, distance)
        # Each threshold adds its tier height
        fx += t * tier_height

    # Add subtle plateau slope as seen in Image 1 sketch (terrace slopes slightly down as distance increases)
    # This prevents the plateau from feeling completely dead while keeping the sharp bump
    plateau_modulation = 0.0
    if 0 < current_zone < num_tiers:
        zone_high = thresholds[current_zone - 1]
        zone_low = thresholds[current_zone]
        span = max(0.001, zone_high - zone_low)
        norm_in_zone = (
            zone_high - distance
        ) / span  # 0 at boundary to 1 at next boundary
        plateau_modulation = 0.04 * (norm_in_zone - 0.5)

    total_intensity = max(0.0, min(1.0, fx + plateau_modulation))
    return total_intensity, current_zone


class DistanceTracker:
    """Tracks distance over time to detect crossing events and generate impulse pulses."""

    def __init__(self, thresholds: List[float] = None, pulse_duration: float = None):
        self.thresholds = thresholds if thresholds is not None else CONFIG.thresholds
        self.pulse_duration = (
            pulse_duration
            if pulse_duration is not None
            else CONFIG.cross_pulse_duration
        )
        self.previous_zone = -1
        self.pulse_timer = 0.0
        self.last_cross_direction = 0  # +1 entering closer, -1 moving away

    def update(self, distance: float, dt: float) -> Tuple[float, int, float]:
        """Updates tracker state and returns (steady_fx, zone_index, pulse_intensity)."""
        steady_fx, zone = calculate_fx(distance, self.thresholds)

        if self.previous_zone == -1:
            self.previous_zone = zone

        # Detect zone crossing
        if zone != self.previous_zone:
            self.pulse_timer = self.pulse_duration
            self.last_cross_direction = 1 if zone > self.previous_zone else -1
            self.previous_zone = zone

        pulse = 0.0
        if self.pulse_timer > 0.0:
            self.pulse_timer = max(0.0, self.pulse_timer - dt)
            # Quadratic decay for a punchy snappy pulse
            progress = self.pulse_timer / self.pulse_duration
            pulse = progress * progress

        return steady_fx, zone, pulse
