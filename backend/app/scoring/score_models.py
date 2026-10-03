"""Reusable data models for Phase 5 scoring outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ScoreAdjustment:
    """A penalty or bonus applied to a score."""

    reason: str
    amount: float
    category: str = ""
    severity: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable adjustment payload."""

        return asdict(self)


@dataclass(slots=True)
class RepScoreResult:
    """Structured score output for a single repetition."""

    rep_number: int
    overall_score: float
    grade: str
    scores: dict[str, float]
    penalties: list[ScoreAdjustment] = field(default_factory=list)
    bonuses: list[ScoreAdjustment] = field(default_factory=list)
    assessment: dict[str, Any] = field(default_factory=dict)
    movement_quality: dict[str, Any] = field(default_factory=dict)
    repetition: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable rep score payload."""

        return {
            "rep_number": self.rep_number,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "scores": self.scores,
            "penalties": [item.as_dict() for item in self.penalties],
            "bonuses": [item.as_dict() for item in self.bonuses],
            "assessment": self.assessment,
            "movement_quality": self.movement_quality,
            "repetition": self.repetition,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class SessionScoreResult:
    """Structured score output for a full workout session."""

    total_reps: int
    average_rep_score: float
    best_rep: float | None
    worst_rep: float | None
    consistency_score: float
    workout_score: float
    grade: str
    rep_scores: list[RepScoreResult] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable session score payload."""

        return {
            "total_reps": self.total_reps,
            "average_rep_score": self.average_rep_score,
            "best_rep": self.best_rep,
            "worst_rep": self.worst_rep,
            "consistency_score": self.consistency_score,
            "workout_score": self.workout_score,
            "grade": self.grade,
            "rep_scores": [rep.as_dict() for rep in self.rep_scores],
            "statistics": self.statistics,
        }