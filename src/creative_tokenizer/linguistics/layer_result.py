"""Layer result — unified payload for every step in the linguistic pipeline.

Each layer in the analysis chain produces a ``LayerResult`` that records:
* which formal layer it belongs to,
* the concrete value it computed,
* its fractal identity,
* the layer and identity it was derived from (trace),
* a confidence score (1.0 = deterministic, <1.0 = heuristic / lookup).

This makes the full chain inspectable and auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..morphology.formal_chain import LayerIndex

__all__ = ["LayerResult"]


@dataclass(frozen=True, slots=True)
class LayerResult:
    """A single step in the linguistic analysis trace."""

    layer: LayerIndex
    value: Any
    identity: int
    source_layer: LayerIndex
    source_identity: int
    confidence: float  # 0.0–1.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"confidence must be in [0.0, 1.0], got {self.confidence}"
            )
