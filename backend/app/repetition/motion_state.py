"""Finite state machine for bicep curl repetition segmentation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class MovementPhase(str, Enum):
    """Supported movement states for repetition segmentation."""

    IDLE = "IDLE"
    START_POSITION = "START_POSITION"
    CURLING_UP = "CURLING_UP"
    TOP_POSITION = "TOP_POSITION"
    LOWERING_DOWN = "LOWERING_DOWN"
    REP_COMPLETED = "REP_COMPLETED"


@dataclass(slots=True)
class MotionStateResult:
    """FSM output for a single frame."""

    current_state: MovementPhase
    previous_state: MovementPhase
    candidate_state: MovementPhase | None
    transition_confirmed: bool
    rep_progress: float
    movement_direction: str
    active_side: str | None
    active_elbow_angle: float | None
    current_rom: float | None
    reason: str = ""


class MotionStateMachine:
    """Noise-resistant FSM that turns biomechanics into movement phases."""

    allowed_transitions: dict[MovementPhase, tuple[MovementPhase, ...]] = {
        MovementPhase.IDLE: (MovementPhase.START_POSITION,),
        MovementPhase.START_POSITION: (MovementPhase.CURLING_UP,),
        MovementPhase.CURLING_UP: (MovementPhase.TOP_POSITION,),
        MovementPhase.TOP_POSITION: (MovementPhase.LOWERING_DOWN,),
        MovementPhase.LOWERING_DOWN: (MovementPhase.REP_COMPLETED,),
        MovementPhase.REP_COMPLETED: (MovementPhase.START_POSITION,),
    }

    def __init__(
        self,
        start_angle_threshold: float = 130.0,
        top_angle_threshold: float = 100.0,
        movement_delta_threshold: float = 4.0,
        min_rom_for_motion: float = 5.0,
        transition_confirmation_frames: int = 2,
        adaptive_calibration: bool = True,
        min_calibration_span: float = 30.0,
        calibration_margin: float = 0.25,
    ) -> None:
        # Baseline thresholds, used until adaptive calibration has seen enough
        # of the lifter's range. They are deliberately far from anatomical
        # lockout (180) and full flexion (0): a single 2D camera foreshortens
        # the arm unless it is exactly side-on, so a genuinely straight arm
        # commonly projects to only ~135-150 degrees. Thresholds near full
        # extension therefore never fire on real footage.
        self.start_angle_threshold = start_angle_threshold
        self.top_angle_threshold = top_angle_threshold
        self.movement_delta_threshold = movement_delta_threshold
        self.min_rom_for_motion = min_rom_for_motion
        self.transition_confirmation_frames = max(1, transition_confirmation_frames)

        # Adaptive calibration removes the dependence on any one camera setup by
        # deriving thresholds from the range this lifter actually produces.
        self.adaptive_calibration = adaptive_calibration
        self.min_calibration_span = min_calibration_span
        self.calibration_margin = calibration_margin

        self.current_state = MovementPhase.IDLE
        self.previous_state = MovementPhase.IDLE
        self.pending_state: MovementPhase | None = None
        self.pending_count = 0
        self.last_elbow_angle: float | None = None

        self.observed_min_angle: float | None = None
        self.observed_max_angle: float | None = None
        # Thresholds in force for the current frame; recomputed every update.
        self.effective_start_threshold = start_angle_threshold
        self.effective_top_threshold = top_angle_threshold

    def reset(self) -> None:
        """Return the FSM to the initial idle state."""

        self.current_state = MovementPhase.IDLE
        self.previous_state = MovementPhase.IDLE
        self.pending_state = None
        self.pending_count = 0
        self.last_elbow_angle = None
        self.observed_min_angle = None
        self.observed_max_angle = None
        self.effective_start_threshold = self.start_angle_threshold
        self.effective_top_threshold = self.top_angle_threshold

    def _update_calibration(self, elbow_angle: float | None) -> None:
        """Fold this frame's angle into the observed range and re-derive thresholds.

        Once the lifter has shown a span wide enough to be a real repetition,
        the start/top gates are placed a fixed fraction in from each end of that
        span. This tracks whatever range the camera actually captures instead of
        assuming one particular filming angle.
        """

        if elbow_angle is not None:
            self.observed_min_angle = (
                elbow_angle if self.observed_min_angle is None else min(self.observed_min_angle, elbow_angle)
            )
            self.observed_max_angle = (
                elbow_angle if self.observed_max_angle is None else max(self.observed_max_angle, elbow_angle)
            )

        if not self.adaptive_calibration or self.observed_min_angle is None or self.observed_max_angle is None:
            self.effective_start_threshold = self.start_angle_threshold
            self.effective_top_threshold = self.top_angle_threshold
            return

        span = self.observed_max_angle - self.observed_min_angle
        if span < self.min_calibration_span:
            # Not enough movement yet to tell a repetition from standing still.
            self.effective_start_threshold = self.start_angle_threshold
            self.effective_top_threshold = self.top_angle_threshold
            return

        margin = span * self.calibration_margin
        # Never demand more extension than the baseline would have: calibration
        # may only make the start gate easier to reach, never harder.
        self.effective_start_threshold = min(
            self.start_angle_threshold, self.observed_max_angle - margin
        )
        self.effective_top_threshold = max(
            self.top_angle_threshold, self.observed_min_angle + margin
        )

    def update(self, biomechanics: Mapping[str, object]) -> MotionStateResult:
        """Update the FSM using the latest biomechanics payload."""

        active_side, elbow_angle = self._select_active_angle(biomechanics)
        movement_direction = str(biomechanics.get("movement_direction") or "Stationary")
        current_rom = self._as_float(biomechanics.get("range_of_motion"))

        self._update_calibration(elbow_angle)

        candidate_state = self._candidate_state(
            current_state=self.current_state,
            elbow_angle=elbow_angle,
            movement_direction=movement_direction,
            current_rom=current_rom,
        )

        transition_confirmed, reason = self._commit_transition(candidate_state)
        rep_progress = self._calculate_rep_progress(elbow_angle)

        result = MotionStateResult(
            current_state=self.current_state,
            previous_state=self.previous_state,
            candidate_state=candidate_state,
            transition_confirmed=transition_confirmed,
            rep_progress=rep_progress,
            movement_direction=movement_direction,
            active_side=active_side,
            active_elbow_angle=elbow_angle,
            current_rom=current_rom,
            reason=reason,
        )

        self.last_elbow_angle = elbow_angle if elbow_angle is not None else self.last_elbow_angle
        return result

    def _candidate_state(
        self,
        current_state: MovementPhase,
        elbow_angle: float | None,
        movement_direction: str,
        current_rom: float | None,
    ) -> MovementPhase | None:
        """Choose the next plausible state for the current frame."""

        if elbow_angle is None:
            return None

        if current_state == MovementPhase.IDLE:
            if self._is_start_position(elbow_angle, movement_direction):
                return MovementPhase.START_POSITION
            return None

        if current_state == MovementPhase.START_POSITION:
            if self._is_curling_up(elbow_angle, movement_direction, current_rom):
                return MovementPhase.CURLING_UP
            return None

        if current_state == MovementPhase.CURLING_UP:
            if self._is_top_position(elbow_angle, movement_direction, current_rom):
                return MovementPhase.TOP_POSITION
            return None

        if current_state == MovementPhase.TOP_POSITION:
            if self._is_lowering_down(elbow_angle, movement_direction, current_rom):
                return MovementPhase.LOWERING_DOWN
            return None

        if current_state == MovementPhase.LOWERING_DOWN:
            if self._is_rep_completed(elbow_angle, movement_direction, current_rom):
                return MovementPhase.REP_COMPLETED
            return None

        if current_state == MovementPhase.REP_COMPLETED:
            if self._is_start_position(elbow_angle, movement_direction):
                return MovementPhase.START_POSITION
            return None

        return None

    def _commit_transition(self, candidate_state: MovementPhase | None) -> tuple[bool, str]:
        """Commit a candidate state only after enough stable frames."""

        if candidate_state is None or candidate_state == self.current_state:
            self.pending_state = None
            self.pending_count = 0
            return False, ""

        if candidate_state not in self.allowed_transitions.get(self.current_state, ()):
            self.pending_state = None
            self.pending_count = 0
            return False, "invalid_transition"

        if candidate_state == self.pending_state:
            self.pending_count += 1
        else:
            self.pending_state = candidate_state
            self.pending_count = 1

        if self.pending_count < self.transition_confirmation_frames:
            return False, "pending_confirmation"

        self.previous_state = self.current_state
        self.current_state = candidate_state
        self.pending_state = None
        self.pending_count = 0
        return True, "transition_confirmed"

    def _is_start_position(self, elbow_angle: float, movement_direction: str) -> bool:
        """Detect a stable start position near full extension."""

        return elbow_angle >= self.effective_start_threshold and movement_direction in {
            "Stationary",
            "Lowering Down",
        }

    def _is_curling_up(
        self,
        elbow_angle: float,
        movement_direction: str,
        current_rom: float | None,
    ) -> bool:
        """Detect the upward curl phase."""

        if current_rom is not None and current_rom < self.min_rom_for_motion:
            return False

        angle_is_decreasing = self.last_elbow_angle is not None and (
            self.last_elbow_angle - elbow_angle >= self.movement_delta_threshold
        )
        return movement_direction == "Curling Up" or angle_is_decreasing

    def _is_top_position(
        self,
        elbow_angle: float,
        movement_direction: str,
        current_rom: float | None,
    ) -> bool:
        """Detect the top of the curl."""

        if current_rom is not None and current_rom < self.min_rom_for_motion:
            return False

        return elbow_angle <= self.effective_top_threshold and movement_direction in {
            "Curling Up",
            "Stationary",
        }

    def _is_lowering_down(
        self,
        elbow_angle: float,
        movement_direction: str,
        current_rom: float | None,
    ) -> bool:
        """Detect the lowering phase after the top position."""

        if current_rom is not None and current_rom < self.min_rom_for_motion:
            return False

        angle_is_increasing = self.last_elbow_angle is not None and (
            elbow_angle - self.last_elbow_angle >= self.movement_delta_threshold
        )
        return movement_direction == "Lowering Down" or angle_is_increasing

    def _is_rep_completed(
        self,
        elbow_angle: float,
        movement_direction: str,
        current_rom: float | None,
    ) -> bool:
        """Detect the return to the start position after lowering."""

        return elbow_angle >= self.effective_start_threshold and movement_direction in {
            "Lowering Down",
            "Stationary",
        }

    def _calculate_rep_progress(self, elbow_angle: float | None) -> float:
        """Estimate rep progress for debug output."""

        if elbow_angle is None:
            return 0.0

        start_angle = self.effective_start_threshold
        top_angle = self.effective_top_threshold
        total_span = max(start_angle - top_angle, 1.0)

        if self.current_state in {MovementPhase.IDLE, MovementPhase.START_POSITION}:
            return 0.0

        if self.current_state == MovementPhase.CURLING_UP:
            progress = ((start_angle - elbow_angle) / total_span) * 50.0
            return float(max(0.0, min(50.0, progress)))

        if self.current_state == MovementPhase.TOP_POSITION:
            return 50.0

        if self.current_state == MovementPhase.LOWERING_DOWN:
            progress = 50.0 + (((elbow_angle - top_angle) / total_span) * 50.0)
            return float(max(50.0, min(100.0, progress)))

        if self.current_state == MovementPhase.REP_COMPLETED:
            return 100.0

        return 0.0

    def _select_active_angle(self, biomechanics: Mapping[str, object]) -> tuple[str | None, float | None]:
        """Select the active arm angle from the biomechanics payload."""

        active_side = str(biomechanics.get("active_arm_side") or "").strip().lower()
        left_angle = self._as_float(biomechanics.get("left_elbow_angle"))
        right_angle = self._as_float(biomechanics.get("right_elbow_angle"))

        if active_side == "left" and left_angle is not None:
            return "left", left_angle
        if active_side == "right" and right_angle is not None:
            return "right", right_angle

        if left_angle is not None and right_angle is None:
            return "left", left_angle
        if right_angle is not None and left_angle is None:
            return "right", right_angle

        if left_angle is not None and right_angle is not None:
            if abs(left_angle - right_angle) <= 20.0:
                return "left", left_angle
            return ("left", left_angle) if left_angle < right_angle else ("right", right_angle)

        return None, None

    def _as_float(self, value: object) -> float | None:
        """Safely convert an arbitrary numeric-like value to float."""

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
