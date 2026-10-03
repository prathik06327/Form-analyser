"""Modular rule evaluation for completed repetition assessments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from app.assessment.movement_quality import MovementQualityMetrics
from app.assessment.thresholds import AssessmentThresholds


@dataclass(slots=True)
class RuleOutcome:
    """Result produced by a single assessment rule."""

    mistake: str
    triggered: bool
    evidence: dict[str, Any]
    rule_name: str
    metric_name: str | None = None
    observed_value: float | None = None
    threshold_value: float | None = None
    ratio: float | None = None


@dataclass(slots=True)
class AssessmentRule:
    """Reusable rule definition."""

    name: str
    mistake: str
    evaluator: Callable[[Mapping[str, Any], MovementQualityMetrics, AssessmentThresholds], RuleOutcome | None]


class RuleEngine:
    """Evaluate modular form-assessment rules against a completed repetition."""

    def __init__(self, thresholds: AssessmentThresholds) -> None:
        self.thresholds = thresholds
        self.rules = self._build_rules()

    def evaluate(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
    ) -> list[RuleOutcome]:
        """Run every configured rule and return the triggered outcomes."""

        outcomes: list[RuleOutcome] = []
        for rule in self.rules:
            outcome = rule.evaluator(repetition, movement_quality, self.thresholds)
            if outcome is not None and outcome.triggered:
                outcomes.append(outcome)
        return outcomes

    def _build_rules(self) -> list[AssessmentRule]:
        """Create the default assessment rule set."""

        return [
            AssessmentRule("Partial Curl", "Partial Curl", self._partial_curl_rule),
            AssessmentRule("Incomplete Extension", "Incomplete Extension", self._incomplete_extension_rule),
            AssessmentRule("Excessive Body Swing", "Excessive Body Swing", self._body_swing_rule),
            AssessmentRule("Excessive Torso Lean", "Excessive Torso Lean", self._torso_lean_rule),
            AssessmentRule("Elbow Drift", "Elbow Drift", self._elbow_drift_rule),
            AssessmentRule("Wrist Instability", "Wrist Instability", self._wrist_instability_rule),
            AssessmentRule("Fast Lowering", "Fast Lowering", self._fast_lowering_rule),
            AssessmentRule("Jerky Motion", "Jerky Motion", self._jerky_motion_rule),
            AssessmentRule("Inconsistent Tempo", "Inconsistent Tempo", self._tempo_consistency_rule),
        ]

    def _partial_curl_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        rom = movement_quality.rom
        if rom is None or rom >= thresholds.minimum_rom:
            return None
        deficit = thresholds.minimum_rom - rom
        ratio = deficit / max(thresholds.minimum_rom, 1.0)
        return self._outcome("Partial Curl", True, "rom", rom, thresholds.minimum_rom, ratio, {
            "rom": rom,
            "minimum_rom": thresholds.minimum_rom,
            "minimum_reached": False,
        })

    def _incomplete_extension_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        max_elbow = self._float(repetition.get("max_elbow_angle"))
        if max_elbow is None or max_elbow >= thresholds.minimum_extension_angle:
            return None
        deficit = thresholds.minimum_extension_angle - max_elbow
        ratio = deficit / max(thresholds.minimum_extension_angle, 1.0)
        return self._outcome("Incomplete Extension", True, "max_elbow_angle", max_elbow, thresholds.minimum_extension_angle, ratio, {
            "max_elbow_angle": max_elbow,
            "minimum_extension_angle": thresholds.minimum_extension_angle,
        })

    def _body_swing_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        body_sway = movement_quality.average_body_sway
        if body_sway is None or body_sway <= thresholds.maximum_body_sway:
            return None
        excess = body_sway - thresholds.maximum_body_sway
        ratio = excess / max(thresholds.maximum_body_sway, 1.0)
        return self._outcome("Excessive Body Swing", True, "body_sway", body_sway, thresholds.maximum_body_sway, ratio, {
            "average_body_sway": body_sway,
            "maximum_body_sway": thresholds.maximum_body_sway,
        })

    def _torso_lean_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        torso_lean = movement_quality.average_torso_lean
        if torso_lean is None or torso_lean <= thresholds.maximum_torso_lean_degrees:
            return None
        excess = torso_lean - thresholds.maximum_torso_lean_degrees
        ratio = excess / max(thresholds.maximum_torso_lean_degrees, 1.0)
        return self._outcome("Excessive Torso Lean", True, "torso_lean", torso_lean, thresholds.maximum_torso_lean_degrees, ratio, {
            "average_torso_lean": torso_lean,
            "maximum_torso_lean_degrees": thresholds.maximum_torso_lean_degrees,
        })

    def _elbow_drift_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        elbow_drift = self._mean_abs_sample_field(repetition, "elbow_drift")
        if elbow_drift is None or elbow_drift <= thresholds.maximum_elbow_drift:
            return None
        excess = elbow_drift - thresholds.maximum_elbow_drift
        ratio = excess / max(thresholds.maximum_elbow_drift, 1.0)
        return self._outcome("Elbow Drift", True, "elbow_drift", elbow_drift, thresholds.maximum_elbow_drift, ratio, {
            "average_elbow_drift": elbow_drift,
            "maximum_elbow_drift": thresholds.maximum_elbow_drift,
        })

    def _wrist_instability_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        wrist_instability = self._mean_abs_sample_field(repetition, "wrist_instability")
        if wrist_instability is None or wrist_instability <= thresholds.maximum_wrist_instability:
            return None
        excess = wrist_instability - thresholds.maximum_wrist_instability
        ratio = excess / max(thresholds.maximum_wrist_instability, 1.0)
        return self._outcome("Wrist Instability", True, "wrist_instability", wrist_instability, thresholds.maximum_wrist_instability, ratio, {
            "average_wrist_instability": wrist_instability,
            "maximum_wrist_instability": thresholds.maximum_wrist_instability,
        })

    def _fast_lowering_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        lowering_speed = movement_quality.average_curl_speed
        if lowering_speed is None or lowering_speed <= thresholds.acceptable_lowering_speed:
            return None
        excess = lowering_speed - thresholds.acceptable_lowering_speed
        ratio = excess / max(thresholds.acceptable_lowering_speed, 1.0)
        return self._outcome("Fast Lowering", True, "curl_speed", lowering_speed, thresholds.acceptable_lowering_speed, ratio, {
            "average_curl_speed": lowering_speed,
            "acceptable_lowering_speed": thresholds.acceptable_lowering_speed,
        })

    def _jerky_motion_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        smoothness = movement_quality.smoothness
        if smoothness is None or smoothness >= thresholds.minimum_smoothness:
            return None
        deficit = thresholds.minimum_smoothness - smoothness
        ratio = deficit / max(thresholds.minimum_smoothness, 1e-6)
        return self._outcome("Jerky Motion", True, "smoothness", smoothness, thresholds.minimum_smoothness, ratio, {
            "smoothness": smoothness,
            "minimum_smoothness": thresholds.minimum_smoothness,
        })

    def _tempo_consistency_rule(
        self,
        repetition: Mapping[str, Any],
        movement_quality: MovementQualityMetrics,
        thresholds: AssessmentThresholds,
    ) -> RuleOutcome | None:
        tempo_consistency = movement_quality.tempo_consistency
        if tempo_consistency is None or tempo_consistency >= thresholds.minimum_tempo_consistency:
            return None
        deficit = thresholds.minimum_tempo_consistency - tempo_consistency
        ratio = deficit / max(thresholds.minimum_tempo_consistency, 1e-6)
        return self._outcome("Inconsistent Tempo", True, "tempo_consistency", tempo_consistency, thresholds.minimum_tempo_consistency, ratio, {
            "tempo_consistency": tempo_consistency,
            "minimum_tempo_consistency": thresholds.minimum_tempo_consistency,
        })

    def _outcome(
        self,
        mistake: str,
        triggered: bool,
        metric_name: str,
        observed_value: float | None,
        threshold_value: float | None,
        ratio: float | None,
        evidence: dict[str, Any],
    ) -> RuleOutcome:
        """Build a standardized rule outcome."""

        return RuleOutcome(
            mistake=mistake,
            triggered=triggered,
            evidence=evidence,
            rule_name=mistake,
            metric_name=metric_name,
            observed_value=observed_value,
            threshold_value=threshold_value,
            ratio=ratio,
        )

    def _mean_abs_sample_field(self, repetition: Mapping[str, Any], field_name: str) -> float | None:
        """Average a sample field across the repetition's samples."""

        samples = repetition.get("samples") or []
        if not isinstance(samples, list):
            return None

        values = []
        for sample in samples:
            if not isinstance(sample, Mapping):
                continue
            numeric_value = self._float(sample.get(field_name))
            if numeric_value is not None:
                values.append(abs(numeric_value))
        if not values:
            return None
        return sum(values) / len(values)

    def _float(self, value: Any) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
