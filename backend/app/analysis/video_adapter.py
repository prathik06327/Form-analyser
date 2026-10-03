"""Headless video analysis adapter.

Runs the existing engine chain (pose -> biomechanics -> repetition ->
assessment -> scoring) over a video file with no display calls, so it is safe to
execute inside a server process. This is the same flow `test_video.py` performs
interactively, minus the OpenCV window and console output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import cv2

from app.analysis.frame_pipeline import process_pipeline_frame
from app.analysis.schemas import (
    MovementBreakdown,
    RepAnalysis,
    SessionAnalysis,
    TimelineEvent,
)
from app.assessment.assessment_engine import AssessmentEngine
from app.biomechanics.biomechanics_engine import BiomechanicsEngine
from app.repetition.repetition_engine import RepetitionEngine
from app.scoring.scoring_engine import ScoringEngine
from app.services.pose_service import PoseService

# PoseService resolves its default model path relative to the process working
# directory. Resolve it from this file instead so analysis works regardless of
# where uvicorn was launched from.
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_MODEL_PATH = _BACKEND_ROOT / "yolo11n-pose.pt"

DEFAULT_FPS = 30.0


def _resolve_fps(capture: "cv2.VideoCapture", fps: float | None) -> float:
    """Return a usable frame rate, falling back when metadata is missing."""

    if fps and fps > 0:
        return float(fps)

    reported = capture.get(cv2.CAP_PROP_FPS)
    # Some codecs report 0 or NaN; NaN fails the self-equality check.
    if not reported or reported <= 0 or reported != reported:
        return DEFAULT_FPS
    return float(reported)


def _mean(values: Iterable[float | None]) -> float | None:
    """Average the non-null values, or return None when there are none."""

    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return None
    return round(sum(numbers) / len(numbers), 1)


def _build_timeline(reps: Sequence[RepAnalysis]) -> list[TimelineEvent]:
    """Turn per-rep mistakes into chronological form events."""

    events: list[TimelineEvent] = []
    for rep in reps:
        if rep.mistakes:
            events.extend(
                TimelineEvent(timestampSec=rep.timestampSec, label=mistake, kind="warning")
                for mistake in rep.mistakes
            )
        else:
            events.append(
                TimelineEvent(timestampSec=rep.timestampSec, label="Good form", kind="good")
            )
    return events


def _most_common_issue(reps: Sequence[RepAnalysis]) -> str | None:
    """Return the most frequently detected mistake across the session."""

    counts: dict[str, int] = {}
    for rep in reps:
        for mistake in rep.mistakes:
            counts[mistake] = counts.get(mistake, 0) + 1
    if not counts:
        return None
    return max(counts, key=lambda name: counts[name])


def run_video_analysis(video_path: str, fps: float | None = None) -> SessionAnalysis:
    """Analyze a video file and return the aggregated session result.

    Raises:
        FileNotFoundError: the video path does not exist.
        ValueError: the file exists but OpenCV cannot decode it.
    """

    source = Path(video_path)
    if not source.exists():
        raise FileNotFoundError(f"Video file not found: {source}")

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        # Only the file name, never the full server path — this message is
        # surfaced verbatim to the browser.
        raise ValueError(
            f"Could not decode '{source.name}'. The file may be corrupt or in an unsupported format."
        )

    pose_service = PoseService(model_path=_MODEL_PATH)
    biomechanics_engine = BiomechanicsEngine()
    repetition_engine = RepetitionEngine()
    assessment_engine = AssessmentEngine()
    scoring_engine = ScoringEngine()

    effective_fps = _resolve_fps(capture, fps)
    reps: list[RepAnalysis] = []
    # Per-rep 0-100 metric scores. Kept separately from RepAnalysis because the
    # breakdown is expressed as percentages, while RepAnalysis carries the raw
    # measurements (degrees, seconds).
    metric_history: list[Mapping[str, Any]] = []
    # Keypoint confidences observed since the last completed rep, so each rep
    # reports the detection quality of its own frames.
    confidence_window: list[float] = []
    frame_number = 0

    try:
        while True:
            success, frame = capture.read()
            if not success:
                break

            frame_number += 1

            result = process_pipeline_frame(
                pose_service=pose_service,
                biomechanics_engine=biomechanics_engine,
                repetition_engine=repetition_engine,
                assessment_engine=assessment_engine,
                scoring_engine=scoring_engine,
                frame=frame,
                frame_number=frame_number,
                # Video time, never wall-clock: tempo must describe the lifter,
                # not how fast this machine decoded frames.
                timestamp=frame_number / effective_fps,
                fps=effective_fps,
                confidence_window=confidence_window,
            )

            if result.completed_rep is None:
                continue

            reps.append(result.completed_rep)
            metric_history.append(result.metric_scores or {})
    finally:
        capture.release()

    session_score = (scoring_engine.last_session_score.as_dict() if scoring_engine.last_session_score else {})

    correct_reps = sum(1 for rep in reps if not rep.mistakes)
    average_score = session_score.get("average_rep_score")
    best_score = session_score.get("best_rep")

    return SessionAnalysis(
        totalReps=len(reps),
        correctReps=correct_reps,
        averageFormScore=round(float(average_score or 0.0), 1),
        bestScore=round(float(best_score or 0.0), 1),
        reps=reps,
        movementBreakdown=MovementBreakdown(
            # No shoulder-specific or wrist-alignment metric exists in the
            # biomechanics engine; reported as null rather than invented.
            shoulderStability=None,
            # These are the engine's 0-100 metric scores, not the raw degrees
            # and seconds carried on each RepAnalysis.
            elbowStability=_mean(scores.get("elbow_control") for scores in metric_history),
            rangeOfMotion=_mean(scores.get("rom") for scores in metric_history),
            wristAlignment=None,
            tempo=_mean(scores.get("tempo") for scores in metric_history),
        ),
        timeline=_build_timeline(reps),
        mostCommonIssue=_most_common_issue(reps),
    )
