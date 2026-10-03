"""Evaluate overall movement quality from completed repetition data."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Any, Iterable, Mapping

from app.assessment.thresholds import AssessmentThresholds


@dataclass(slots=True)
class MovementQualityMetrics:
    """Normalized movement quality metrics for one repetition."""

    rom: float | None
    normalized_rom: float | None
    stability: float | None
    tempo_consistency: float | None
    smoothness: float | None
    symmetry: float | None
    average_torso_lean: float | None
    average_body_sway: float | None
    average_curl_speed: float | None

    def as_dict(self) -> dict[str, float | None]:
        """Return a serializable movement-quality payload."""

        return {
            "rom": self.rom,
            "normalized_rom": self.normalized_rom,
            "stability": self.stability,
            "tempo_consistency": self.tempo_consistency,
            "smoothness": self.smoothness,
            "symmetry": self.symmetry,
            "average_torso_lean": self.average_torso_lean,
            "average_body_sway": self.average_body_sway,
            "average_curl_speed": self.average_curl_speed,
        }


class MovementQualityAnalyzer:
    """Calculate normalized movement metrics without classifying mistakes."""

    def evaluate(
        self,
        repetition: Mapping[str, Any],
        thresholds: AssessmentThresholds,
    ) -> MovementQualityMetrics:
        """Return movement quality measurements for a completed repetition."""

        samples = self._samples(repetition)
        rom = self._float(repetition.get("range_of_motion"))
        normalized_rom = self._ratio(rom, thresholds.minimum_rom)
        average_torso_lean = self._mean_abs(samples, "torso_angle")
        average_body_sway = self._mean_abs(samples, "body_sway")
        average_curl_speed = self._mean_abs(samples, "curl_speed")

        stability = self._invert_ratio(average_body_sway, thresholds.maximum_body_sway)
        tempo_consistency = self._tempo_consistency(samples, thresholds)
        smoothness = self._invert_ratio(self._jerkiness(samples), thresholds.maximum_jerkiness)
        symmetry = self._symmetry(repetition, samples)

        return MovementQualityMetrics(
            rom=rom,
            normalized_rom=normalized_rom,
            stability=stability,
            tempo_consistency=tempo_consistency,
            smoothness=smoothness,
            symmetry=symmetry,
            average_torso_lean=average_torso_lean,
            average_body_sway=average_body_sway,
            average_curl_speed=average_curl_speed,
        )

    def _samples(self, repetition: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        """Return the sample list from a repetition payload."""

        raw_samples = repetition.get("samples") or []
        if not isinstance(raw_samples, list):
            return []
        return [sample for sample in raw_samples if isinstance(sample, Mapping)]

    def _float(self, value: Any) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _ratio(self, value: float | None, threshold: float | None) -> float | None:
        """Normalize a value against a threshold and clamp to 0..1."""

        if value is None or threshold is None or threshold <= 0.0:
            return None
        return max(0.0, min(1.0, value / threshold))

    def _invert_ratio(self, value: float | None, threshold: float | None) -> float | None:
        """Return a normalized score where lower values are better."""

        ratio = self._ratio(value, threshold)
        if ratio is None:
            return None
        return max(0.0, min(1.0, 1.0 - ratio))

    def _mean_abs(self, samples: Iterable[Mapping[str, Any]], key: str) -> float | None:
        """Return the average absolute value for a sample field."""

        values = []
        for sample in samples:
            numeric_value = self._float(sample.get(key))
            if numeric_value is not None:
                values.append(abs(numeric_value))
        if not values:
            return None
        return fmean(values)

    def _tempo_consistency(
        self,
        samples: list[Mapping[str, Any]],
        thresholds: AssessmentThresholds,
    ) -> float | None:
        """Estimate how consistently the curl speed stays near the expected range."""

        speeds = []
        for sample in samples:
            speed = self._float(sample.get("curl_speed"))
            if speed is not None:
                speeds.append(abs(speed))
        if not speeds:
            return None

        average_speed = fmean(speeds)
        target_speed = thresholds.acceptable_curl_speed
        delta = abs(average_speed - target_speed)
        return max(0.0, min(1.0, 1.0 - (delta / max(target_speed, 1.0))))

    def _jerkiness(self, samples: list[Mapping[str, Any]]) -> float | None:
        """Measure speed variation as a simple smoothness proxy."""

        speeds = []
        for sample in samples:
            speed = self._float(sample.get("curl_speed"))
            if speed is not None:
                speeds.append(abs(speed))
        if len(speeds) < 2:
            return None

        average_speed = fmean(speeds)
        if average_speed <= 0.0:
            return None

        average_delta = fmean(abs(speed - average_speed) for speed in speeds)
        return max(0.0, average_delta / average_speed)

    def _symmetry(
        self,
        repetition: Mapping[str, Any],
        samples: list[Mapping[str, Any]],
    ) -> float | None:
        """Estimate symmetry when bilateral data is available, otherwise return a neutral value."""

        if repetition.get("left_elbow_angle") is not None and repetition.get("right_elbow_angle") is not None:
            left_angle = self._float(repetition.get("left_elbow_angle"))
            right_angle = self._float(repetition.get("right_elbow_angle"))
            if left_angle is None or right_angle is None:
                return None
            max_angle = max(left_angle, right_angle, 1.0)
            return max(0.0, min(1.0, 1.0 - (abs(left_angle - right_angle) / max_angle)))

        if not samples:
            return None

        return 1.0
