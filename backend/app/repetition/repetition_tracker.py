"""Track repetition lifecycle and aggregated repetition data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from app.repetition.motion_state import MotionStateResult, MovementPhase
from app.repetition.repetition_data import (
    RepetitionDataStore,
    RepetitionRecord,
    RepetitionSample,
)


@dataclass(slots=True)
class ActiveRepetition:
    """In-progress repetition state."""

    rep_number: int
    start_frame: int
    start_timestamp: float
    samples: list[RepetitionSample] = field(default_factory=list)
    last_sample: RepetitionSample | None = None


class RepetitionTracker:
    """Maintain repetition counts and finalized repetition records."""

    def __init__(self) -> None:
        self.total_reps = 0
        self.current_rep_number = 0
        self.current_rep_state = MovementPhase.IDLE
        self.active_repetition: ActiveRepetition | None = None
        self.data_store = RepetitionDataStore()

    def start_rep(self, frame_number: int, timestamp: float) -> None:
        """Start a new repetition if none is currently active."""

        if self.active_repetition is not None:
            return

        self.current_rep_number = self.total_reps + 1
        self.current_rep_state = MovementPhase.START_POSITION
        self.active_repetition = ActiveRepetition(
            rep_number=self.current_rep_number,
            start_frame=frame_number,
            start_timestamp=timestamp,
        )

    def update_current_rep(
        self,
        biomechanics: Mapping[str, object],
        frame_number: int,
        timestamp: float,
        motion_result: MotionStateResult,
    ) -> None:
        """Capture the latest sample for the active repetition."""

        if self.active_repetition is None:
            return

        sample = self._build_sample(biomechanics, frame_number, timestamp)
        if self.active_repetition.last_sample is not None:
            sample.curl_speed = self._calculate_curl_speed(
                previous_sample=self.active_repetition.last_sample,
                current_sample=sample,
            )

        self.active_repetition.samples.append(sample)
        self.active_repetition.last_sample = sample
        self.current_rep_state = motion_result.current_state

    def finish_rep(
        self,
        biomechanics: Mapping[str, object],
        frame_number: int,
        timestamp: float,
        motion_result: MotionStateResult,
    ) -> RepetitionRecord | None:
        """Finalize the active repetition and store the completed record."""

        if self.active_repetition is None:
            return None

        sample = self._build_sample(biomechanics, frame_number, timestamp)
        if self.active_repetition.last_sample is not None:
            sample.curl_speed = self._calculate_curl_speed(
                previous_sample=self.active_repetition.last_sample,
                current_sample=sample,
            )

        self.active_repetition.samples.append(sample)
        completed_record = self._finalize_active_rep(timestamp)
        self.current_rep_state = motion_result.current_state
        return completed_record

    def reset(self) -> None:
        """Clear all repetition counters and stored records."""

        self.total_reps = 0
        self.current_rep_number = 0
        self.current_rep_state = MovementPhase.IDLE
        self.active_repetition = None
        self.data_store.reset()

    def get_total_reps(self) -> int:
        """Return the number of completed repetitions."""

        return self.total_reps

    def is_rep_active(self) -> bool:
        """Return whether a repetition is currently active."""

        return self.active_repetition is not None

    def snapshot(self, motion_result: MotionStateResult, frame_number: int, timestamp: float) -> dict[str, object]:
        """Return the current session state for debugging and future consumers."""

        active_rep = self.active_repetition
        elapsed_frames = 0
        elapsed_seconds = 0.0
        if active_rep is not None:
            elapsed_frames = max(0, frame_number - active_rep.start_frame + 1)
            elapsed_seconds = max(0.0, timestamp - active_rep.start_timestamp)

        return {
            "current_state": motion_result.current_state.value,
            "previous_state": motion_result.previous_state.value,
            "movement_direction": self._movement_label(
                motion_result.current_state,
                motion_result.movement_direction,
            ),
            "current_rep": self.current_rep_number,
            "total_reps": self.total_reps,
            "current_elbow_angle": motion_result.active_elbow_angle,
            "current_rom": motion_result.current_rom,
            "rep_progress": motion_result.rep_progress,
            "rep_active": active_rep is not None,
            "active_rep_start_frame": active_rep.start_frame if active_rep else None,
            "active_rep_elapsed_frames": elapsed_frames,
            "active_rep_elapsed_seconds": elapsed_seconds,
            "session_data": self.data_store.as_list(),
        }

    def _build_sample(
        self,
        biomechanics: Mapping[str, object],
        frame_number: int,
        timestamp: float,
    ) -> RepetitionSample:
        """Build a repetition sample from the current biomechanics payload."""

        active_side = str(biomechanics.get("active_arm_side") or "").strip().lower()
        elbow_angle: float | None
        if active_side == "left":
            elbow_angle = self._as_float(biomechanics.get("left_elbow_angle"))
        elif active_side == "right":
            elbow_angle = self._as_float(biomechanics.get("right_elbow_angle"))
        else:
            elbow_angle = self._as_float(
                biomechanics.get("current_elbow_angle", biomechanics.get("left_elbow_angle"))
            )

        return RepetitionSample(
            frame_number=frame_number,
            timestamp=timestamp,
            elbow_angle=elbow_angle,
            torso_angle=self._as_float(biomechanics.get("torso_angle")),
            body_sway=self._as_float(biomechanics.get("body_sway")),
            movement_direction=str(biomechanics.get("movement_direction") or "Stationary"),
            current_rom=self._as_float(biomechanics.get("range_of_motion")),
        )

    def _finalize_active_rep(self, end_timestamp: float) -> RepetitionRecord | None:
        """Convert the active repetition into a completed record."""

        active_rep = self.active_repetition
        if active_rep is None:
            return None

        samples = active_rep.samples
        if not samples:
            self.active_repetition = None
            self.current_rep_state = MovementPhase.REP_COMPLETED
            return None

        elbow_angles = [sample.elbow_angle for sample in samples if sample.elbow_angle is not None]
        torso_angles = [sample.torso_angle for sample in samples if sample.torso_angle is not None]
        body_swings = [sample.body_sway for sample in samples if sample.body_sway is not None]
        curl_speeds = [sample.curl_speed for sample in samples if sample.curl_speed is not None]

        min_elbow = min(elbow_angles) if elbow_angles else None
        max_elbow = max(elbow_angles) if elbow_angles else None
        range_of_motion = (
            max_elbow - min_elbow if min_elbow is not None and max_elbow is not None else None
        )

        record = RepetitionRecord(
            rep_number=active_rep.rep_number,
            start_frame=active_rep.start_frame,
            end_frame=samples[-1].frame_number,
            duration_seconds=max(0.0, end_timestamp - active_rep.start_timestamp),
            min_elbow_angle=min_elbow,
            max_elbow_angle=max_elbow,
            range_of_motion=range_of_motion,
            average_torso_angle=(sum(torso_angles) / len(torso_angles)) if torso_angles else None,
            average_body_sway=(sum(body_swings) / len(body_swings)) if body_swings else None,
            average_curl_speed=(sum(curl_speeds) / len(curl_speeds)) if curl_speeds else None,
            samples=list(samples),
        )

        self.data_store.add_record(record)
        self.total_reps += 1
        self.current_rep_state = MovementPhase.REP_COMPLETED
        self.active_repetition = None
        return record

    def _calculate_curl_speed(
        self,
        previous_sample: RepetitionSample,
        current_sample: RepetitionSample,
    ) -> float | None:
        """Calculate the instantaneous curl speed between two samples."""

        if previous_sample.elbow_angle is None or current_sample.elbow_angle is None:
            return None

        delta_time = current_sample.timestamp - previous_sample.timestamp
        if delta_time <= 0.0:
            return None

        return abs(current_sample.elbow_angle - previous_sample.elbow_angle) / delta_time

    def _movement_label(self, current_state: MovementPhase, movement_direction: str) -> str:
        """Map internal states to a compact debug movement label."""

        if current_state == MovementPhase.CURLING_UP:
            return "Up"
        if current_state == MovementPhase.LOWERING_DOWN:
            return "Down"
        if current_state == MovementPhase.REP_COMPLETED:
            return "Complete"
        return movement_direction

    def _as_float(self, value: object) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
