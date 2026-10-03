"""Track arm movement direction from consecutive keypoint positions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from app.services.pose_service import Keypoint


@dataclass(slots=True)
class ArmMotionState:
    """Store the previous arm positions and the latest displacement values."""

    previous_wrist: np.ndarray | None = None
    previous_elbow: np.ndarray | None = None
    wrist_displacement: float | None = None
    elbow_displacement: float | None = None
    direction: str = "Stationary"


class ArmTracker:
    """Measure wrist and elbow movement without counting repetitions."""

    def __init__(self, movement_threshold: float = 2.0) -> None:
        self.movement_threshold = movement_threshold
        self.left_state = ArmMotionState()
        self.right_state = ArmMotionState()

    def update(
        self,
        keypoints: Mapping[str, Keypoint],
        min_confidence: float = 0.3,
    ) -> dict[str, object]:
        """Update arm movement states from the latest frame."""

        left_result = self._update_side(
            self.left_state,
            keypoints.get("left_wrist"),
            keypoints.get("left_elbow"),
            min_confidence,
        )
        right_result = self._update_side(
            self.right_state,
            keypoints.get("right_wrist"),
            keypoints.get("right_elbow"),
            min_confidence,
        )

        active_side = self._select_active_side(left_result, right_result)
        active_result = left_result if active_side == "left" else right_result if active_side == "right" else None

        return {
            "active_side": active_side,
            "movement_direction": active_result["direction"] if active_result else "Stationary",
            "wrist_displacement": active_result["wrist_displacement"] if active_result else None,
            "elbow_displacement": active_result["elbow_displacement"] if active_result else None,
            "left": left_result,
            "right": right_result,
        }

    def reset(self) -> None:
        """Clear stored movement history."""

        self.left_state = ArmMotionState()
        self.right_state = ArmMotionState()

    def _update_side(
        self,
        state: ArmMotionState,
        wrist: Keypoint | None,
        elbow: Keypoint | None,
        min_confidence: float,
    ) -> dict[str, float | str | None]:
        """Update one arm and return its motion summary."""

        wrist_point = self._to_point(wrist, min_confidence)
        elbow_point = self._to_point(elbow, min_confidence)

        previous_wrist = state.previous_wrist
        previous_elbow = state.previous_elbow

        wrist_displacement = self._calculate_displacement(previous_wrist, wrist_point)
        elbow_displacement = self._calculate_displacement(previous_elbow, elbow_point)

        state.previous_wrist = wrist_point if wrist_point is not None else state.previous_wrist
        state.previous_elbow = elbow_point if elbow_point is not None else state.previous_elbow
        state.wrist_displacement = wrist_displacement
        state.elbow_displacement = elbow_displacement

        direction = self._infer_direction(wrist_point, previous_wrist, elbow_point, previous_elbow)
        state.direction = direction

        return {
            "direction": direction,
            "wrist_displacement": wrist_displacement,
            "elbow_displacement": elbow_displacement,
        }

    def _to_point(self, keypoint: Keypoint | None, min_confidence: float) -> np.ndarray | None:
        """Convert a keypoint to a NumPy point if it is reliable enough."""

        if keypoint is None or keypoint.confidence < min_confidence:
            return None

        return np.asarray([keypoint.x, keypoint.y], dtype=float)

    def _calculate_displacement(
        self,
        previous_point: np.ndarray | None,
        current_point: np.ndarray | None,
    ) -> float | None:
        """Return the Euclidean displacement between consecutive points."""

        if previous_point is None or current_point is None:
            return None

        return float(np.linalg.norm(current_point - previous_point))

    def _infer_direction(
        self,
        current_wrist: np.ndarray | None,
        previous_wrist: np.ndarray | None,
        current_elbow: np.ndarray | None,
        previous_elbow: np.ndarray | None,
    ) -> str:
        """Infer whether the arm is curling up, lowering down, or stationary."""

        vertical_delta = 0.0
        sample_count = 0

        if current_wrist is not None and previous_wrist is not None:
            vertical_delta += float(previous_wrist[1] - current_wrist[1])
            sample_count += 1

        if current_elbow is not None and previous_elbow is not None:
            vertical_delta += float(previous_elbow[1] - current_elbow[1])
            sample_count += 1

        if sample_count == 0:
            return "Stationary"

        average_vertical_delta = vertical_delta / sample_count
        if average_vertical_delta > self.movement_threshold:
            return "Curling Up"
        if average_vertical_delta < -self.movement_threshold:
            return "Lowering Down"
        return "Stationary"

    def _select_active_side(
        self,
        left_result: dict[str, float | str | None],
        right_result: dict[str, float | str | None],
    ) -> str | None:
        """Pick the arm with the strongest observed motion."""

        left_score = self._motion_score(left_result)
        right_score = self._motion_score(right_result)

        if left_score == 0.0 and right_score == 0.0:
            return None

        return "left" if left_score >= right_score else "right"

    def _motion_score(self, result: dict[str, float | str | None]) -> float:
        """Score a motion result so the active side can be selected."""

        wrist_displacement = result.get("wrist_displacement")
        elbow_displacement = result.get("elbow_displacement")

        score = 0.0
        if isinstance(wrist_displacement, (int, float)):
            score += float(wrist_displacement)
        if isinstance(elbow_displacement, (int, float)):
            score += float(elbow_displacement)
        return score