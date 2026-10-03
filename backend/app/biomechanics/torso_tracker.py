"""Track torso inclination, lean, and sway from shoulder and hip keypoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from app.services.pose_service import Keypoint


@dataclass(slots=True)
class TorsoState:
    """Store the previous torso midpoint and latest measurement values."""

    previous_midpoint: np.ndarray | None = None
    torso_angle: float | None = None
    body_sway: float | None = None
    body_lean: str = "Unknown"


class TorsoTracker:
    """Measure torso-related motion without assigning form quality."""

    def __init__(self, lean_threshold_degrees: float = 7.0) -> None:
        self.lean_threshold_degrees = lean_threshold_degrees
        self.state = TorsoState()

    def update(
        self,
        keypoints: Mapping[str, Keypoint],
        min_confidence: float = 0.3,
    ) -> dict[str, float | str | tuple[float, float] | None]:
        """Return torso inclination and sway measurements for the current frame."""

        left_shoulder = self._to_point(keypoints.get("left_shoulder"), min_confidence)
        right_shoulder = self._to_point(keypoints.get("right_shoulder"), min_confidence)
        left_hip = self._to_point(keypoints.get("left_hip"), min_confidence)
        right_hip = self._to_point(keypoints.get("right_hip"), min_confidence)

        shoulder_midpoint = self._midpoint(left_shoulder, right_shoulder)
        hip_midpoint = self._midpoint(left_hip, right_hip)

        if shoulder_midpoint is None or hip_midpoint is None:
            self.state.torso_angle = None
            self.state.body_sway = None
            self.state.body_lean = "Unknown"
            return {
                "torso_angle": None,
                "body_sway": None,
                "body_lean": "Unknown",
                "torso_midpoint": None,
            }

        torso_vector = shoulder_midpoint - hip_midpoint
        torso_angle = self._calculate_torso_angle(torso_vector)
        torso_midpoint = (shoulder_midpoint + hip_midpoint) / 2.0

        body_sway = None
        if self.state.previous_midpoint is not None:
            body_sway = float(np.linalg.norm(torso_midpoint - self.state.previous_midpoint))

        self.state.previous_midpoint = torso_midpoint
        self.state.torso_angle = torso_angle
        self.state.body_sway = body_sway
        self.state.body_lean = self._detect_lean(torso_vector, torso_angle)

        return {
            "torso_angle": torso_angle,
            "body_sway": body_sway,
            "body_lean": self.state.body_lean,
            "torso_midpoint": (float(torso_midpoint[0]), float(torso_midpoint[1])),
        }

    def reset(self) -> None:
        """Reset the tracked torso state."""

        self.state = TorsoState()

    def _to_point(self, keypoint: Keypoint | None, min_confidence: float) -> np.ndarray | None:
        """Convert a keypoint into a NumPy point if confidence is high enough."""

        if keypoint is None or keypoint.confidence < min_confidence:
            return None

        return np.asarray([keypoint.x, keypoint.y], dtype=float)

    def _midpoint(
        self,
        point_a: np.ndarray | None,
        point_b: np.ndarray | None,
    ) -> np.ndarray | None:
        """Return the midpoint between two 2D points."""

        if point_a is None or point_b is None:
            return None

        return (point_a + point_b) / 2.0

    def _calculate_torso_angle(self, torso_vector: np.ndarray) -> float:
        """Calculate the torso inclination relative to the vertical axis."""

        vertical_axis = np.asarray([0.0, -1.0], dtype=float)
        norm_torso = np.linalg.norm(torso_vector)
        if norm_torso == 0.0:
            return 0.0

        cosine_value = float(np.dot(torso_vector, vertical_axis) / norm_torso)
        cosine_value = float(np.clip(cosine_value, -1.0, 1.0))
        angle = float(np.degrees(np.arccos(cosine_value)))
        return angle

    def _detect_lean(self, torso_vector: np.ndarray, torso_angle: float) -> str:
        """Classify torso lean direction using the torso vector."""

        if torso_angle <= self.lean_threshold_degrees:
            return "Upright"

        horizontal_delta = float(torso_vector[0])
        if horizontal_delta < 0:
            return "Leaning Left"
        if horizontal_delta > 0:
            return "Leaning Right"
        return "Leaning"