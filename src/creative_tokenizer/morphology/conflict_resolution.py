"""Semantic conflict resolution: rank interpretation paths before judgment.

Score(p) = lit_priority_base × 10
         + context_fit + economy + closure + domain_coherence + semantic_strength

Priority order (canonical semantic principle):
  1. LITERAL      — original wadi' sense (highest priority)
  2. TRANSFERRED  — urfi or istilahi transferred sense
  3. TAKHSIS      — narrowing by restriction
  4. IDMAR        — implicit element restoration
  5. MAJAZI       — metaphorical reading
  6. MUSHTARAK    — polysemous reading resolved by context
  7. PROBABLE     — weak inferential candidate

This layer is pre-judgment: it ranks paths but does not assign truth values.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class InterpretationPath(IntEnum):
    LITERAL = 1
    TRANSFERRED = 2
    TAKHSIS = 3
    IDMAR = 4
    MAJAZI = 5
    MUSHTARAK = 6
    PROBABLE = 7


_PATH_PRIORITY: dict[InterpretationPath, int] = {
    InterpretationPath.LITERAL: 7,
    InterpretationPath.TRANSFERRED: 6,
    InterpretationPath.TAKHSIS: 5,
    InterpretationPath.IDMAR: 4,
    InterpretationPath.MAJAZI: 3,
    InterpretationPath.MUSHTARAK: 2,
    InterpretationPath.PROBABLE: 1,
}


@dataclass(frozen=True, slots=True)
class SemanticPath:
    path_type: InterpretationPath
    signified_id: int
    literal_priority: int
    context_fit: int
    economy: int
    closure: int
    domain_coherence: int
    semantic_strength: int
    total_score: int
    path_id: int


@dataclass(frozen=True, slots=True)
class ConflictResolution:
    paths: tuple[SemanticPath, ...]  # ranked descending by total_score
    winner: SemanticPath
    resolution_id: int


def score_path(
    path_type: InterpretationPath,
    signified_id: int,
    context_fit: int = 5,
    economy: int = 5,
    closure: int = 5,
    domain_coherence: int = 5,
    semantic_strength: int = 5,
) -> SemanticPath:
    """Score an interpretation path.  All dimensional scores are 0–10."""
    lit_prio = _PATH_PRIORITY[path_type]
    total = (
        lit_prio * 10
        + context_fit
        + economy
        + closure
        + domain_coherence
        + semantic_strength
    )
    path_id = fractal_fold(
        [
            cantor_pair(1, int(path_type)),
            cantor_pair(2, signified_id),
            cantor_pair(3, total),
        ]
    )
    return SemanticPath(
        path_type=path_type,
        signified_id=signified_id,
        literal_priority=lit_prio,
        context_fit=context_fit,
        economy=economy,
        closure=closure,
        domain_coherence=domain_coherence,
        semantic_strength=semantic_strength,
        total_score=total,
        path_id=path_id,
    )


def resolve_conflict(paths: list[SemanticPath]) -> ConflictResolution:
    """Select the highest-scoring path as winner (pre-judgment ranking)."""
    if not paths:
        raise ValueError("resolve_conflict requires at least one path")
    ranked = sorted(paths, key=lambda p: p.total_score, reverse=True)
    winner = ranked[0]
    resolution_id = fractal_fold(
        [
            cantor_pair(1, winner.path_id),
            cantor_pair(2, len(paths)),
            cantor_pair(3, winner.total_score),
        ]
    )
    return ConflictResolution(
        paths=tuple(ranked),
        winner=winner,
        resolution_id=resolution_id,
    )
