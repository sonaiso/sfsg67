"""Minimal closure / economy layer.

MinClose(ℛ) = argmin Cost(ℛ)  subject to: all obligatory slots are filled

Cost(ℛ) = Σ_r ( α·d_r  +  β·i_r  +  γ·h_r )  +  λ·u

Where
    d_r  distance between the two nodes in the sequence
    i_r  implicitness penalty (0=explicit, 1=implicit)
    h_r  relation-type weight  (isnad < taqyid < tadmun < reference)
    u    number of unfilled obligatory slots

Default coefficients (integer-scaled to avoid floats)
    α=1, β=2, γ=1, λ=10

The minimal closure function takes a list of *candidate* RelationNodes
(all structurally possible relations) plus a set of obligatory slot indices,
and returns the cheapest set that satisfies all slots.

Implementation uses a greedy nearest-first selection; each slot is closed
by the cheapest available candidate that fills it.
"""
from __future__ import annotations

from .relation_nodes import DerivedNode, DerivedType, RelationNode, RelationType, make_derived_node

# ── Cost weights (integer, no floats) ────────────────────────────────
ALPHA  = 1   # distance
BETA   = 2   # implicitness
GAMMA  = 1   # relation-type weight
LAMBDA = 10  # per unfilled slot


_REL_WEIGHT: dict[RelationType, int] = {
    RelationType.ISNAD:     1,
    RelationType.TAQYID:    2,
    RelationType.TADMUN:    3,
    RelationType.REFERENCE: 4,
}


def _edge_cost(r: RelationNode, implicit: bool = False) -> int:
    distance   = abs(r.right_index - r.left_index)
    impl_flag  = 1 if implicit else 0
    rel_weight = _REL_WEIGHT.get(r.rel_type, 5)
    return ALPHA * distance + BETA * impl_flag + GAMMA * rel_weight


def minimal_closure(
    candidates: list[RelationNode],
    obligatory_left_indices: set[int] | None = None,
) -> tuple[list[RelationNode], int]:
    """Select the cheapest set of relations that closes all obligatory slots.

    Args
    ----
    candidates:              all structurally possible RelationNodes
    obligatory_left_indices: set of left-node indices that *must* be connected

    Returns
    -------
    (selected_relations, total_cost)
    """
    obligatory = set(obligatory_left_indices or set())
    # Sort candidates by edge cost (distance + weight) ascending
    ranked = sorted(candidates, key=lambda r: _edge_cost(r))

    selected: list[RelationNode] = []
    filled: set[int] = set()

    for rel in ranked:
        # If this candidate fills an obligatory slot not yet filled, take it
        if rel.left_index in obligatory and rel.left_index not in filled:
            selected.append(rel)
            filled.add(rel.left_index)

    # Unfilled slots
    unfilled = obligatory - filled
    total_cost = sum(_edge_cost(r) for r in selected) + LAMBDA * len(unfilled)
    return selected, total_cost


# ── Derive knowledge nodes from an accepted relation set ──────────────


def derive_nodes(relations: list[RelationNode]) -> list[DerivedNode]:
    """Generate DerivedNodes from ISNAD relations."""
    derived = []
    for rel in relations:
        if rel.rel_type is RelationType.ISNAD:
            # verb (left) → agent (right): fai'liyya
            derived.append(
                make_derived_node(
                    DerivedType.FAI_LIYYA,
                    primary_id=rel.left_id,
                    secondary_id=rel.right_id,
                    relation_id=rel.identity,
                )
            )
    return derived
