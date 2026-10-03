"""Reusable data structures for stored repetition measurements."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable


@dataclass(slots=True)
class RepetitionSample:
    """One frame worth of repetition measurements."""

    frame_number: int
    timestamp: float
    elbow_angle: float | None
    torso_angle: float | None
    body_sway: float | None
    movement_direction: str
    current_rom: float | None
    curl_speed: float | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a serializable sample payload."""

        return asdict(self)


@dataclass(slots=True)
class RepetitionRecord:
    """Aggregated measurements for one completed repetition."""

    rep_number: int
    start_frame: int
    end_frame: int
    duration_seconds: float
    min_elbow_angle: float | None
    max_elbow_angle: float | None
    range_of_motion: float | None
    average_torso_angle: float | None
    average_body_sway: float | None
    average_curl_speed: float | None
    samples: list[RepetitionSample] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        """Return a serializable representation of the record."""

        return {
            "rep_number": self.rep_number,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "duration_seconds": self.duration_seconds,
            "min_elbow_angle": self.min_elbow_angle,
            "max_elbow_angle": self.max_elbow_angle,
            "range_of_motion": self.range_of_motion,
            "average_torso_angle": self.average_torso_angle,
            "average_body_sway": self.average_body_sway,
            "average_curl_speed": self.average_curl_speed,
            "samples": [sample.to_dict() for sample in self.samples],
        }


class RepetitionDataStore:
    """Store completed repetitions for downstream phases."""

    def __init__(self) -> None:
        self.records: list[RepetitionRecord] = []

    def add_record(self, record: RepetitionRecord) -> None:
        """Append a completed repetition to the store."""

        self.records.append(record)

    def extend(self, records: Iterable[RepetitionRecord]) -> None:
        """Append several completed repetitions."""

        self.records.extend(records)

    def reset(self) -> None:
        """Clear all stored records."""

        self.records.clear()

    def latest(self) -> RepetitionRecord | None:
        """Return the most recent record, if available."""

        if not self.records:
            return None
        return self.records[-1]

    def as_list(self) -> list[dict[str, object]]:
        """Return all stored records in dictionary form."""

        return [record.as_dict() for record in self.records]
