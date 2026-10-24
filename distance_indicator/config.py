"""Configuration parameters for the distance_indicator prototype."""

from dataclasses import dataclass
from typing import List


@dataclass
class DistanceConfig:
    # 4 sensible close-combat / fighting distance thresholds (in meters)
    thresholds: List[float] = None
    threshold_names: List[str] = None

    # Step transition sharpness (width of sigmoid transition in meters)
    step_width: float = 0.04

    # FoV scaling: fov = base_fov + zoom_const * f(d)
    base_fov: float = 60.0
    zoom_const: float = 16.0

    # Movement speeds (slow walking for precise distance testing)
    player_walk_speed: float = 1.8
    opponent_speed: float = 0.9

    # Transient impulse settings on crossing thresholds
    cross_pulse_duration: float = 0.35  # seconds

    def __post_init__(self):
        if self.thresholds is None:
            # 4 fighting distance thresholds: 1.6m (Alert), 1.4m (Threat), 1.2m (Danger), 1.0m (Clinch)
            self.thresholds = [1.6, 1.4, 1.2, 1.0]
        if self.threshold_names is None:
            self.threshold_names = ["Alert", "Threat", "Danger", "Clinch"]


CONFIG = DistanceConfig()
