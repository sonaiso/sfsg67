"""Semantic resolution functions: ishtirak, idmar, takhsis.

These are NOT free interpretive jumps; each is conditional on structural
and semantic constraints established by the context and the constitutive
graph.

  resolve_ishtirak — select one signified from a polysemous word in context
  resolve_idmar    — reconstruct an implicit element to restore closure
  resolve_takhsis  — narrow a general semantic class via restrictions
"""

from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair, fractal_fold


@dataclass(frozen=True, slots=True)
class IstirakResult:
    """Resolution of a polysemous (mushtarak) word in context."""

    word_id: int
    context_id: int
    candidate_signifieds: tuple[int, ...]  # ordered by contextual rank
    selected_id: int
    resolution_id: int


@dataclass(frozen=True, slots=True)
class IdmarResult:
    """Reconstructed implicit (mudmar) element restoring compositional closure."""

    clause_id: int
    missing_element_type: int
    reconstructed_id: int
    restoration_mode: int
    resolution_id: int


@dataclass(frozen=True, slots=True)
class TakhsisResult:
    """Narrowed semantic class after applying restriction conditions."""

    general_class_id: int
    restriction_ids: tuple[int, ...]
    remaining_space_id: int
    resolution_id: int


def resolve_ishtirak(
    word_id: int,
    context_id: int,
    candidate_signifieds: list[int],
) -> IstirakResult:
    """Select the most context-fitting signified for a mushtarak word.

    Callers supply candidates already ordered by contextual priority;
    the first element is chosen as winner.
    """
    selected = candidate_signifieds[0] if candidate_signifieds else 0
    resolution_id = fractal_fold(
        [
            cantor_pair(1, word_id),
            cantor_pair(2, context_id),
            cantor_pair(3, selected),
            cantor_pair(4, len(candidate_signifieds)),
        ]
    )
    return IstirakResult(
        word_id=word_id,
        context_id=context_id,
        candidate_signifieds=tuple(candidate_signifieds),
        selected_id=selected,
        resolution_id=resolution_id,
    )


def resolve_idmar(
    clause_id: int,
    missing_element_type: int,
    reconstructed_id: int,
    restoration_mode: int = 0,
) -> IdmarResult:
    """Store the implicit element that restores compositional closure."""
    resolution_id = fractal_fold(
        [
            cantor_pair(1, clause_id),
            cantor_pair(2, missing_element_type),
            cantor_pair(3, reconstructed_id),
            cantor_pair(4, restoration_mode),
        ]
    )
    return IdmarResult(
        clause_id=clause_id,
        missing_element_type=missing_element_type,
        reconstructed_id=reconstructed_id,
        restoration_mode=restoration_mode,
        resolution_id=resolution_id,
    )


def resolve_takhsis(
    general_class_id: int,
    restriction_ids: list[int],
) -> TakhsisResult:
    """Narrow a general semantic class by a set of restriction conditions.

    remaining_space_id = π(general_class_id, fold(sorted restrictions))
    """
    sorted_restr = sorted(restriction_ids)
    restr_fold = fractal_fold(sorted_restr) if sorted_restr else 0
    remaining_space_id = cantor_pair(general_class_id, restr_fold)
    resolution_id = fractal_fold(
        [
            cantor_pair(1, general_class_id),
            cantor_pair(2, restr_fold),
            cantor_pair(3, len(sorted_restr)),
        ]
    )
    return TakhsisResult(
        general_class_id=general_class_id,
        restriction_ids=tuple(sorted_restr),
        remaining_space_id=remaining_space_id,
        resolution_id=resolution_id,
    )
