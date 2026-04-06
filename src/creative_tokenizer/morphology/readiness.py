"""Readiness envelope: is the word numerically closed enough for composition?

𝕁(w) = F(
    π(j_identity_closed,    x1),
    π(j_family_closed,      x2),
    π(j_constraint_closed,  x3),
    π(j_semantic_closed,    x4),
    π(j_factor_ready,       x5),
    π(j_composition_score,  q)
)

where q is an ExactDecimal.fractal_id() — never a raw float.
"""
from __future__ import annotations

from .exact_decimal import READY_FULL, READY_HIGH, ExactDecimal
from .fractal_storage import cantor_pair, fractal_fold

# ── Slot tags ─────────────────────────────────────────────────────────
_J_IDENTITY   = 1
_J_FAMILY     = 2
_J_CONSTRAINT = 3
_J_SEMANTIC   = 4
_J_FACTOR     = 5
_J_SCORE      = 6


def readiness_envelope(
    identity_closed: bool = True,
    family_closed: bool = True,
    constraint_closed: bool = True,
    semantic_closed: bool = True,
    factor_ready: bool = True,
    composition_score: tuple[int, int] = READY_FULL,
) -> int:
    """𝕁(w): composite readiness id.

    Each boolean is stored as 1/0.  composition_score is an (n, s) pair
    for ExactDecimal — default is READY_FULL (1.000).

    Typical patterns:
        independent noun / verb:       all True, score=READY_FULL
        relative pronoun (needs sila): factor_ready=False, score=READY_HIGH
        attached pronoun (needs ref):  factor_ready=False, score=READY_MID
    """
    score_id = ExactDecimal.from_pair(composition_score).fractal_id()
    return fractal_fold([
        cantor_pair(_J_IDENTITY,   int(identity_closed)),
        cantor_pair(_J_FAMILY,     int(family_closed)),
        cantor_pair(_J_CONSTRAINT, int(constraint_closed)),
        cantor_pair(_J_SEMANTIC,   int(semantic_closed)),
        cantor_pair(_J_FACTOR,     int(factor_ready)),
        cantor_pair(_J_SCORE,      score_id),
    ])


# ── Convenience constructors ──────────────────────────────────────────


def full_readiness() -> int:
    """Score 1.000 — fully closed, ready for composition."""
    return readiness_envelope()


def partial_readiness(score: tuple[int, int] = READY_HIGH, **flags: bool) -> int:
    """Partially ready word (e.g. needs referent, needs sila, etc.)."""
    return readiness_envelope(composition_score=score, **flags)
