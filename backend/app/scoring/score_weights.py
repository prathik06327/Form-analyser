"""Centralized scoring weights for the Phase 5 scoring engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ScoreWeights:
    """Configurable weights used by the scoring calculator.

    The weights must sum to 1.0 so the final weighted score remains normalized.
    """

    rom: float = 0.25
    stability: float = 0.20
    tempo: float = 0.15
    elbow_control: float = 0.20
    body_control: float = 0.20

    def __post_init__(self) -> None:
        total = self.total
        if abs(total - 1.0) > 1e-6:
            raise ValueError("scoring weights must total 1.0")

    @property
    def total(self) -> float:
        """Return the total weight."""

        return self.rom + self.stability + self.tempo + self.elbow_control + self.body_control

    def as_dict(self) -> dict[str, float]:
        """Return the weights as a serializable dictionary."""

        return {
            "rom": self.rom,
            "stability": self.stability,
            "tempo": self.tempo,
            "elbow_control": self.elbow_control,
            "body_control": self.body_control,
        }


def get_default_weights() -> ScoreWeights:
    """Return the default scoring weights."""

    return ScoreWeights()