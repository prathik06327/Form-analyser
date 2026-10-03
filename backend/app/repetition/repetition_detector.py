"""Repetition start and completion detection built on the FSM."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from app.repetition.motion_state import MotionStateMachine, MotionStateResult, MovementPhase


@dataclass(slots=True)
class RepetitionDetectionResult:
    """Output from the repetition detector for a single frame."""

    motion_result: MotionStateResult
    repetition_started: bool
    repetition_completed: bool
    reason: str = ""


class RepetitionDetector:
    """Detect repetition start and completion events from biomechanics measurements."""

    def __init__(self, motion_state_machine: MotionStateMachine | None = None) -> None:
        self.motion_state_machine = motion_state_machine or MotionStateMachine()

    def reset(self) -> None:
        """Reset the underlying FSM."""

        self.motion_state_machine.reset()

    def detect(self, biomechanics: Mapping[str, object]) -> RepetitionDetectionResult:
        """Return the current motion phase and repetition event flags."""

        motion_result = self.motion_state_machine.update(biomechanics)
        repetition_started = self._is_rep_start(motion_result)
        repetition_completed = self._is_rep_complete(motion_result)

        return RepetitionDetectionResult(
            motion_result=motion_result,
            repetition_started=repetition_started,
            repetition_completed=repetition_completed,
            reason=motion_result.reason,
        )

    def _is_rep_start(self, motion_result: MotionStateResult) -> bool:
        """Return ``True`` when the FSM reaches the start position from idle."""

        return (
            motion_result.transition_confirmed
            and motion_result.current_state == MovementPhase.START_POSITION
            and motion_result.previous_state in {MovementPhase.IDLE, MovementPhase.REP_COMPLETED}
        )

    def _is_rep_complete(self, motion_result: MotionStateResult) -> bool:
        """Return ``True`` when a full curl cycle returns to the repetition completion phase."""

        return (
            motion_result.transition_confirmed
            and motion_result.current_state == MovementPhase.REP_COMPLETED
            and motion_result.previous_state == MovementPhase.LOWERING_DOWN
        )
