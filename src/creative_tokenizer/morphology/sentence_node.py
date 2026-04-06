"""Sentence / clause node: the minimal closed compositional result.

Σ_k is formed from the fractal fold of:
    - all selected RelationNode identities
    - all IrabNode identities
    - all ReferenceNode identities
    - the head word's ℙ identity

It represents the minimal-closure output of one Arabic clause.
"""
from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import fractal_fold
from .irab_node import IrabNode
from .relation_nodes import DerivedNode, ReferenceNode, RelationNode


@dataclass(frozen=True, slots=True)
class SentenceNode:
    """A closed clause/sentence node produced by composition.

    Attributes
    ----------
    head_id:       ℙ(w) of the structural head (verb / predicate)
    relations:     accepted RelationNodes
    irab_nodes:    generated IrabNodes
    references:    ReferenceNodes
    derived:       DerivedNodes (fai'liyya, maf'uliyya …)
    identity:      single fractal id for this clause
    """

    head_id:    int
    relations:  tuple[RelationNode, ...]
    irab_nodes: tuple[IrabNode, ...]
    references: tuple[ReferenceNode, ...]
    derived:    tuple[DerivedNode, ...]
    identity:   int


def make_sentence_node(
    head_id: int,
    relations: list[RelationNode],
    irab_nodes: list[IrabNode],
    references: list[ReferenceNode] | None = None,
    derived: list[DerivedNode] | None = None,
) -> SentenceNode:
    """Compose Σ_k from its constituent nodes.

    identity = F( head_id,
                  F(relation identities…),
                  F(irab identities…),
                  F(reference identities…),
                  F(derived identities…) )
    """
    refs: list[ReferenceNode] = list(references or [])
    drvd: list[DerivedNode] = list(derived or [])

    def fold_ids(
        nodes: (
            list[RelationNode]
            | list[IrabNode]
            | list[ReferenceNode]
            | list[DerivedNode]
        ),
    ) -> int:
        return fractal_fold([n.identity for n in nodes]) if nodes else 0

    identity = fractal_fold([
        head_id,
        fold_ids(relations),
        fold_ids(irab_nodes),
        fold_ids(refs),
        fold_ids(drvd),
    ])
    return SentenceNode(
        head_id=head_id,
        relations=tuple(relations),
        irab_nodes=tuple(irab_nodes),
        references=tuple(refs),
        derived=tuple(drvd),
        identity=identity,
    )
