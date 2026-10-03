"""Joint-angle calculations for biomechanics analysis."""

from __future__ import annotations

from dataclasses import dataclass
from math import degrees
from typing import Mapping, Sequence

import numpy as np

from app.services.pose_service import Keypoint


PointLike = Keypoint | Sequence[float] | np.ndarray


@dataclass(slots=True)
class AngleResult:
    """Container for a single angle measurement."""

    angle: float | None
    is_valid: bool


class AngleCalculator:
    """Calculate reusable joint angles from already extracted keypoints."""

    def __init__(self, min_confidence: float = 0.3) -> None:
        self.min_confidence = min_confidence

    def calculate_angle(
        self,
        point_a: PointLike | None,
        point_b: PointLike | None,
        point_c: PointLike | None,
        min_confidence: float | None = None,
    ) -> float | None:
        """Return the angle ABC in degrees, or ``None`` if it cannot be computed."""

        confidence_threshold = self.min_confidence if min_confidence is None else min_confidence
        a_point = self._normalize_point(point_a, confidence_threshold)
        b_point = self._normalize_point(point_b, confidence_threshold)
        c_point = self._normalize_point(point_c, confidence_threshold)

        if a_point is None or b_point is None or c_point is None:
            return None

        vector_ab = a_point - b_point
        vector_cb = c_point - b_point

        norm_ab = np.linalg.norm(vector_ab)
        norm_cb = np.linalg.norm(vector_cb)
        if norm_ab == 0.0 or norm_cb == 0.0:
            return None

        cosine_value = float(np.dot(vector_ab, vector_cb) / (norm_ab * norm_cb))
        cosine_value = float(np.clip(cosine_value, -1.0, 1.0))
        return float(degrees(np.arccos(cosine_value)))

    def calculate_left_elbow_angle(
        self,
        keypoints: Mapping[str, Keypoint],
        min_confidence: float | None = None,
    ) -> float | None:
        """Calculate the left elbow angle using shoulder, elbow, and wrist."""

        return self.calculate_angle(
            keypoints.get("left_shoulder"),
            keypoints.get("left_elbow"),
            keypoints.get("left_wrist"),
            min_confidence,
        )

    def calculate_right_elbow_angle(
        self,
        keypoints: Mapping[str, Keypoint],
        min_confidence: float | None = None,
    ) -> float | None:
        """Calculate the right elbow angle using shoulder, elbow, and wrist."""

        return self.calculate_angle(
            keypoints.get("right_shoulder"),
            keypoints.get("right_elbow"),
            keypoints.get("right_wrist"),
            min_confidence,
        )

    def calculate_shoulder_angle(
        self,
        keypoints: Mapping[str, Keypoint],
        side: str = "left",
        min_confidence: float | None = None,
    ) -> float | None:
        """Calculate the shoulder angle using hip, shoulder, and elbow."""

        if side not in {"left", "right"}:
            raise ValueError("side must be 'left' or 'right'")

        return self.calculate_angle(
            keypoints.get(f"{side}_hip"),
            keypoints.get(f"{side}_shoulder"),
            keypoints.get(f"{side}_elbow"),
            min_confidence,
        )

    def calculate_joint_angles(
        self,
        keypoints: Mapping[str, Keypoint],
        min_confidence: float | None = None,
    ) -> dict[str, float | None]:
        """Return the current elbow and shoulder angles for both sides."""

        return {
            "left_elbow_angle": self.calculate_left_elbow_angle(keypoints, min_confidence),
            "right_elbow_angle": self.calculate_right_elbow_angle(keypoints, min_confidence),
            "left_shoulder_angle": self.calculate_shoulder_angle(keypoints, "left", min_confidence),
            "right_shoulder_angle": self.calculate_shoulder_angle(keypoints, "right", min_confidence),
        }

    def _normalize_point(
        self,
        point: PointLike | None,
        min_confidence: float,
    ) -> np.ndarray | None:
        """Convert a keypoint into a 2D NumPy point when confidence is sufficient."""

        if point is None:
            return None

        if isinstance(point, Keypoint):
            if point.confidence < min_confidence:
                return None
            return np.asarray([point.x, point.y], dtype=float)

        array = np.asarray(point, dtype=float)
        if array.size < 2:
            return None

        return array.reshape(-1)[:2]