"""Exercise-level workout summary generation."""

from __future__ import annotations

from typing import Any, Mapping

from app.feedback.feedback_models import ExerciseSummary
from app.scoring.grading import GradeEvaluator


class ExerciseSummaryBuilder:
    """Build a short workout overview without coaching advice."""

    def __init__(self, grade_evaluator: GradeEvaluator | None = None) -> None:
        self.grade_evaluator = grade_evaluator or GradeEvaluator()

    def build(self, session_score: Mapping[str, Any] | Any, exercise_name: str | None = None) -> ExerciseSummary:
        """Return a concise summary for the current exercise."""

        session_data = self._mapping(session_score)
        statistics = self._mapping(session_data.get("statistics"))
        rep_scores = self._rep_scores(session_data)

        average_score = self._float(
            session_data.get("average_rep_score")
            or statistics.get("average_score")
            or self._average_score(rep_scores)
        )
        grade = str(session_data.get("grade") or session_data.get("workout_grade") or self.grade_evaluator.grade(average_score))

        return ExerciseSummary(
            exercise=self._exercise_name(session_data, exercise_name),
            total_reps=int(session_data.get("total_reps") or len(rep_scores)),
            average_score=round(average_score, 2) if average_score is not None else None,
            grade=grade,
            consistency=self._float(session_data.get("consistency_score") or statistics.get("consistency", {}).get("score")),
        )

    def _exercise_name(self, session_data: Mapping[str, Any], exercise_name: str | None) -> str:
        """Resolve a usable exercise name for the report."""

        if exercise_name:
            return exercise_name

        metadata = self._mapping(session_data.get("metadata"))
        for key in ("exercise", "exercise_name", "movement", "workout"):
            value = metadata.get(key) or session_data.get(key)
            if value:
                return str(value)

        return "Bicep Curl"

    def _rep_scores(self, session_data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        """Return a normalized list of repetition score payloads."""

        rep_scores = session_data.get("rep_scores") or []
        if not isinstance(rep_scores, list):
            return []

        normalized: list[Mapping[str, Any]] = []
        for rep in rep_scores:
            if hasattr(rep, "as_dict"):
                normalized.append(rep.as_dict())
            elif isinstance(rep, Mapping):
                normalized.append(rep)
        return normalized

    def _average_score(self, rep_scores: list[Mapping[str, Any]]) -> float | None:
        """Compute the mean score from repetition payloads."""

        scores = []
        for rep in rep_scores:
            score = self._float(rep.get("overall_score"))
            if score is not None:
                scores.append(score)
        if not scores:
            return None
        return sum(scores) / len(scores)

    def _mapping(self, value: Any) -> dict[str, Any]:
        """Normalize a mapping or dataclass-like object into a dictionary."""

        if value is None:
            return {}
        if hasattr(value, "as_dict"):
            return dict(value.as_dict())
        if isinstance(value, Mapping):
            return dict(value)
        return {}

    def _float(self, value: Any) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None