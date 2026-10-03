"""Session statistics derived from Phase 5 scoring outputs."""

from __future__ import annotations

from statistics import fmean
from typing import Any, Mapping

from app.feedback.feedback_models import RepetitionSnapshot, SessionStatistics


class SessionStatisticsAnalyzer:
    """Calculate aggregate session statistics from scored repetitions."""

    def calculate(self, session_score: Mapping[str, Any] | Any) -> SessionStatistics:
        """Return structured statistics for a scored workout session."""

        session_data = self._mapping(session_score)
        rep_scores = self._rep_scores(session_data)

        total_repetitions = len(rep_scores)
        rep_snapshots = [self._snapshot(rep) for rep in rep_scores]

        durations = [snapshot.duration_seconds for snapshot in rep_snapshots if snapshot.duration_seconds is not None]
        scores = [snapshot.score for snapshot in rep_snapshots if snapshot.score is not None]
        rom_values = [snapshot.rom for snapshot in rep_snapshots if snapshot.rom is not None]
        tempo_values = [snapshot.tempo for snapshot in rep_snapshots if snapshot.tempo is not None]
        stability_values = [snapshot.stability for snapshot in rep_snapshots if snapshot.stability is not None]

        consistency_score = self._float(
            session_data.get("consistency_score")
            or session_data.get("statistics", {}).get("consistency", {}).get("score")
        )

        return SessionStatistics(
            total_repetitions=total_repetitions,
            workout_duration_seconds=round(sum(durations), 2) if durations else None,
            average_repetition_duration_seconds=round(fmean(durations), 2) if durations else None,
            average_score=round(fmean(scores), 2) if scores else self._float(session_data.get("average_rep_score")),
            best_repetition=self._best_snapshot(rep_snapshots),
            worst_repetition=self._worst_snapshot(rep_snapshots),
            consistency_score=round(consistency_score, 2) if consistency_score is not None else (100.0 if not rep_snapshots else None),
            highest_rom=round(max(rom_values), 2) if rom_values else None,
            lowest_rom=round(min(rom_values), 2) if rom_values else None,
            average_rom=round(fmean(rom_values), 2) if rom_values else None,
            average_tempo=round(fmean(tempo_values), 2) if tempo_values else None,
            average_stability=round(fmean(stability_values), 2) if stability_values else None,
        )

    def _rep_scores(self, session_data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        """Return a normalized list of repetition score payloads."""

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

    def _snapshot(self, rep_score: Mapping[str, Any]) -> RepetitionSnapshot:
        """Convert a scored repetition into a compact snapshot."""

        repetition = self._mapping(rep_score.get("repetition"))
        scores = self._mapping(rep_score.get("scores"))
        assessment = self._mapping(rep_score.get("assessment"))
        entries = assessment.get("entries") or assessment.get("mistakes") or []
        mistake_names = self._mistake_names(entries)

        return RepetitionSnapshot(
            rep_number=int(rep_score.get("rep_number") or 0),
            score=self._float(rep_score.get("overall_score")),
            grade=str(rep_score.get("grade") or ""),
            duration_seconds=self._duration_seconds(repetition),
            rom=self._float(scores.get("rom")),
            tempo=self._float(scores.get("tempo")),
            stability=self._float(scores.get("stability")),
            mistake_count=len(mistake_names),
            mistakes=mistake_names,
        )

    def _duration_seconds(self, repetition: Mapping[str, Any]) -> float | None:
        """Derive repetition duration from explicit data or sample timestamps."""

        duration = self._float(repetition.get("duration_seconds"))
        if duration is not None:
            return duration

        samples = repetition.get("samples") or []
        if not isinstance(samples, list) or len(samples) < 2:
            return None

        timestamps: list[float] = []
        for sample in samples:
            if not isinstance(sample, Mapping):
                continue
            numeric_timestamp = self._float(sample.get("timestamp"))
            if numeric_timestamp is not None:
                timestamps.append(numeric_timestamp)

        if len(timestamps) < 2:
            return None

        return max(0.0, timestamps[-1] - timestamps[0])

    def _best_snapshot(self, snapshots: list[RepetitionSnapshot]) -> RepetitionSnapshot | None:
        """Return the highest-scoring repetition snapshot."""

        candidates = [snapshot for snapshot in snapshots if snapshot.score is not None]
        if not candidates:
            return None
        return max(candidates, key=lambda item: (item.score or 0.0, -item.rep_number))

    def _worst_snapshot(self, snapshots: list[RepetitionSnapshot]) -> RepetitionSnapshot | None:
        """Return the lowest-scoring repetition snapshot."""

        candidates = [snapshot for snapshot in snapshots if snapshot.score is not None]
        if not candidates:
            return None
        return min(candidates, key=lambda item: (item.score if item.score is not None else 0.0, item.rep_number))

    def _mistake_names(self, entries: Any) -> list[str]:
        """Extract mistake names from an assessment payload."""

        if not isinstance(entries, list):
            return []

        names: list[str] = []
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            name = str(entry.get("mistake") or "").strip()
            if name:
                names.append(name)
        return names

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