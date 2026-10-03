"""Combine all Phase 6 analytics into a structured workout report."""

from __future__ import annotations

from typing import Any, Mapping

from app.feedback.feedback_models import (
    ExerciseSummary,
    FeedbackReport,
    ImprovementAreaSummary,
    MistakeSummary,
    RecommendationItem,
    SessionStatistics,
)


class ReportGenerator:
    """Build the final structured session report."""

    def generate(
        self,
        session_statistics: SessionStatistics | Mapping[str, Any],
        exercise_summary: Mapping[str, Any] | Any,
        mistake_summary: MistakeSummary | Mapping[str, Any],
        improvement_areas: ImprovementAreaSummary | Mapping[str, Any],
        recommendations: list[RecommendationItem] | list[Mapping[str, Any]],
    ) -> FeedbackReport:
        """Return a complete workout report object."""

        stats = self._model(session_statistics, SessionStatistics)
        mistakes = self._model(mistake_summary, MistakeSummary)
        improvements = self._model(improvement_areas, ImprovementAreaSummary)
        summary = self._model(exercise_summary, ExerciseSummary)

        recommendation_messages = [
            item.message if hasattr(item, "message") else str(item.get("message") or "")
            for item in recommendations
            if (item.message if hasattr(item, "message") else item.get("message"))
        ]

        return FeedbackReport(
            session_statistics=stats,
            exercise_summary=summary,
            mistake_summary=mistakes,
            improvement_areas=improvements,
            strengths=[area.title for area in improvements.strengths],
            weaknesses=[area.title for area in improvements.weaknesses],
            recommendations=recommendation_messages,
        )

    def _model(self, value: Any, model_type: Any) -> Any:
        """Normalize a dataclass-like object into the requested model type."""

        if isinstance(value, model_type):
            return value
        if hasattr(value, "as_dict"):
            payload = value.as_dict()
        elif isinstance(value, Mapping):
            payload = dict(value)
        else:
            payload = {}
        return model_type(**payload)