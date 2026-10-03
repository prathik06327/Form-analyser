"""Aggregate repetition scores into session-level statistics."""

from __future__ import annotations

from statistics import fmean
from typing import Any, Iterable, Mapping

from app.scoring.consistency_analyzer import ConsistencyAnalyzer
from app.scoring.grading import GradeEvaluator
from app.scoring.score_models import RepScoreResult, SessionScoreResult


class SessionScoreCalculator:
    """Compute session-level score statistics from scored repetitions."""

    def __init__(self, consistency_analyzer: ConsistencyAnalyzer, grade_evaluator: GradeEvaluator) -> None:
        self.consistency_analyzer = consistency_analyzer
        self.grade_evaluator = grade_evaluator

    def calculate(self, rep_scores: Iterable[RepScoreResult], session_bonuses: Iterable[Mapping[str, Any]] | None = None) -> SessionScoreResult:
        """Return aggregate session statistics for all scored repetitions."""

        rep_scores = list(rep_scores)
        total_reps = len(rep_scores)
        rep_values = [rep.overall_score for rep in rep_scores]

        average_rep_score = fmean(rep_values) if rep_values else 0.0
        best_rep = max(rep_values) if rep_values else None
        worst_rep = min(rep_values) if rep_values else None

        consistency_result = self.consistency_analyzer.analyze([rep.as_dict() for rep in rep_scores])
        consistency_score = consistency_result.score

        workout_score = self._workout_score(average_rep_score, consistency_score, session_bonuses)

        statistics = {
            "consistency": consistency_result.as_dict(),
            "rep_score_count": total_reps,
        }

        return SessionScoreResult(
            total_reps=total_reps,
            average_rep_score=round(average_rep_score, 2),
            best_rep=round(best_rep, 2) if best_rep is not None else None,
            worst_rep=round(worst_rep, 2) if worst_rep is not None else None,
            consistency_score=round(consistency_score, 2),
            workout_score=round(workout_score, 2),
            grade=self.grade_evaluator.grade(workout_score),
            rep_scores=rep_scores,
            statistics=statistics,
        )

    def _workout_score(
        self,
        average_rep_score: float,
        consistency_score: float,
        session_bonuses: Iterable[Mapping[str, Any]] | None,
    ) -> float:
        """Blend average rep score, consistency, and session bonuses."""

        base = (average_rep_score * 0.8) + (consistency_score * 0.2)
        bonus_total = 0.0
        if session_bonuses is not None:
            for item in session_bonuses:
                if not isinstance(item, Mapping):
                    continue
                try:
                    bonus_total += float(item.get("amount") or 0.0)
                except (TypeError, ValueError):
                    continue
        return max(0.0, min(100.0, base + bonus_total))