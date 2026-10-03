"""Convert detected assessment mistakes into score deductions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.assessment.severity import Severity
from app.scoring.score_models import ScoreAdjustment


@dataclass(slots=True, frozen=True)
class PenaltyRule:
    """Base penalty mapping for one mistake type."""

    mistake: str
    base_penalty: float
    category: str


class PenaltyEngine:
    """Apply severity-scaled deductions for detected mistakes."""

    severity_multipliers = {
        Severity.LOW.value: 0.35,
        Severity.MEDIUM.value: 0.65,
        Severity.HIGH.value: 1.0,
    }

    def __init__(self, rules: list[PenaltyRule] | None = None) -> None:
        self.rules = rules or self._default_rules()

    def evaluate(self, assessment: Mapping[str, Any]) -> list[ScoreAdjustment]:
        """Convert the assessment mistakes into penalty adjustments."""

        penalties: list[ScoreAdjustment] = []
        mistakes = assessment.get("assessment") or []
        if not isinstance(mistakes, list):
            return penalties

        for mistake in mistakes:
            if not isinstance(mistake, Mapping):
                continue

            mistake_name = str(mistake.get("mistake") or "").strip()
            if not mistake_name:
                continue

            rule = self._rule_for(mistake_name)
            if rule is None:
                continue

            severity = str(mistake.get("severity") or Severity.LOW.value).upper()
            multiplier = self.severity_multipliers.get(severity, self.severity_multipliers[Severity.LOW.value])
            deduction = round(rule.base_penalty * multiplier, 2)

            penalties.append(
                ScoreAdjustment(
                    reason=mistake_name,
                    amount=deduction,
                    category=rule.category,
                    severity=severity,
                    evidence=dict(mistake.get("evidence") or {}),
                )
            )

        return penalties

    def _rule_for(self, mistake: str) -> PenaltyRule | None:
        """Return the configured penalty rule for a mistake."""

        for rule in self.rules:
            if rule.mistake == mistake:
                return rule
        return None

    def _default_rules(self) -> list[PenaltyRule]:
        """Create the default mistake-to-penalty mapping."""

        return [
            PenaltyRule("Partial Curl", 15.0, "rom"),
            PenaltyRule("Incomplete Extension", 10.0, "elbow_control"),
            PenaltyRule("Excessive Body Swing", 10.0, "body_control"),
            PenaltyRule("Excessive Torso Lean", 8.0, "body_control"),
            PenaltyRule("Elbow Drift", 12.0, "elbow_control"),
            PenaltyRule("Wrist Instability", 6.0, "elbow_control"),
            PenaltyRule("Fast Lowering", 8.0, "tempo"),
            PenaltyRule("Jerky Motion", 6.0, "tempo"),
            PenaltyRule("Inconsistent Tempo", 5.0, "tempo"),
        ]