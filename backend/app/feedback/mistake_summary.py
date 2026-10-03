"""Mistake aggregation for completed workout sessions."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping

from app.feedback.feedback_models import MistakeOccurrence, MistakeSummary


class MistakeSummaryAnalyzer:
    """Aggregate repetition-level mistakes into a session summary."""

    def summarize(self, session_score: Mapping[str, Any] | Any) -> MistakeSummary:
        """Return frequency and timing data for all detected mistakes."""

        session_data = self._mapping(session_score)
        rep_scores = self._rep_scores(session_data)
        total_repetitions = len(rep_scores)

        mistake_counter: Counter[str] = Counter()
        mistake_reps: dict[str, set[int]] = defaultdict(set)
        first_seen: dict[str, int] = {}
        last_seen: dict[str, int] = {}

        for rep in rep_scores:
            rep_number = int(rep.get("rep_number") or 0)
            mistakes = self._mistakes(rep)
            for mistake in mistakes:
                mistake_counter[mistake] += 1
                mistake_reps[mistake].add(rep_number)
                first_seen.setdefault(mistake, rep_number)
                last_seen[mistake] = rep_number

        mistake_items = [
            MistakeOccurrence(
                mistake=mistake,
                occurrences=occurrences,
                percentage_affected=round((len(mistake_reps[mistake]) / total_repetitions) * 100.0, 2)
                if total_repetitions
                else 0.0,
                first_occurrence=first_seen.get(mistake),
                last_occurrence=last_seen.get(mistake),
            )
            for mistake, occurrences in sorted(
                mistake_counter.items(),
                key=lambda item: (-item[1], first_seen.get(item[0], 0), item[0]),
            )
        ]

        most_common = mistake_items[0] if mistake_items else None
        total_occurrences = sum(item.occurrences for item in mistake_items)

        return MistakeSummary(
            most_common_mistake=most_common,
            mistakes=mistake_items,
            total_unique_mistakes=len(mistake_items),
            total_mistake_occurrences=total_occurrences,
        )

    def _rep_scores(self, session_data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        """Return a normalized list of rep score payloads."""

        rep_scores = session_data.get("rep_scores") or []
        if not isinstance(rep_scores, list):
            return []

        normalized: list[Mapping[str, Any]] = []
        for rep in rep_scores:
            if hasattr(rep, "as_dict"):
                normalized.append(rep.as_dict())
            elif isinstance(rep, Mapping):
                normalized.append(rep)
        return normalized

    def _mistakes(self, rep_score: Mapping[str, Any]) -> list[str]:
        """Extract mistake names from a scored repetition."""

        assessment = self._mapping(rep_score.get("assessment"))
        entries = assessment.get("entries") or assessment.get("mistakes") or []
        if not isinstance(entries, list):
            return []

        mistakes: list[str] = []
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            mistake = str(entry.get("mistake") or "").strip()
            if mistake:
                mistakes.append(mistake)
        return mistakes

    def _mapping(self, value: Any) -> dict[str, Any]:
        """Normalize a mapping or dataclass-like object into a dictionary."""

        if value is None:
            return {}
        if hasattr(value, "as_dict"):
            return dict(value.as_dict())
        if isinstance(value, Mapping):
            return dict(value)
        return {}