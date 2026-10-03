"""Severity evaluation for detected form mistakes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """Supported severity levels for assessment findings."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(slots=True)
class SeverityBand:
    """Numeric ranges mapped to severity labels."""

    low_max: float = 0.20
    medium_max: float = 0.50


class SeverityEvaluator:
    """Assign severity based on the distance from a configured threshold."""

    def __init__(self, bands: SeverityBand | None = None) -> None:
        self.bands = bands or SeverityBand()

    def from_ratio(self, ratio: float | None) -> Severity:
        """Map a normalized exceedance ratio to a severity level."""

        if ratio is None or ratio <= 0.0:
            return Severity.LOW
        if ratio <= self.bands.low_max:
            return Severity.LOW
        if ratio <= self.bands.medium_max:
            return Severity.MEDIUM
        return Severity.HIGH

    def from_excess(self, excess: float | None, threshold: float | None) -> Severity:
        """Evaluate severity using absolute excess over a threshold."""

        if excess is None or threshold is None or threshold <= 0.0:
            return Severity.LOW
        return self.from_ratio(max(0.0, excess / threshold))

    def from_deficit(self, deficit: float | None, threshold: float | None) -> Severity:
        """Evaluate severity using the deficit relative to a target threshold."""

        if deficit is None or threshold is None or threshold <= 0.0:
            return Severity.LOW
        return self.from_ratio(max(0.0, deficit / threshold))
