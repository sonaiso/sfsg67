"""Relation nodes and derived knowledge nodes produced by composition.

Relation types
--------------
    ISNAD      — predicative / attributive relation (verb↔subject, S↔P …)
    TAQYID     — restrictive / modifying relation (adjective, idafa, adverb …)
    TADMUN     — embedding / containment (semantic incorporation)
    REFERENCE  — anaphoric reference (explicit / implicit / relative / s2s)

Derived knowledge types
-----------------------
    FAI_LIYYA     — agent-hood
    MAF_ULIYYA    — patient-hood
    SABABIYYA     — causality
    MUSABBABIYYA  — result / effect
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .exact_decimal import READY_FULL, ExactDecimal
from .fractal_storage import cantor_pair, fractal_fold

# ── Relation type tag ─────────────────────────────────────────────────


class RelationType(IntEnum):
    ISNAD      = 1
    TAQYID     = 2
    TADMUN     = 3
    REFERENCE  = 4


# ── Derived knowledge type tag ────────────────────────────────────────


class DerivedType(IntEnum):
    FAI_LIYYA     = 1
    MAF_ULIYYA    = 2
    SABABIYYA     = 3
    MUSABBABIYYA  = 4


# ── Reference sub-type ────────────────────────────────────────────────


class ReferenceMode(IntEnum):
    EXPLICIT    = 1   # ضمير ظاهر / اسم إشارة ظاهر
    IMPLICIT    = 2   # مستتر / مشار إليه مقدر
    RELATIVE    = 3   # موصول + صلة
    SENTENCE    = 4   # جملة → جملة (مفهومي)


# ── Dataclasses ───────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class RelationNode:
    """A single compositional relation between two pre-compositional nodes.

    Attributes
    ----------
    rel_type:     type of relation
    left_index:   positional index of the left / head node
    right_index:  positional index of the right / dependent node
    left_id:      ℙ(w_left)
    right_id:     ℙ(w_right)
    left_ctx:     𝕏_left  context id
    right_ctx:    𝕏_right context id
    economy:      ExactDecimal — structural possibility weight
    identity:     single fractal id for this relation node
    """

    rel_type:     RelationType
    left_index:   int
    right_index:  int
    left_id:      int
    right_id:     int
    left_ctx:     int
    right_ctx:    int
    economy:      ExactDecimal
    identity:     int


@dataclass(frozen=True, slots=True)
class DerivedNode:
    """A knowledge node derived from a relation (e.g. agent-hood).

    Attributes
    ----------
    derived_type: FAI_LIYYA / MAF_ULIYYA / SABABIYYA / MUSABBABIYYA
    primary_id:   ℙ(w) of the verb / cause node
    secondary_id: ℙ(w) of the noun / effect node
    relation_id:  RelationNode.identity that generated this derived node
    identity:     single fractal id
    """

    derived_type: DerivedType
    primary_id:   int
    secondary_id: int
    relation_id:  int
    identity:     int


@dataclass(frozen=True, slots=True)
class ReferenceNode:
    """An anaphoric or conceptual reference link.

    Attributes
    ----------
    ref_mode:     EXPLICIT / IMPLICIT / RELATIVE / SENTENCE
    source_id:    ℙ(w) of the referring element
    target_id:    ℙ(w) or Σ(clause) of the referent
    distance:     ExactDecimal encoding structural closeness
    identity:     single fractal id
    """

    ref_mode:   ReferenceMode
    source_id:  int
    target_id:  int
    distance:   ExactDecimal
    identity:   int


# ── Constructors ──────────────────────────────────────────────────────


def make_relation_node(
    rel_type: RelationType,
    left_index: int,
    right_index: int,
    left_id: int,
    right_id: int,
    left_ctx: int = 0,
    right_ctx: int = 0,
    economy: tuple[int, int] = READY_FULL,
) -> RelationNode:
    """ℛ_τ(i,j) = F( π(rel_type,τ), π(L,l_id), π(R,r_id),
                        π(Xl,l_ctx), π(Xr,r_ctx), π(e,econ) )."""
    econ = ExactDecimal.from_pair(economy)
    identity = fractal_fold([
        cantor_pair(1, int(rel_type)),
        cantor_pair(2, left_id),
        cantor_pair(3, right_id),
        cantor_pair(4, left_ctx),
        cantor_pair(5, right_ctx),
        cantor_pair(6, econ.fractal_id()),
    ])
    return RelationNode(
        rel_type=rel_type,
        left_index=left_index,
        right_index=right_index,
        left_id=left_id,
        right_id=right_id,
        left_ctx=left_ctx,
        right_ctx=right_ctx,
        economy=econ,
        identity=identity,
    )


def make_derived_node(
    derived_type: DerivedType,
    primary_id: int,
    secondary_id: int,
    relation_id: int,
) -> DerivedNode:
    """Derived node from an ISNAD relation."""
    identity = fractal_fold([
        cantor_pair(1, int(derived_type)),
        cantor_pair(2, primary_id),
        cantor_pair(3, secondary_id),
        cantor_pair(4, relation_id),
    ])
    return DerivedNode(
        derived_type=derived_type,
        primary_id=primary_id,
        secondary_id=secondary_id,
        relation_id=relation_id,
        identity=identity,
    )


def make_reference_node(
    ref_mode: ReferenceMode,
    source_id: int,
    target_id: int,
    distance: tuple[int, int] = READY_FULL,
) -> ReferenceNode:
    """ℌ(i,j) — explicit or implicit reference link."""
    dist = ExactDecimal.from_pair(distance)
    identity = fractal_fold([
        cantor_pair(1, int(ref_mode)),
        cantor_pair(2, source_id),
        cantor_pair(3, target_id),
        cantor_pair(4, dist.fractal_id()),
    ])
    return ReferenceNode(
        ref_mode=ref_mode,
        source_id=source_id,
        target_id=target_id,
        distance=dist,
        identity=identity,
    )
