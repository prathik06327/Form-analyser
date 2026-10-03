"""Response schemas for the analysis API.

Field names are deliberately camelCase because they mirror the TypeScript
contract the frontend already declares in `frontend/types/analysis.ts`
(`RepAnalysis`, `SessionAnalysis`, `MovementBreakdown`, `TimelineEvent`).
Keeping the names identical on both sides means no translation layer and no
invented field names.
"""

from __future__ import annotations

from pydantic import BaseModel


class RepAnalysis(BaseModel):
    """One completed repetition, mirroring the frontend `RepAnalysis` type."""

    repNumber: int
    formScore: float
    elbowAngle: float | None
    rangeOfMotion: float | None
    tempo: float | None
    elbowStability: float | None
    poseConfidence: float | None
    # A finished repetition is not currently in a movement phase. "idle" is the
    # honest value here; live phase tracking belongs to the (out of scope)
    # real-time frame endpoint.
    phase: str
    mistakes: list[str]
    timestampSec: float


class MovementBreakdown(BaseModel):
    """Session-average movement metrics, mirroring the frontend type.

    `shoulderStability` and `wristAlignment` are always None: the biomechanics
    engine computes no equivalent metric today. They are returned explicitly as
    null so the UI can render an empty row rather than a fabricated number.
    """

    shoulderStability: float | None
    elbowStability: float | None
    rangeOfMotion: float | None
    wristAlignment: float | None
    tempo: float | None


class TimelineEvent(BaseModel):
    """A single chronological form event, mirroring the frontend type."""

    timestampSec: float
    label: str
    kind: str  # "good" | "warning"


class SessionAnalysis(BaseModel):
    """Full result payload for one analyzed video.

    The first five fields are exactly the frontend's `SessionAnalysis` type; the
    remainder carry additional data the pipeline genuinely produces so the
    dashboard does not have to fall back to mock values.
    """

    totalReps: int
    correctReps: int
    averageFormScore: float
    bestScore: float
    reps: list[RepAnalysis]

    movementBreakdown: MovementBreakdown
    timeline: list[TimelineEvent]
    mostCommonIssue: str | None


class LiveFrameResult(BaseModel):
    """Response for one `POST /analyze/frame` call.

    `currentRep` is the rep that just completed on this frame, if any — not a
    running snapshot, since the pipeline only scores completed repetitions.
    """

    sessionId: str
    analysisAvailable: bool
    totalReps: int
    currentRep: RepAnalysis | None
    movementState: str
    mistakes: list[str]
