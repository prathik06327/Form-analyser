"""Controller for Phase 5 scoring and session evaluation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from app.assessment.thresholds import AssessmentThresholds, get_default_thresholds
from app.scoring.bonus_engine import BonusEngine
from app.scoring.consistency_analyzer import ConsistencyAnalyzer
from app.scoring.grading import GradeEvaluator
from app.scoring.penalty_engine import PenaltyEngine
from app.scoring.score_calculator import ScoreCalculator
from app.scoring.score_models import RepScoreResult, SessionScoreResult
from app.scoring.score_weights import ScoreWeights, get_default_weights
from app.scoring.session_score import SessionScoreCalculator


class ScoringEngine:
    """Score assessed repetitions and maintain session-level scoring state."""

    def __init__(
        self,
        thresholds: AssessmentThresholds | None = None,
        weights: ScoreWeights | None = None,
    ) -> None:
        self.thresholds = thresholds or get_default_thresholds()
        self.weights = weights or get_default_weights()
        self.grade_evaluator = GradeEvaluator()
        self.penalty_engine = PenaltyEngine()
        self.bonus_engine = BonusEngine()
        self.score_calculator = ScoreCalculator(
            thresholds=self.thresholds,
            weights=self.weights,
            penalty_engine=self.penalty_engine,
            bonus_engine=self.bonus_engine,
            grade_evaluator=self.grade_evaluator,
        )
        self.consistency_analyzer = ConsistencyAnalyzer()
        self.session_score_calculator = SessionScoreCalculator(self.consistency_analyzer, self.grade_evaluator)
        self.rep_scores: list[RepScoreResult] = []
        self.last_session_score: SessionScoreResult | None = None

    def process_assessment(self, assessment_result: Mapping[str, Any]) -> dict[str, Any]:
        """Score one assessed repetition and update the running session summary."""

        rep_score = self.score_calculator.calculate_rep_score(assessment_result)
        self.rep_scores.append(rep_score)

        session_bonuses = self.bonus_engine.evaluate_session_bonuses(
            {
                "consistency_score": self._last_consistency_score(),
                "total_reps": len(self.rep_scores),
            }
        )
        session_score = self.session_score_calculator.calculate(self.rep_scores, session_bonuses)
        self.last_session_score = session_score

        return {
            "rep_score": rep_score.as_dict(),
            "session_score": self._session_payload(session_score, session_bonuses),
        }

    def reset(self) -> None:
        """Clear all session scoring state."""

        self.rep_scores.clear()
        self.last_session_score = None

    def _last_consistency_score(self) -> float:
        """Return the current consistency score for session-bonus evaluation."""

        if not self.rep_scores:
            return 100.0
        consistency = self.consistency_analyzer.analyze([rep.as_dict() for rep in self.rep_scores])
        return consistency.score

    def _session_payload(self, session_score: SessionScoreResult, session_bonuses: list[Any]) -> dict[str, Any]:
        """Return a serializable session scoring payload."""

        payload = session_score.as_dict()
        payload["session_bonuses"] = [bonus.as_dict() if hasattr(bonus, "as_dict") else asdict(bonus) for bonus in session_bonuses]
        payload["workout_grade"] = payload.get("grade")
        return payload