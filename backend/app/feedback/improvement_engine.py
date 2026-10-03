"""Identify strengths and weaknesses from session analytics."""

from __future__ import annotations

from typing import Any, Mapping

from app.feedback.feedback_models import ImprovementArea, ImprovementAreaSummary, MistakeSummary, SessionStatistics


class ImprovementEngine:
    """Translate metrics and mistakes into structured improvement areas."""

    def analyze(
        self,
        session_statistics: SessionStatistics | Mapping[str, Any],
        mistake_summary: MistakeSummary | Mapping[str, Any] | None = None,
    ) -> ImprovementAreaSummary:
        """Return the strongest positives and weakest areas in the workout."""

        stats = self._mapping(session_statistics)
        mistakes = self._mistake_list(mistake_summary)

        strengths = self._strengths(stats)
        weaknesses = self._weaknesses(stats, mistakes)

        return ImprovementAreaSummary(strengths=strengths, weaknesses=weaknesses)

    def _strengths(self, stats: Mapping[str, Any]) -> list[ImprovementArea]:
        """Build strength items from the highest quality metrics."""

        total_repetitions = int(stats.get("total_repetitions") or 0)
        if total_repetitions <= 0:
            return []

        candidates: list[ImprovementArea] = []
        metric_map = [
            ("average_rom", "Excellent Range of Motion", "rom"),
            ("average_tempo", "Excellent Tempo", "tempo"),
            ("average_stability", "Excellent Stability", "stability"),
            ("consistency_score", "Excellent Consistency", "consistency"),
        ]

        for key, title, metric in metric_map:
            score = self._float(stats.get(key))
            if score is None:
                continue
            if score >= 90.0:
                candidates.append(
                    ImprovementArea(
                        title=title,
                        kind="strength",
                        detail=f"Average {metric} remained strong at {round(score, 2)}.",
                        score=round(score, 2),
                        metric=metric,
                    )
                )

        if not candidates:
            fallback_metrics = [
                ("average_rom", "Range of Motion"),
                ("average_tempo", "Tempo"),
                ("average_stability", "Stability"),
            ]
            ranked = [
                (self._float(stats.get(key)), title, key)
                for key, title in fallback_metrics
                if self._float(stats.get(key)) is not None
            ]
            ranked.sort(key=lambda item: item[0] or 0.0, reverse=True)
            for score, title, metric in ranked[:3]:
                candidates.append(
                    ImprovementArea(
                        title=f"Solid {title}",
                        kind="strength",
                        detail=f"{title} was the best available metric in this session.",
                        score=round(score or 0.0, 2),
                        metric=metric,
                    )
                )

        return candidates

    def _weaknesses(self, stats: Mapping[str, Any], mistakes: list[Mapping[str, Any]]) -> list[ImprovementArea]:
        """Build weakness items from mistakes and lower-scoring metrics."""

        weaknesses: list[ImprovementArea] = []
        for mistake in mistakes[:3]:
            percentage = self._float(mistake.get("percentage_affected"))
            occurrences = int(mistake.get("occurrences") or 0)
            title = str(mistake.get("mistake") or "")
            weaknesses.append(
                ImprovementArea(
                    title=title,
                    kind="weakness",
                    detail=f"Detected in {occurrences} repetition(s) and affected {percentage or 0.0:.0f}% of the session.",
                    occurrences=occurrences,
                    related_mistake=title,
                )
            )

        metric_weaknesses = [
            ("average_rom", "Partial Curl", "rom"),
            ("average_tempo", "Fast Lowering", "tempo"),
            ("average_stability", "Body Swing", "stability"),
        ]
        for key, title, metric in metric_weaknesses:
            score = self._float(stats.get(key))
            if score is None or score >= 75.0:
                continue
            weaknesses.append(
                ImprovementArea(
                    title=title,
                    kind="weakness",
                    detail=f"Average {metric} was limited at {round(score, 2)}.",
                    score=round(score, 2),
                    metric=metric,
                    related_mistake=title,
                )
            )

        return self._dedupe(weaknesses)

    def _mistake_list(self, mistake_summary: MistakeSummary | Mapping[str, Any] | None) -> list[Mapping[str, Any]]:
        """Return the summary's mistake list in plain mapping form."""

        if mistake_summary is None:
            return []

        payload = self._mapping(mistake_summary)
        mistakes = payload.get("mistakes") or []
        if not isinstance(mistakes, list):
            return []
        normalized: list[Mapping[str, Any]] = []
        for mistake in mistakes:
            if hasattr(mistake, "as_dict"):
                normalized.append(mistake.as_dict())
            elif isinstance(mistake, Mapping):
                normalized.append(mistake)
        return normalized

    def _dedupe(self, areas: list[ImprovementArea]) -> list[ImprovementArea]:
        """Remove duplicate improvement items while preserving order."""

        seen: set[tuple[str, str]] = set()
        unique: list[ImprovementArea] = []
        for area in areas:
            key = (area.kind, area.title)
            if key in seen:
                continue
            seen.add(key)
            unique.append(area)
        return unique

    def _mapping(self, value: Any) -> dict[str, Any]:
        """Normalize a mapping or dataclass-like object into a dictionary."""

        if value is None:
            return {}
        if hasattr(value, "as_dict"):
            return dict(value.as_dict())
        if isinstance(value, Mapping):
            return dict(value)
        return {}

    def _float(self, value: Any) -> float | None:
        """Safely convert a value to float."""

        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None