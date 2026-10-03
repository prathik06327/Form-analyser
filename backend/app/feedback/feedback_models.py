"""Reusable response models for workout feedback and session analytics."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class RepetitionSnapshot:
    """Compact summary of one repetition used in reports."""

    rep_number: int
    score: float | None = None
    grade: str = ""
    duration_seconds: float | None = None
    rom: float | None = None
    tempo: float | None = None
    stability: float | None = None
    mistake_count: int = 0
    mistakes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable snapshot payload."""

        return asdict(self)


@dataclass(slots=True)
class SessionStatistics:
    """Aggregate workout statistics derived from scored repetitions."""

    total_repetitions: int
    workout_duration_seconds: float | None = None
    average_repetition_duration_seconds: float | None = None
    average_score: float | None = None
    best_repetition: RepetitionSnapshot | None = None
    worst_repetition: RepetitionSnapshot | None = None
    consistency_score: float | None = None
    highest_rom: float | None = None
    lowest_rom: float | None = None
    average_rom: float | None = None
    average_tempo: float | None = None
    average_stability: float | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable statistics payload."""

        return asdict(self)


@dataclass(slots=True)
class MistakeOccurrence:
    """Frequency summary for one detected form mistake."""

    mistake: str
    occurrences: int
    percentage_affected: float
    first_occurrence: int | None = None
    last_occurrence: int | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable occurrence payload."""

        return asdict(self)


@dataclass(slots=True)
class MistakeSummary:
    """Aggregate mistake information for the full workout."""

    most_common_mistake: MistakeOccurrence | None
    mistakes: list[MistakeOccurrence] = field(default_factory=list)
    total_unique_mistakes: int = 0
    total_mistake_occurrences: int = 0

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable mistake summary payload."""

        return asdict(self)


@dataclass(slots=True)
class ExerciseSummary:
    """High-level workout summary for the current exercise."""

    exercise: str
    total_reps: int
    average_score: float | None
    grade: str
    consistency: float | None

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable exercise summary payload."""

        return asdict(self)


@dataclass(slots=True)
class ImprovementArea:
    """One strength or weakness detected during the workout."""

    title: str
    kind: str
    detail: str
    score: float | None = None
    occurrences: int | None = None
    metric: str | None = None
    related_mistake: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable improvement area payload."""

        return asdict(self)


@dataclass(slots=True)
class ImprovementAreaSummary:
    """Structured strengths and weaknesses for the workout."""

    strengths: list[ImprovementArea] = field(default_factory=list)
    weaknesses: list[ImprovementArea] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable improvement summary payload."""

        return asdict(self)


@dataclass(slots=True)
class RecommendationItem:
    """A deterministic coaching recommendation."""

    message: str
    trigger: str = ""
    priority: int = 0

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable recommendation payload."""

        return asdict(self)


@dataclass(slots=True)
class FeedbackReport:
    """Complete structured workout report."""

    session_statistics: SessionStatistics
    exercise_summary: ExerciseSummary
    mistake_summary: MistakeSummary
    improvement_areas: ImprovementAreaSummary
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable report payload."""

        return {
            "session_statistics": self.session_statistics.as_dict(),
            "exercise_summary": self.exercise_summary.as_dict(),
            "mistake_summary": self.mistake_summary.as_dict(),
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "improvement_areas": self.improvement_areas.as_dict(),
        }