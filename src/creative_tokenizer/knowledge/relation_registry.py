"""Relation registry — formal catalogue of upper-ontology relations.

The registry wraps the twelve transitions already defined in
:mod:`~creative_tokenizer.morphology.upper_ontology` and adds:

* ``RelationKind`` — an ``IntEnum`` mirroring ``TransitionKind`` but starting
  from 0 for convenience in lookup tables.
* ``RelationEntry`` — extended metadata for each relation (source, target,
  kind, governing constraints).
* ``RelationRegistry`` — the singleton catalogue with lookup and validation
  helpers.
* ``validate_concept`` — concept-gate function that rejects any new concept
  that does not declare both an upstream and a downstream relation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from ..morphology.upper_ontology import (
    UPPER_TRANSITIONS,
    ConstraintIndex,
    NodeIndex,
    TransitionKind,
)

__all__ = [
    "ConceptProposal",
    "RelationEntry",
    "RelationKind",
    "RelationRegistry",
    "validate_concept",
]


# ═══════════════════════════════════════════════════════════════════════
# §1  Relation kind enum (mirrors TransitionKind, zero-based)
# ═══════════════════════════════════════════════════════════════════════


class RelationKind(IntEnum):
    """Twelve relation kinds — zero-based mirror of ``TransitionKind``."""

    SUBJECT = 0       # موضوع (Reality → Sense)
    TRANSFER = 1      # نقل (Sense → Prior Knowledge)
    INTERPRET = 2     # تفسير (Prior Knowledge → Binding)
    SYNTHESISE = 3    # تركيب (Binding → Judgement)
    PRODUCE = 4       # إنتاج (Judgement → Signifier)
    REPRESENT = 5     # تمثيل (Signifier → Composition)
    REFER = 6         # إحالة (Composition → Signification)
    TRANSIT = 7       # انتقال (Signification → Truth/Falsehood)
    EVALUATE = 8      # تقويم (Truth/Falsehood → Guidance)
    DIRECT = 9        # توجيه (Guidance → Action)
    BEAR_FRUIT = 10   # إثمار (Action → Outcome)
    FEEDBACK = 11     # إرجاع (Outcome → Prior Knowledge)


# ═══════════════════════════════════════════════════════════════════════
# §2  Relation entry
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class RelationEntry:
    """A single catalogued relation between two ontology nodes."""

    source_node: NodeIndex
    target_node: NodeIndex
    kind: RelationKind
    label_ar: str
    label_en: str
    constraints: tuple[ConstraintIndex, ...]


# ═══════════════════════════════════════════════════════════════════════
# §3  Registry  (builds from existing upper-ontology transitions)
# ═══════════════════════════════════════════════════════════════════════


# Mapping from TransitionKind → RelationKind
_TK_TO_RK: dict[TransitionKind, RelationKind] = {
    TransitionKind.SUBJECT: RelationKind.SUBJECT,
    TransitionKind.TRANSFER: RelationKind.TRANSFER,
    TransitionKind.INTERPRET: RelationKind.INTERPRET,
    TransitionKind.SYNTHESISE: RelationKind.SYNTHESISE,
    TransitionKind.PRODUCE: RelationKind.PRODUCE,
    TransitionKind.REPRESENT: RelationKind.REPRESENT,
    TransitionKind.REFER: RelationKind.REFER,
    TransitionKind.TRANSIT: RelationKind.TRANSIT,
    TransitionKind.EVALUATE: RelationKind.EVALUATE,
    TransitionKind.DIRECT: RelationKind.DIRECT,
    TransitionKind.BEAR_FRUIT: RelationKind.BEAR_FRUIT,
    TransitionKind.FEEDBACK: RelationKind.FEEDBACK,
}

# Constraint mapping: which ConstraintIndex applies to which transition.
# Derived from the 8 governing constraints in upper_ontology.
_TRANSITION_CONSTRAINTS: dict[tuple[NodeIndex, NodeIndex], tuple[ConstraintIndex, ...]] = {
    (NodeIndex.BINDING, NodeIndex.JUDGEMENT): (ConstraintIndex.NO_JUDGEMENT_WITHOUT_BINDING,),
    (NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING): (
        ConstraintIndex.NO_BINDING_WITHOUT_PRIOR,
        ConstraintIndex.NO_PRIOR_WITH_OPINION_CONTAMINATION,
    ),
    (NodeIndex.SIGNIFIER, NodeIndex.COMPOSITION): (
        ConstraintIndex.NO_SIGNIFIER_WITHOUT_CONVENTION,
    ),
    (NodeIndex.COMPOSITION, NodeIndex.SIGNIFICATION): (
        ConstraintIndex.NO_SIGNIFICATION_WITHOUT_SAFEGUARD,
    ),
    (NodeIndex.TRUTH_VALUE, NodeIndex.GUIDANCE): (
        ConstraintIndex.NO_EVALUATION_WITHOUT_STANDARD,
        ConstraintIndex.NO_GUIDANCE_WITHOUT_TRUTH,
    ),
    (NodeIndex.ACTION, NodeIndex.OUTCOME): (
        ConstraintIndex.NO_KNOWLEDGE_WITHOUT_FRUIT,
    ),
}


def _build_entries() -> tuple[RelationEntry, ...]:
    entries: list[RelationEntry] = []
    for tr in UPPER_TRANSITIONS:
        rk = _TK_TO_RK[tr.kind]
        constraints = _TRANSITION_CONSTRAINTS.get((tr.source, tr.target), ())
        entries.append(RelationEntry(
            source_node=tr.source,
            target_node=tr.target,
            kind=rk,
            label_ar=tr.label_ar,
            label_en=tr.label_en,
            constraints=constraints,
        ))
    return tuple(entries)


class RelationRegistry:
    """Catalogue of all twelve upper-ontology relations.

    Acts as a singleton lookup table.
    """

    def __init__(self, entries: tuple[RelationEntry, ...] | None = None) -> None:
        self._entries = entries if entries is not None else _build_entries()

    @property
    def entries(self) -> tuple[RelationEntry, ...]:
        return self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def by_kind(self, kind: RelationKind) -> RelationEntry | None:
        for e in self._entries:
            if e.kind == kind:
                return e
        return None

    def by_source(self, node: NodeIndex) -> list[RelationEntry]:
        return [e for e in self._entries if e.source_node == node]

    def by_target(self, node: NodeIndex) -> list[RelationEntry]:
        return [e for e in self._entries if e.target_node == node]

    def between(self, src: NodeIndex, tgt: NodeIndex) -> RelationEntry | None:
        for e in self._entries:
            if e.source_node == src and e.target_node == tgt:
                return e
        return None


# Module-level default registry
DEFAULT_REGISTRY = RelationRegistry()


# ═══════════════════════════════════════════════════════════════════════
# §4  Concept gate
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class ConceptProposal:
    """A proposed concept that must pass the concept gate.

    ``source_node`` and ``target_node`` identify where the concept
    plugs into the ontology chain.  ``upstream_kind`` and
    ``downstream_kind`` must match known relation kinds.
    """

    name_ar: str
    name_en: str
    source_node: NodeIndex
    target_node: NodeIndex
    upstream_kind: RelationKind
    downstream_kind: RelationKind


def validate_concept(
    proposal: ConceptProposal,
    registry: RelationRegistry | None = None,
) -> list[str]:
    """Validate a concept proposal against the relation registry.

    Returns a list of error messages (empty if valid).  A concept is
    rejected if:
    * source_node or target_node is missing,
    * upstream_kind does not correspond to a known relation targeting
      source_node,
    * downstream_kind does not correspond to a known relation sourcing
      from target_node.
    """
    reg = registry or DEFAULT_REGISTRY
    errors: list[str] = []

    # Check upstream: is there a relation of upstream_kind *targeting* source_node?
    inbound = reg.by_target(proposal.source_node)
    if not any(e.kind == proposal.upstream_kind for e in inbound):
        errors.append(
            f"لا علاقة واردة من نوع {proposal.upstream_kind.name} "
            f"إلى العقدة {proposal.source_node.name}"
        )

    # Check downstream: is there a relation of downstream_kind *sourcing* from target_node?
    outbound = reg.by_source(proposal.target_node)
    if not any(e.kind == proposal.downstream_kind for e in outbound):
        errors.append(
            f"لا علاقة صادرة من نوع {proposal.downstream_kind.name} "
            f"من العقدة {proposal.target_node.name}"
        )

    return errors
