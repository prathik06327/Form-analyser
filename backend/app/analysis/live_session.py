"""In-memory live-camera session state.

One LiveSession holds exactly the engine instances and running counters the
pipeline needs carried between frames of the same camera stream — nothing per
individual frame is retained. This lets `/analyze/frame` process the frames of
one session incrementally, the same way `run_video_analysis` processes the
frames of one video, just spread across many HTTP requests instead of one loop.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from pathlib import Path

import numpy as np

from app.analysis.frame_pipeline import process_pipeline_frame
from app.analysis.schemas import LiveFrameResult, RepAnalysis
from app.assessment.assessment_engine import AssessmentEngine
from app.biomechanics.biomechanics_engine import BiomechanicsEngine
from app.repetition.repetition_engine import RepetitionEngine
from app.scoring.scoring_engine import ScoringEngine
from app.services.pose_service import PoseService

logger = logging.getLogger("live_session")

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_MODEL_PATH = _BACKEND_ROOT / "yolo11n-pose.pt"


class LiveSession:
    """Per-connection pipeline state for one live camera stream."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.pose_service = PoseService(model_path=_MODEL_PATH)
        self.biomechanics_engine = BiomechanicsEngine()
        self.repetition_engine = RepetitionEngine()
        self.assessment_engine = AssessmentEngine()
        self.scoring_engine = ScoringEngine()

        self.frame_number = 0
        self.total_reps = 0
        self.confidence_window: list[float] = []
        self.started_at = time.time()

    def process_frame(self, frame: np.ndarray) -> LiveFrameResult:
        """Run one live frame through the pipeline and update running state."""

        self.frame_number += 1
        # Live camera IS real-time, so wall-clock timing is correct here —
        # unlike video analysis, there is no faster-than-real-time decoding to
        # correct for.
        timestamp = time.time() - self.started_at
        elapsed = max(timestamp, 0.001)
        approx_fps = max(self.frame_number / elapsed, 1.0)

        result = process_pipeline_frame(
            pose_service=self.pose_service,
            biomechanics_engine=self.biomechanics_engine,
            repetition_engine=self.repetition_engine,
            assessment_engine=self.assessment_engine,
            scoring_engine=self.scoring_engine,
            frame=frame,
            frame_number=self.frame_number,
            timestamp=timestamp,
            fps=approx_fps,
            confidence_window=self.confidence_window,
        )

        rep: RepAnalysis | None = result.completed_rep
        if rep is not None:
            self.total_reps += 1
            logger.info("session=%s rep completed number=%s score=%s", self.session_id, rep.repNumber, rep.formScore)

        logger.info(
            "session=%s frame=%s pose=%s state=%s rep_completed=%s",
            self.session_id,
            self.frame_number,
            result.has_person,
            result.movement_state,
            rep is not None,
        )

        return LiveFrameResult(
            sessionId=self.session_id,
            analysisAvailable=result.has_person,
            totalReps=self.total_reps,
            currentRep=rep,
            movementState=result.movement_state,
            mistakes=list(rep.mistakes) if rep is not None else [],
        )


# KNOWN LIMITATION: sessions live in this process's memory only, same as video
# jobs. A restart drops every live session; fine for local development.
_sessions: dict[str, LiveSession] = {}
_sessions_lock = threading.Lock()


def create_session() -> LiveSession:
    """Start a new live session with a fresh set of pipeline engines."""

    session_id = str(uuid.uuid4())
    session = LiveSession(session_id)
    with _sessions_lock:
        _sessions[session_id] = session
    logger.info("Created analysis session: %s", session_id)
    return session


def get_session(session_id: str) -> LiveSession | None:
    """Return an existing session, or None if the id is unknown."""

    with _sessions_lock:
        return _sessions.get(session_id)
