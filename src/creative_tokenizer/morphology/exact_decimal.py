"""Exact decimal encoding for fractional values within the fractal system.

Instead of IEEE-754 floats (which introduce rounding errors), every fractional
value is represented as a pair (numerator: int, scale: int) meaning

    value = numerator / 10**scale

This pair is then fed into the Cantor pairing function so it participates in
the same fractal arithmetic as every other identity component.

Examples
--------
>>> d = ExactDecimal(875, 3)   # 0.875
>>> d.as_float()
0.875
>>> d.fractal_id()  # π(875, 3)
387511
"""
from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair

# -----------------------------------------------------------------------
# Pre-defined readiness constants used by ReadinessEnvelope
# -----------------------------------------------------------------------
READY_FULL: tuple[int, int] = (1000, 3)   # 1.000
READY_HIGH: tuple[int, int] = (875, 3)    # 0.875
READY_MID:  tuple[int, int] = (500, 3)    # 0.500
READY_LOW:  tuple[int, int] = (250, 3)    # 0.250
READY_ZERO: tuple[int, int] = (0, 3)      # 0.000


@dataclass(frozen=True, slots=True)
class ExactDecimal:
    """An exact decimal rational  numerator / 10**scale."""

    numerator: int   # non-negative integer
    scale: int       # number of decimal places (>= 0)

    def __post_init__(self) -> None:
        if self.numerator < 0:
            raise ValueError("numerator must be non-negative")
        if self.scale < 0:
            raise ValueError("scale must be non-negative")

    # ------------------------------------------------------------------
    def fractal_id(self) -> int:
        """Return π(numerator, scale) — stable, hashable, fractal-ready."""
        return cantor_pair(self.numerator, self.scale)

    def as_float(self) -> float:
        """Human-readable float — for display/debugging only, not arithmetic."""
        result: float = self.numerator / (10 ** self.scale)
        return result

    # ------------------------------------------------------------------
    @staticmethod
    def from_pair(pair: tuple[int, int]) -> ExactDecimal:
        return ExactDecimal(pair[0], pair[1])

    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"ExactDecimal({self.numerator}, {self.scale})"
