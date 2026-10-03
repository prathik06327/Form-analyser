"""Structured outputs for form assessment results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from app.assessment.severity import Severity


@dataclass(slots=True)
class AssessmentEntry:
    """One detected mistake with severity and evidence."""

    mistake: str
    severity: Severity
    evidence: dict[str, Any] = field(default_factory=dict)
    rule_name: str = ""

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable assessment entry."""

        return {
            "mistake": self.mistake,
            "severity": self.severity.value,
            "evidence": self.evidence,
            "rule_name": self.rule_name,
        }


@dataclass(slots=True)
class AssessmentResult:
    """Structured output for a completed repetition assessment."""

    rep_number: int
    assessment: list[AssessmentEntry] = field(default_factory=list)
    movement_quality: dict[str, Any] = field(default_factory=dict)
    repetition: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable assessment result."""

        return {
            "rep_number": self.rep_number,
            "assessment": [entry.as_dict() for entry in self.assessment],
            "movement_quality": self.movement_quality,
            "repetition": self.repetition,
            "metadata": self.metadata,
        }
