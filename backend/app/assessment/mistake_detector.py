"""Mistake detection for completed repetition assessments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.assessment.movement_quality import MovementQualityMetrics
from app.assessment.rule_engine import RuleOutcome, RuleEngine
from app.assessment.severity import Severity, SeverityEvaluator
from app.assessment.thresholds import AssessmentThresholds


@dataclass(slots=True)
class DetectedMistake:
    """A single detected form mistake with evidence and severity."""

    mistake: str
    severity: Severity
    evidence: dict[str, Any]
    rule_name: str
    metric_name: str | None = None
    observed_value: float | None = None
    threshold_value: float | None = None
    ratio: float | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable mistake description."""

        return {
            "mistake": self.mistake,
            "severity": self.severity.value,
            "evidence": self.evidence,
            "rule_name": self.rule_name,
            "metric_name": self.metric_name,
            "observed_value": self.observed_value,
            "threshold_value": self.threshold_value,
            "ratio": self.ratio,
        }


class MistakeDetector:
    """Convert rule outcomes into detected mistakes with severity labels."""

    def __init__(self, severity_evaluator: SeverityEvaluator | None = None) -> None:
        self.severity_evaluator = severity_evaluator or SeverityEvaluator()

    def detect(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        rule_engine: RuleEngine,
    ) -> list[DetectedMistake]:
        """Return all mistakes detected in the current repetition."""

        mistakes: list[DetectedMistake] = []
        for outcome in rule_engine.evaluate(repetition, movement_quality):
            mistakes.append(self._to_mistake(outcome))
        return mistakes

    def _to_mistake(self, outcome: RuleOutcome) -> DetectedMistake:
        """Convert a rule outcome into a detected mistake."""

        severity = self.severity_evaluator.from_ratio(outcome.ratio)

        return DetectedMistake(
            mistake=outcome.mistake,
            severity=severity,
            evidence=outcome.evidence,
            rule_name=outcome.rule_name,
            metric_name=outcome.metric_name,
            observed_value=outcome.observed_value,
            threshold_value=outcome.threshold_value,
            ratio=outcome.ratio,
        )
