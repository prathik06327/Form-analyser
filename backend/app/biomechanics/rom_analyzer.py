"""Range-of-motion tracking for elbow angles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RangeOfMotionState:
    """Stores minimum, maximum, and current ROM values for one side."""

    min_angle: float | None = None
    max_angle: float | None = None
    current_rom: float | None = None

    def update(self, angle: float | None) -> None:
        """Update the tracked range using the latest elbow angle."""

        if angle is None:
            return

        if self.min_angle is None or angle < self.min_angle:
            self.min_angle = angle

        if self.max_angle is None or angle > self.max_angle:
            self.max_angle = angle

        if self.min_angle is not None and self.max_angle is not None:
            self.current_rom = self.max_angle - self.min_angle

    def reset(self) -> None:
        """Clear the stored state."""

        self.min_angle = None
        self.max_angle = None
        self.current_rom = None

    def as_dict(self) -> dict[str, float | None]:
        """Return the state as a dictionary."""

        return {
            "min_angle": self.min_angle,
            "max_angle": self.max_angle,
            "current_rom": self.current_rom,
        }


class RangeOfMotionAnalyzer:
    """Track elbow range of motion continuously as frames arrive."""

    def __init__(self) -> None:
        self.left_state = RangeOfMotionState()
        self.right_state = RangeOfMotionState()

    def update(
        self,
        left_angle: float | None = None,
        right_angle: float | None = None,
    ) -> dict[str, float | None | dict[str, float | None]]:
        """Update the tracked ROM state from the latest elbow angles."""

        self.left_state.update(left_angle)
        self.right_state.update(right_angle)

        active_side = self._select_active_side()
        active_state = self._get_state(active_side)

        return {
            "active_side": active_side,
            "left": self.left_state.as_dict(),
            "right": self.right_state.as_dict(),
            "min_angle": active_state.min_angle if active_state else None,
            "max_angle": active_state.max_angle if active_state else None,
            "range_of_motion": active_state.current_rom if active_state else None,
        }

    def reset(self) -> None:
        """Reset both tracked sides."""

        self.left_state.reset()
        self.right_state.reset()

    def _select_active_side(self) -> str | None:
        """Choose the side with the most useful ROM information."""

        left_rom = self.left_state.current_rom or 0.0
        right_rom = self.right_state.current_rom or 0.0

        if left_rom == 0.0 and right_rom == 0.0:
            if self.left_state.max_angle is not None:
                return "left"
            if self.right_state.max_angle is not None:
                return "right"
            return None

        return "left" if left_rom >= right_rom else "right"

    def _get_state(self, side: str | None) -> RangeOfMotionState | None:
        """Return the state for the requested side."""

        if side == "left":
            return self.left_state
        if side == "right":
            return self.right_state
        return None