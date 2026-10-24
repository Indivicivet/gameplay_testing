"""Configuration parameters for the distance_indicator prototype."""

from dataclasses import dataclass
from typing import List


@dataclass
class DistanceConfig:
    # 4 fighting distance thresholds in center-to-center distance (1.0m, 1.5m, 2.0m, 2.5m)
    thresholds: List[float] = None
    threshold_names: List[str] = None

    # Step transition sharpness (width of sigmoid transition in meters)
    step_width: float = 0.08

    # FoV scaling: fov = base_fov + zoom_const * f(d) + kick + breathing
    base_fov: float = 62.0
    zoom_const: float = 10.0  # Light, comfortable FoV dilation across tiers

    # Movement speeds (slowed down by 30% for careful distance testing)
    player_walk_speed: float = 1.26
    opponent_speed: float = 0.63

    # Light FoV transition kick duration (zero screen flash)
    cross_pulse_duration: float = 0.28

    def __post_init__(self):
        if self.thresholds is None:
            # 4 fighting distance thresholds (center-to-center distance: 2.5m, 2.0m, 1.5m, 1.0m)
            self.thresholds = [2.5, 2.0, 1.5, 1.0]
        if self.threshold_names is None:
            self.threshold_names = ["Alert", "Threat", "Danger", "Clinch"]


CONFIG = DistanceConfig()
