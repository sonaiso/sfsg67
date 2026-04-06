"""Typed edges for the fractal knowledge graph.

Every edge carries a semantic EdgeType so the graph is richly typed rather
than a uniform adjacency structure.

Two classes of edges:
  constitutive  — form the foundational DAG (no cycles)
  overlay       — anaphoric / cross-sentence references (may back-point)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class EdgeType(IntEnum):
    # --- identity ---
    HAS_RAW_FORM = 1
    HAS_SKELETON = 2
    HAS_PATTERN = 3
    HAS_ROOT = 4
    # --- meaning ---
    DENOTES_BY_MUTABAQA = 10
    EMBEDS_TADAMMUN = 11
    CONDITIONALLY_ENTAILS = 12
    # --- ontology ---
    INSTANCE_OF = 20
    BELONGS_TO_DOMAIN = 21
    HAS_EPISTEMIC_MODE = 22
    HAS_EXISTENTIAL_MODE = 23
    # --- morphology ---
    INFLECTS_AS = 30
    CONSTRAINED_BY = 31
    MARKED_BY = 32
    # --- compositional (constitutive) ---
    PREDICATES = 40
    QUALIFIES = 41
    EMBEDS = 42
    REFERS_TO = 43
    CAUSES = 44
    RESULTS_IN = 45
    RESTRICTS = 46
    # --- style ---
    REALIZES_STYLE = 50
    BELONGS_TO_STYLE_HUB = 51
    # --- pre-judgment semantics ---
    HAS_MANTUQ = 60
    HAS_MAFHUM = 61
    HAS_IQTIDA = 62
    HAS_ISHARA = 63
    HAS_SHART = 64
    HAS_GHAYA = 65
    HAS_MUWAFAQA = 66
    HAS_MUKHALAFA = 67
    # --- transfer ---
    TRANSFERRED_TO_URFI = 70
    TRANSFERRED_TO_ISTILAHI = 71
    TRANSFERRED_TO_DOMAIN = 72
    # --- metaphor (overlay) ---
    METAPHORICALLY_EXTENDS = 80
    # --- anaphora / cross-sentence (overlay) ---
    ANAPHORICALLY_LINKS = 90
    SENTENCE_LINKS_TO = 91


@dataclass(frozen=True, slots=True)
class TypedEdge:
    source_id: int
    target_id: int
    edge_type: EdgeType
    edge_id: int


def make_edge(
    source_id: int,
    target_id: int,
    edge_type: EdgeType,
) -> TypedEdge:
    edge_id = fractal_fold(
        [
            cantor_pair(1, source_id),
            cantor_pair(2, target_id),
            cantor_pair(3, int(edge_type)),
        ]
    )
    return TypedEdge(
        source_id=source_id,
        target_id=target_id,
        edge_type=edge_type,
        edge_id=edge_id,
    )
