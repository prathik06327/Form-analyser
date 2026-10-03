"""Controller for the Phase 4 form assessment engine."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from app.assessment.assessment_result import AssessmentEntry, AssessmentResult
from app.assessment.mistake_detector import MistakeDetector
from app.assessment.movement_quality import MovementQualityAnalyzer
from app.assessment.rule_engine import RuleEngine
from app.assessment.severity import SeverityEvaluator
from app.assessment.thresholds import AssessmentThresholds, get_default_thresholds


class AssessmentEngine:
    """Assess completed repetitions using only Phase 3 repetition data."""

    def __init__(self, thresholds: AssessmentThresholds | None = None) -> None:
        self.thresholds = thresholds or get_default_thresholds()
        self.movement_quality_analyzer = MovementQualityAnalyzer()
        self.rule_engine = RuleEngine(self.thresholds)
        self.severity_evaluator = SeverityEvaluator()
        self.mistake_detector = MistakeDetector(self.severity_evaluator)
        self.history: list[AssessmentResult] = []

    def assess_rep(self, repetition: Mapping[str, Any]) -> AssessmentResult:
        """Return a structured assessment for one completed repetition."""

        rep_number = int(repetition.get("rep_number") or 0)
        movement_quality = self.movement_quality_analyzer.evaluate(repetition, self.thresholds)
        detected_mistakes = self.mistake_detector.detect(repetition, movement_quality, self.rule_engine)

        assessment_entries = [
            AssessmentEntry(
                mistake=mistake.mistake,
                severity=mistake.severity,
                evidence=mistake.evidence,
                rule_name=mistake.rule_name,
            )
            for mistake in detected_mistakes
        ]

        result = AssessmentResult(
            rep_number=rep_number,
            assessment=assessment_entries,
            movement_quality=movement_quality.as_dict(),
            repetition={
                "start_frame": repetition.get("start_frame"),
                "end_frame": repetition.get("end_frame"),
                "duration_seconds": repetition.get("duration_seconds"),
                "min_elbow_angle": repetition.get("min_elbow_angle"),
                "max_elbow_angle": repetition.get("max_elbow_angle"),
                "range_of_motion": repetition.get("range_of_motion"),
                "average_torso_angle": repetition.get("average_torso_angle"),
                "average_body_sway": repetition.get("average_body_sway"),
                "average_curl_speed": repetition.get("average_curl_speed"),
            },
            metadata={
                "thresholds": asdict(self.thresholds),
                "mistake_count": len(assessment_entries),
            },
        )

        self.history.append(result)
        return result

    def assess_rep_dict(self, repetition: Mapping[str, Any]) -> dict[str, Any]:
        """Return a serializable assessment payload for a completed repetition."""

        return self.assess_rep(repetition).as_dict()
