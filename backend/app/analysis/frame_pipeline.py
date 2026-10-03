"""Shared single-frame processing step.

Both `/analyze/video` (many frames, one file) and `/analyze/frame` (one frame
per HTTP request, state kept in a session) need to run an image through the
exact same pose -> biomechanics -> repetition -> assessment -> scoring chain.
This is that one shared step, extracted so neither endpoint duplicates it.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from app.analysis.schemas import RepAnalysis
from app.assessment.assessment_engine import AssessmentEngine
from app.biomechanics.biomechanics_engine import BiomechanicsEngine
from app.repetition.repetition_engine import RepetitionEngine
from app.scoring.scoring_engine import ScoringEngine
from app.services.pose_service import PoseService


def frame_confidence(confidences: Mapping[str, float]) -> float | None:
    """Mean keypoint confidence for a single frame, as a percentage."""

    values = [float(value) for value in confidences.values() if value is not None]
    if not values:
        return None
    return (sum(values) / len(values)) * 100.0


def round_or_none(value: Any) -> float | None:
    """Round a numeric value to one decimal place, preserving None."""

    if value is None:
        return None
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


def build_rep(
    assessment: Mapping[str, Any],
    score_payload: Mapping[str, Any],
    completed_rep: Mapping[str, Any],
    confidences: list[float],
    fps: float,
) -> RepAnalysis:
    """Map one scored repetition onto the frontend's RepAnalysis contract."""

    rep_score = score_payload.get("rep_score") or {}
    metric_scores = rep_score.get("scores") or {}
    mistakes = [
        str(entry.get("mistake"))
        for entry in (assessment.get("assessment") or [])
        if entry.get("mistake")
    ]
    end_frame = completed_rep.get("end_frame") or 0

    return RepAnalysis(
        repNumber=int(rep_score.get("rep_number") or completed_rep.get("rep_number") or 0),
        formScore=round(float(rep_score.get("overall_score") or 0.0), 1),
        elbowAngle=round_or_none(completed_rep.get("min_elbow_angle")),
        rangeOfMotion=round_or_none(completed_rep.get("range_of_motion")),
        tempo=round_or_none(completed_rep.get("duration_seconds")),
        elbowStability=round_or_none(metric_scores.get("elbow_control")),
        poseConfidence=(sum(confidences) / len(confidences)) if confidences else None,
        phase="idle",
        mistakes=mistakes,
        timestampSec=round(float(end_frame) / fps, 1),
    )


class FrameResult:
    """Outcome of processing exactly one frame through the pipeline."""

    __slots__ = ("has_person", "completed_rep", "metric_scores", "movement_state")

    def __init__(
        self,
        has_person: bool,
        completed_rep: RepAnalysis | None,
        metric_scores: dict[str, Any] | None,
        movement_state: str,
    ) -> None:
        self.has_person = has_person
        self.completed_rep = completed_rep
        self.metric_scores = metric_scores
        self.movement_state = movement_state


def process_pipeline_frame(
    *,
    pose_service: PoseService,
    biomechanics_engine: BiomechanicsEngine,
    repetition_engine: RepetitionEngine,
    assessment_engine: AssessmentEngine,
    scoring_engine: ScoringEngine,
    frame: np.ndarray,
    frame_number: int,
    timestamp: float,
    fps: float,
    confidence_window: list[float],
) -> FrameResult:
    """Run one frame through the full chain, scoring a rep only if one just completed.

    `confidence_window` is mutated in place: this frame's confidence is
    appended, and it is cleared here whenever a rep completes (the caller does
    not need to manage it).
    """

    detection = pose_service.detect_pose(frame)
    conf = frame_confidence(detection.confidences)
    if conf is not None:
        confidence_window.append(conf)

    measurements = biomechanics_engine.process_frame(detection.keypoints)
    repetition_info = repetition_engine.process_frame(
        measurements,
        frame_number=frame_number,
        # Never wall-clock: tempo must describe the lifter, not request timing.
        timestamp=timestamp,
    )

    movement_state = str(repetition_info.get("current_state", "IDLE"))
    completed = repetition_info.get("completed_rep")
    if completed is None:
        return FrameResult(detection.has_person, None, None, movement_state)

    assessment = assessment_engine.assess_rep_dict(completed)
    score_payload = scoring_engine.process_assessment(assessment)
    rep = build_rep(
        assessment=assessment,
        score_payload=score_payload,
        completed_rep=completed,
        confidences=list(confidence_window),
        fps=fps,
    )
    confidence_window.clear()
    metric_scores = (score_payload.get("rep_score") or {}).get("scores") or {}
    return FrameResult(detection.has_person, rep, metric_scores, movement_state)
