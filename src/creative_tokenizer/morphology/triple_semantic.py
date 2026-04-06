"""Semantic envelope with three distinct layers:

    mutabaqa  — central / primary denotation
    tadammun  — component / entailed semantic parts
    iltizam   — conditional inferential implicature (obligation-mode = 0)

𝔻(w) = F( π(d_mutabaqa, m), π(d_tadammun, t), π(d_iltizam, l) )

The *iltizam* component encodes a conditional inference schema, NOT a direct
obligation.  It is represented as its own fractal sub-id derived from:
    F( π(t_condition, c), π(t_strength, λ), π(t_obligation_mode, 0) )

where obligation_mode is always 0 (conditional, non-obligatory).
"""
from __future__ import annotations

from .exact_decimal import ExactDecimal
from .fractal_storage import cantor_pair, fractal_fold

# ── Tag constants for the outer three-layer fold ──────────────────────
_D_MUTABAQA  = 1
_D_TADAMMUN  = 2
_D_ILTIZAM   = 3

# ── Tag constants inside iltizam sub-fold ─────────────────────────────
_T_CONDITION        = 1
_T_STRENGTH         = 2
_T_OBLIGATION_MODE  = 3  # always 0 = conditional/non-obligatory


def iltizam_id(
    condition_schema: int,
    inference_strength: ExactDecimal,
) -> int:
    """Encode an inferential implication as a fractal id.

    obligation_mode is always 0 — the implication is conditional, not direct.
    """
    return fractal_fold([
        cantor_pair(_T_CONDITION,       condition_schema),
        cantor_pair(_T_STRENGTH,        inference_strength.fractal_id()),
        cantor_pair(_T_OBLIGATION_MODE, 0),
    ])


def triple_semantic_envelope(
    mutabaqa: int,
    tadammun: int,
    iltizam: int,
) -> int:
    """𝔻(w) = F( π(1, mutabaqa), π(2, tadammun), π(3, iltizam) ).

    Each argument is a pre-computed fractal id for that semantic sub-layer.
    Pass 0 when a layer is absent / unspecified.
    """
    return fractal_fold([
        cantor_pair(_D_MUTABAQA, mutabaqa),
        cantor_pair(_D_TADAMMUN, tadammun),
        cantor_pair(_D_ILTIZAM,  iltizam),
    ])
