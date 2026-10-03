"""Reward excellent repetitions with configurable score bonuses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.scoring.score_models import ScoreAdjustment


@dataclass(slots=True, frozen=True)
class BonusRule:
    """Base bonus definition for one reward condition."""

    reason: str
    amount: float
    category: str


class BonusEngine:
    """Apply configurable bonuses to rep and session scores."""

    def __init__(self, rep_rules: list[BonusRule] | None = None, session_rules: list[BonusRule] | None = None) -> None:
        self.rep_rules = rep_rules or self._default_rep_rules()
        self.session_rules = session_rules or self._default_session_rules()

    def evaluate_rep_bonuses(self, assessment: Mapping[str, Any]) -> list[ScoreAdjustment]:
        """Return bonuses for a single completed repetition."""

        movement_quality = assessment.get("movement_quality") or {}
        repetition = assessment.get("repetition") or {}

        bonuses: list[ScoreAdjustment] = []
        normalized_rom = self._float(movement_quality.get("normalized_rom"))
        stability = self._float(movement_quality.get("stability"))
        tempo_consistency = self._float(movement_quality.get("tempo_consistency"))
        smoothness = self._float(movement_quality.get("smoothness"))

        if normalized_rom is not None and normalized_rom >= 0.95:
            bonuses.append(self._build_bonus("Excellent ROM", 3.0, "rom", {"normalized_rom": normalized_rom}))
        if stability is not None and stability >= 0.95:
            bonuses.append(self._build_bonus("Excellent Stability", 2.0, "stability", {"stability": stability}))
        if tempo_consistency is not None and tempo_consistency >= 0.95:
            bonuses.append(self._build_bonus("Perfect Tempo", 2.0, "tempo", {"tempo_consistency": tempo_consistency}))
        if smoothness is not None and smoothness >= 0.95:
            bonuses.append(self._build_bonus("Smooth Motion", 2.0, "body_control", {"smoothness": smoothness}))

        if repetition.get("range_of_motion") is not None and normalized_rom is not None and normalized_rom >= 0.98:
            bonuses.append(self._build_bonus("Complete Range", 2.0, "rom", {"range_of_motion": repetition.get("range_of_motion")}))

        return bonuses

    def evaluate_session_bonuses(self, session_summary: Mapping[str, Any]) -> list[ScoreAdjustment]:
        """Return session-level bonuses such as consistent repetitions."""

        bonuses: list[ScoreAdjustment] = []
        consistency_score = self._float(session_summary.get("consistency_score"))
        total_reps = int(session_summary.get("total_reps") or 0)

        if consistency_score is not None and consistency_score >= 95.0 and total_reps >= 3:
            bonuses.append(
                self._build_bonus(
                    "Consistent Repetitions",
                    3.0,
                    "session",
                    {"consistency_score": consistency_score, "total_reps": total_reps},
                )
            )

        return bonuses

    def _build_bonus(self, reason: str, amount: float, category: str, evidence: dict[str, Any]) -> ScoreAdjustment:
        """Create a standardized bonus adjustment."""

        return ScoreAdjustment(reason=reason, amount=amount, category=category, severity="BONUS", evidence=evidence)

    def _default_rep_rules(self) -> list[BonusRule]:
        """Default rep-level bonus rules."""

        return [
            BonusRule("Excellent ROM", 3.0, "rom"),
            BonusRule("Excellent Stability", 2.0, "stability"),
            BonusRule("Perfect Tempo", 2.0, "tempo"),
            BonusRule("Smooth Motion", 2.0, "body_control"),
        ]

    def _default_session_rules(self) -> list[BonusRule]:
        """Default session-level bonus rules."""

        return [BonusRule("Consistent Repetitions", 3.0, "session")]

    def _float(self, value: Any) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None