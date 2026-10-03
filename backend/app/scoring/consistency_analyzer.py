"""Analyze workout consistency across completed repetitions."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import fmean
from typing import Any, Iterable, Mapping


@dataclass(slots=True)
class ConsistencyResult:
    """Summary of inter-repetition consistency."""

    score: float
    rom_variation: float | None
    tempo_variation: float | None
    stability_variation: float | None
    form_variation: float | None

    def as_dict(self) -> dict[str, float | None]:
        """Return a serializable consistency payload."""

        return {
            "score": self.score,
            "rom_variation": self.rom_variation,
            "tempo_variation": self.tempo_variation,
            "stability_variation": self.stability_variation,
            "form_variation": self.form_variation,
        }


class ConsistencyAnalyzer:
    """Measure variation in movement quality across all scored repetitions."""

    def analyze(self, rep_scores: Iterable[Mapping[str, Any]]) -> ConsistencyResult:
        """Return a consistency score and supporting variation metrics."""

        rep_scores = list(rep_scores)
        if not rep_scores:
            return ConsistencyResult(100.0, None, None, None, None)

        rom_variation = self._variation(self._metric_series(rep_scores, "rom"))
        tempo_variation = self._variation(self._metric_series(rep_scores, "tempo"))
        stability_variation = self._variation(self._metric_series(rep_scores, "stability"))
        form_variation = self._variation(self._form_series(rep_scores))

        normalized_values = [
            self._normalized_variation(rom_variation),
            self._normalized_variation(tempo_variation),
            self._normalized_variation(stability_variation),
            self._normalized_variation(form_variation),
        ]
        available = [value for value in normalized_values if value is not None]
        if not available:
            return ConsistencyResult(100.0, rom_variation, tempo_variation, stability_variation, form_variation)

        average_variation = fmean(available)
        score = max(0.0, min(100.0, 100.0 - (average_variation * 100.0)))
        return ConsistencyResult(score, rom_variation, tempo_variation, stability_variation, form_variation)

    def _metric_series(self, rep_scores: list[Mapping[str, Any]], metric: str) -> list[float]:
        """Extract a metric series from scored repetitions."""

        series: list[float] = []
        for rep in rep_scores:
            scores = rep.get("scores") or {}
            if not isinstance(scores, Mapping):
                continue
            value = scores.get(metric)
            numeric_value = self._float(value)
            if numeric_value is not None:
                series.append(numeric_value)
        return series

    def _form_series(self, rep_scores: list[Mapping[str, Any]]) -> list[float]:
        """Build a form-quality series from penalties and mistake counts."""

        series: list[float] = []
        for rep in rep_scores:
            penalties = rep.get("penalties") or []
            mistakes = rep.get("assessment") or []
            penalty_total = 0.0
            if isinstance(penalties, list):
                for item in penalties:
                    if isinstance(item, Mapping):
                        penalty_total += abs(self._float(item.get("amount")) or 0.0)
            mistake_count = len(mistakes) if isinstance(mistakes, list) else 0
            series.append(penalty_total + float(mistake_count))
        return series

    def _variation(self, series: list[float]) -> float | None:
        """Return the coefficient of variation for a numeric series."""

        if len(series) < 2:
            return 0.0 if series else None

        mean_value = fmean(series)
        if mean_value <= 0.0:
            return 0.0

        variance = fmean((value - mean_value) ** 2 for value in series)
        return sqrt(variance) / mean_value

    def _normalized_variation(self, variation: float | None) -> float | None:
        """Clamp variation to the 0..1 range for score conversion."""

        if variation is None:
            return None
        return max(0.0, min(1.0, variation))

    def _float(self, value: Any) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None