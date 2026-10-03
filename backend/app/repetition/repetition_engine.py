"""Controller for Phase 3 repetition segmentation and motion tracking."""

from __future__ import annotations

import time
from typing import Mapping

from app.repetition.motion_state import MovementPhase
from app.repetition.repetition_detector import RepetitionDetector, RepetitionDetectionResult
from app.repetition.repetition_tracker import RepetitionTracker


class RepetitionEngine:
    """Run repetition segmentation using only biomechanics output."""

    def __init__(self) -> None:
        self.detector = RepetitionDetector()
        self.tracker = RepetitionTracker()

    def reset(self) -> None:
        """Reset the detector and tracked repetition state."""

        self.detector.reset()
        self.tracker.reset()

    def process_frame(
        self,
        biomechanics: Mapping[str, object] | None,
        frame_number: int | None = None,
        timestamp: float | None = None,
    ) -> dict[str, object]:
        """Advance the repetition pipeline for a single frame."""

        biomechanics = biomechanics or {}
        frame_number = 0 if frame_number is None else frame_number
        timestamp = time.time() if timestamp is None else timestamp

        try:
            detection_result = self.detector.detect(biomechanics)
            self._handle_detection(
                biomechanics=biomechanics,
                frame_number=frame_number,
                timestamp=timestamp,
                detection_result=detection_result,
            )

            session_snapshot = self.tracker.snapshot(detection_result.motion_result, frame_number, timestamp)
            latest_record = self.tracker.data_store.latest()

            session_snapshot.update(
                {
                    "frame_number": frame_number,
                    "repetition_started": detection_result.repetition_started,
                    "repetition_completed": detection_result.repetition_completed,
                    "detector_reason": detection_result.reason,
                    "completed_rep": latest_record.as_dict() if detection_result.repetition_completed and latest_record else None,
                    "latest_completed_rep": latest_record.as_dict() if latest_record else None,
                    "session_summary": self.tracker.data_store.as_list(),
                }
            )
            return session_snapshot
        except Exception as exc:  # pragma: no cover - defensive frame-level guard
            latest_record = self.tracker.data_store.latest()
            return {
                "frame_number": frame_number,
                "current_state": self.tracker.current_rep_state.value if self.tracker else MovementPhase.IDLE.value,
                "previous_state": MovementPhase.IDLE.value,
                "movement_direction": "Stationary",
                "current_rep": self.tracker.current_rep_number if self.tracker else 0,
                "total_reps": self.tracker.get_total_reps() if self.tracker else 0,
                "current_elbow_angle": None,
                "current_rom": None,
                "rep_progress": 0.0,
                "rep_active": False,
                "active_rep_start_frame": None,
                "active_rep_elapsed_frames": 0,
                "active_rep_elapsed_seconds": 0.0,
                "repetition_started": False,
                "repetition_completed": False,
                "detector_reason": "frame_error",
                "completed_rep": None,
                "latest_completed_rep": latest_record.as_dict() if latest_record else None,
                "session_summary": self.tracker.data_store.as_list(),
                "error": str(exc),
            }

    def _handle_detection(
        self,
        biomechanics: Mapping[str, object],
        frame_number: int,
        timestamp: float,
        detection_result: RepetitionDetectionResult,
    ) -> None:
        """Update the tracker based on detector events."""

        if detection_result.repetition_started:
            self.tracker.start_rep(frame_number, timestamp)

        if detection_result.repetition_completed:
            self.tracker.finish_rep(
                biomechanics=biomechanics,
                frame_number=frame_number,
                timestamp=timestamp,
                motion_result=detection_result.motion_result,
            )
            return

        if self.tracker.is_rep_active():
            self.tracker.update_current_rep(
                biomechanics=biomechanics,
                frame_number=frame_number,
                timestamp=timestamp,
                motion_result=detection_result.motion_result,
            )
