"""Combine assessment, penalties, bonuses, and weights into scores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.assessment.thresholds import AssessmentThresholds
from app.scoring.bonus_engine import BonusEngine
from app.scoring.grading import GradeEvaluator
from app.scoring.penalty_engine import PenaltyEngine
from app.scoring.score_models import RepScoreResult, ScoreAdjustment
from app.scoring.score_weights import ScoreWeights


@dataclass(slots=True)
class MetricScores:
    """Normalized metric scores used to compute the overall rep score."""

    rom: float | None
    tempo: float | None
    stability: float | None
    body_control: float | None
    elbow_control: float | None

    def as_dict(self) -> dict[str, float | None]:
        """Return a serializable metric score payload."""

        return {
            "rom": self.rom,
            "tempo": self.tempo,
            "stability": self.stability,
            "body_control": self.body_control,
            "elbow_control": self.elbow_control,
        }


class ScoreCalculator:
    """Convert an assessed repetition into a numerical score."""

    def __init__(
        self,
        thresholds: AssessmentThresholds,
        weights: ScoreWeights,
        penalty_engine: PenaltyEngine,
        bonus_engine: BonusEngine,
        grade_evaluator: GradeEvaluator,
    ) -> None:
        self.thresholds = thresholds
        self.weights = weights
        self.penalty_engine = penalty_engine
        self.bonus_engine = bonus_engine
        self.grade_evaluator = grade_evaluator

    def calculate_rep_score(self, assessment_result: Mapping[str, Any]) -> RepScoreResult:
        """Return a scored repetition derived from the assessment payload."""

        repetition = assessment_result.get("repetition") or {}
        movement_quality = assessment_result.get("movement_quality") or {}
        penalties = self.penalty_engine.evaluate(assessment_result)
        bonuses = self.bonus_engine.evaluate_rep_bonuses(assessment_result)

        metric_scores = self._build_metric_scores(repetition, movement_quality)
        weighted_score = self._weighted_score(metric_scores)
        adjusted_score = self._apply_adjustments(weighted_score, penalties, bonuses)
        overall_score = round(max(0.0, min(100.0, adjusted_score)), 2)

        return RepScoreResult(
            rep_number=int(assessment_result.get("rep_number") or 0),
            overall_score=overall_score,
            grade=self.grade_evaluator.grade(overall_score),
            scores=metric_scores.as_dict(),
            penalties=penalties,
            bonuses=bonuses,
            assessment={
                "entries": assessment_result.get("assessment") or [],
                "mistake_count": len(assessment_result.get("assessment") or []),
            },
            movement_quality=dict(movement_quality),
            repetition=dict(repetition),
            metadata={
                "weights": self.weights.as_dict(),
                "base_score": weighted_score,
                "penalty_total": self._total_adjustment(penalties),
                "bonus_total": self._total_adjustment(bonuses),
            },
        )

    def _build_metric_scores(
        self,
        repetition: Mapping[str, Any],
        movement_quality: Mapping[str, Any],
    ) -> MetricScores:
        """Calculate all normalized metric scores on a 0..100 scale."""

        rom = self._scale(movement_quality.get("normalized_rom"), default=movement_quality.get("rom"), threshold=self.thresholds.minimum_rom)
        tempo = self._scale(movement_quality.get("tempo_consistency"))
        stability = self._scale(movement_quality.get("stability"))

        body_sway_control = self._invert_scale(movement_quality.get("average_body_sway"), self.thresholds.maximum_body_sway)
        torso_control = self._invert_scale(movement_quality.get("average_torso_lean"), self.thresholds.maximum_torso_lean_degrees)
        smoothness = self._scale(movement_quality.get("smoothness"))
        body_control = self._average([body_sway_control, torso_control, smoothness])

        extension_control = self._extension_control(repetition)
        symmetry = self._scale(movement_quality.get("symmetry"))
        elbow_control = self._average([extension_control, symmetry])

        return MetricScores(
            rom=rom,
            tempo=tempo,
            stability=stability,
            body_control=body_control,
            elbow_control=elbow_control,
        )

    def _extension_control(self, repetition: Mapping[str, Any]) -> float | None:
        """Score elbow extension quality using the peak elbow angle."""

        max_elbow_angle = self._float(repetition.get("max_elbow_angle"))
        if max_elbow_angle is None:
            return None

        ratio = max_elbow_angle / max(self.thresholds.minimum_extension_angle, 1.0)
        return max(0.0, min(100.0, ratio * 100.0))

    def _weighted_score(self, metric_scores: MetricScores) -> float:
        """Compute the weighted base score using only available metrics."""

        values = {
            "rom": metric_scores.rom,
            "stability": metric_scores.stability,
            "tempo": metric_scores.tempo,
            "elbow_control": metric_scores.elbow_control,
            "body_control": metric_scores.body_control,
        }
        total_weight = 0.0
        weighted_sum = 0.0
        for metric, score in values.items():
            if score is None:
                continue
            weight = getattr(self.weights, metric)
            total_weight += weight
            weighted_sum += score * weight

        if total_weight <= 0.0:
            return 0.0

        return weighted_sum / total_weight

    def _apply_adjustments(
        self,
        base_score: float,
        penalties: list[ScoreAdjustment],
        bonuses: list[ScoreAdjustment],
    ) -> float:
        """Apply penalties and bonuses while keeping the score within 0..100."""

        return base_score - self._total_adjustment(penalties) + self._total_adjustment(bonuses)

    def _total_adjustment(self, adjustments: list[ScoreAdjustment]) -> float:
        """Return the net amount of a list of adjustments."""

        return sum(item.amount for item in adjustments)

    def _scale(self, value: Any, default: Any | None = None, threshold: float | None = None) -> float | None:
        """Normalize a metric-like value into a 0..100 score."""

        numeric_value = self._float(value)
        if numeric_value is None:
            numeric_value = self._float(default)
            if numeric_value is None:
                return None
            if threshold is None or threshold <= 0.0:
                return max(0.0, min(100.0, numeric_value))
            return max(0.0, min(100.0, (numeric_value / threshold) * 100.0))

        if 0.0 <= numeric_value <= 1.0:
            return numeric_value * 100.0
        return max(0.0, min(100.0, numeric_value))

    def _invert_scale(self, value: Any, threshold: float) -> float | None:
        """Return a score where lower raw values produce higher scores."""

        numeric_value = self._float(value)
        if numeric_value is None:
            return None
        if threshold <= 0.0:
            return 100.0
        ratio = max(0.0, min(1.0, 1.0 - (numeric_value / threshold)))
        return ratio * 100.0

    def _average(self, values: list[float | None]) -> float | None:
        """Average the available values in a list."""

        available = [value for value in values if value is not None]
        if not available:
            return None
        return sum(available) / len(available)

    def _float(self, value: Any) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None