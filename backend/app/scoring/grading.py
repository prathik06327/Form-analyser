"""Performance grading for numerical scores."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GradeBand:
    """A numeric grade band."""

    lower: float
    upper: float
    label: str


class GradeEvaluator:
    """Convert numerical scores into performance grades."""

    def __init__(self, bands: list[GradeBand] | None = None) -> None:
        self.bands = bands or [
            GradeBand(95.0, 100.0, "Excellent"),
            GradeBand(85.0, 94.99, "Very Good"),
            GradeBand(75.0, 84.99, "Good"),
            GradeBand(60.0, 74.99, "Fair"),
            GradeBand(0.0, 59.99, "Needs Improvement"),
        ]

    def grade(self, score: float | None) -> str:
        """Return a label for the supplied score."""

        numeric_score = 0.0 if score is None else max(0.0, min(100.0, score))
        for band in self.bands:
            if band.lower <= numeric_score <= band.upper:
                return band.label
        return self.bands[-1].label