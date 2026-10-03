"""Centralized threshold configuration for form assessment rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AssessmentThresholds:
    """Configurable thresholds used by the assessment engine."""

    # Calibrated against angles as a single 2D camera measures them, not against
    # true anatomical angles. Because the arm foreshortens unless the camera is
    # exactly side-on, a fully extended elbow typically projects to ~135-145
    # degrees and a full-range curl to ~90-105 degrees of travel. Thresholds set
    # for unprojected angles (150 / 100) flag every real repetition as faulty.
    minimum_rom: float = 85.0
    minimum_extension_angle: float = 135.0
    maximum_torso_lean_degrees: float = 8.0
    maximum_body_sway: float = 4.0
    maximum_elbow_drift: float = 10.0
    maximum_wrist_instability: float = 8.0
    acceptable_lowering_speed: float = 140.0
    acceptable_curl_speed: float = 120.0
    minimum_tempo_consistency: float = 0.75
    minimum_stability: float = 0.80
    maximum_jerkiness: float = 0.35
    minimum_smoothness: float = 0.80
    minimum_symmetry: float = 0.80


def get_default_thresholds() -> AssessmentThresholds:
    """Return the default assessment thresholds."""

    return AssessmentThresholds()
