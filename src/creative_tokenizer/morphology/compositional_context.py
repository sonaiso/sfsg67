"""Compositional context window for a single word node.

𝕏_i = F(N_{i-r}, …, N_i, …, N_{i+r})

The window is stored as a sorted fractal fold over present neighbour ids so
that absent edges (start/end of sequence) contribute 0 and do not corrupt
the identity.
"""
from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair, fractal_fold


@dataclass(frozen=True, slots=True)
class CompositionalContext:
    """Context window around a single pre-compositional node.

    Attributes
    ----------
    node_id:    ℙ(w_i) — the focal word's pre-compositional value
    left_id:    ℙ(w_{i-1}) or 0 if absent
    right_id:   ℙ(w_{i+1}) or 0 if absent
    context_id: 𝕏_i — the combined context fractal id
    """

    node_id:    int
    left_id:    int
    right_id:   int
    context_id: int


def make_context(
    node_id: int,
    left_id: int = 0,
    right_id: int = 0,
) -> CompositionalContext:
    """Build 𝕏_i = F( π(0, left), π(1, node), π(2, right) ).

    Tags 0/1/2 encode *position* so that
    F(left=A, node=B, right=C) ≠ F(left=B, node=A, right=C).
    """
    context_id = fractal_fold([
        cantor_pair(0, left_id),
        cantor_pair(1, node_id),
        cantor_pair(2, right_id),
    ])
    return CompositionalContext(
        node_id=node_id,
        left_id=left_id,
        right_id=right_id,
        context_id=context_id,
    )
