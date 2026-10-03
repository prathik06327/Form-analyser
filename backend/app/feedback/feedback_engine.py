"""Controller for Phase 6 feedback and session analytics."""

from __future__ import annotations

from typing import Any, Mapping

from app.feedback.exercise_summary import ExerciseSummaryBuilder
from app.feedback.improvement_engine import ImprovementEngine
from app.feedback.mistake_summary import MistakeSummaryAnalyzer
from app.feedback.recommendation_engine import RecommendationEngine
from app.feedback.report_generator import ReportGenerator
from app.feedback.session_statistics import SessionStatisticsAnalyzer


class FeedbackEngine:
    """Generate deterministic workout feedback from session score outputs."""

    def __init__(self) -> None:
        self.session_statistics_analyzer = SessionStatisticsAnalyzer()
        self.mistake_summary_analyzer = MistakeSummaryAnalyzer()
        self.exercise_summary_builder = ExerciseSummaryBuilder()
        self.improvement_engine = ImprovementEngine()
        self.recommendation_engine = RecommendationEngine()
        self.report_generator = ReportGenerator()

    def generate_feedback(self, session_score: Mapping[str, Any] | Any, exercise_name: str | None = None) -> dict[str, Any]:
        """Run the full analytics pipeline and return a structured report."""

        session_statistics = self.session_statistics_analyzer.calculate(session_score)
        mistake_summary = self.mistake_summary_analyzer.summarize(session_score)
        exercise_summary = self.exercise_summary_builder.build(session_score, exercise_name=exercise_name)
        improvement_areas = self.improvement_engine.analyze(session_statistics, mistake_summary)
        recommendations = self.recommendation_engine.generate(improvement_areas, mistake_summary)
        report = self.report_generator.generate(
            session_statistics=session_statistics,
            exercise_summary=exercise_summary,
            mistake_summary=mistake_summary,
            improvement_areas=improvement_areas,
            recommendations=recommendations,
        )
        return report.as_dict()

    def process_session(self, session_score: Mapping[str, Any] | Any, exercise_name: str | None = None) -> dict[str, Any]:
        """Alias for generate_feedback to match controller-style call sites."""

        return self.generate_feedback(session_score, exercise_name=exercise_name)