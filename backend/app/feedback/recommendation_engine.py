"""Deterministic coaching recommendations for workout feedback."""

from __future__ import annotations

from typing import Any, Mapping

from app.feedback.feedback_models import ImprovementAreaSummary, RecommendationItem


class RecommendationEngine:
    """Convert weaknesses into rule-based coaching advice."""

    def generate(self, improvement_areas: ImprovementAreaSummary | Mapping[str, Any], mistake_summary: Mapping[str, Any] | Any | None = None) -> list[RecommendationItem]:
        """Return a deduplicated list of recommendations."""

        areas = self._mapping(improvement_areas)
        weaknesses = self._areas(areas.get("weaknesses") or [])
        mistakes = self._mistakes(mistake_summary)

        recommendations: list[RecommendationItem] = []
        for weakness in weaknesses:
            recommendation = self._recommendation_for_area(weakness)
            if recommendation is not None:
                recommendations.append(recommendation)

        for mistake in mistakes:
            recommendation = self._recommendation_for_mistake(mistake)
            if recommendation is not None:
                recommendations.append(recommendation)

        if not recommendations:
            recommendations.append(
                RecommendationItem(
                    message="Continue maintaining your current technique and tempo.",
                    trigger="general",
                    priority=0,
                )
            )

        return self._dedupe(recommendations)

    def _recommendation_for_area(self, area: Mapping[str, Any]) -> RecommendationItem | None:
        """Build a recommendation from a weakness area."""

        title = str(area.get("title") or "").strip()
        if not title:
            return None
        return self._recommendation_for_mistake(title)

    def _recommendation_for_mistake(self, mistake: str) -> RecommendationItem | None:
        """Return the deterministic coaching cue for one mistake."""

        rules = {
            "Partial Curl": "Aim for full elbow extension at the bottom and full flexion at the top.",
            "Incomplete Extension": "Straighten the elbow fully at the bottom of each curl.",
            "Excessive Body Swing": "Reduce torso movement by lowering the weight and keeping your torso stable.",
            "Body Swing": "Reduce torso movement by lowering the weight and keeping your torso stable.",
            "Excessive Torso Lean": "Keep your torso upright and brace your core before each rep.",
            "Elbow Drift": "Keep your elbows close to your sides through the curl.",
            "Wrist Instability": "Keep your wrists neutral and avoid letting them bend back.",
            "Fast Lowering": "Lower the dumbbell under control during the eccentric phase.",
            "Jerky Motion": "Use a smoother, more even tempo through the entire repetition.",
            "Inconsistent Tempo": "Keep the lifting and lowering tempo consistent from rep to rep.",
        }

        message = rules.get(mistake)
        if message is None:
            return None
        return RecommendationItem(message=message, trigger=mistake, priority=self._priority(mistake))

    def _areas(self, areas: list[Any]) -> list[Mapping[str, Any]]:
        """Normalize a list of area objects or mappings."""

        normalized: list[Mapping[str, Any]] = []
        for area in areas:
            if hasattr(area, "as_dict"):
                normalized.append(area.as_dict())
            elif isinstance(area, Mapping):
                normalized.append(area)
        return normalized

    def _mistakes(self, mistake_summary: Mapping[str, Any] | Any | None) -> list[str]:
        """Extract the most relevant mistakes from the summary."""

        if mistake_summary is None:
            return []

        payload = self._mapping(mistake_summary)
        mistakes = payload.get("mistakes") or []
        if not isinstance(mistakes, list):
            return []

        names: list[str] = []
        for mistake in mistakes:
            if not isinstance(mistake, Mapping):
                continue
            name = str(mistake.get("mistake") or "").strip()
            if name:
                names.append(name)
        return names

    def _priority(self, mistake: str) -> int:
        """Assign a deterministic priority to a recommendation."""

        priority_map = {
            "Partial Curl": 10,
            "Incomplete Extension": 9,
            "Excessive Body Swing": 8,
            "Body Swing": 8,
            "Excessive Torso Lean": 7,
            "Elbow Drift": 6,
            "Wrist Instability": 5,
            "Fast Lowering": 9,
            "Jerky Motion": 6,
            "Inconsistent Tempo": 6,
        }
        return priority_map.get(mistake, 1)

    def _dedupe(self, recommendations: list[RecommendationItem]) -> list[RecommendationItem]:
        """Remove duplicate recommendation messages while preserving order."""

        seen: set[str] = set()
        unique: list[RecommendationItem] = []
        for recommendation in sorted(recommendations, key=lambda item: (-item.priority, item.trigger, item.message)):
            if recommendation.message in seen:
                continue
            seen.add(recommendation.message)
            unique.append(recommendation)
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