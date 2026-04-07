"""Tests for the relation registry and concept gate — Sprint 3.

Tests verify:
  - Registry contains 12 base relations (one per transition).
  - Each relation has valid source/target node indices.
  - Lookup by kind, source, target works.
  - validate_concept rejects proposals with invalid upstream/downstream.
  - validate_concept accepts valid proposals.
"""

from creative_tokenizer.knowledge import (
    ConceptProposal,
    RelationKind,
    RelationRegistry,
    validate_concept,
)
from creative_tokenizer.morphology.upper_ontology import NodeIndex

# ── Registry basics ──────────────────────────────────────────────────


def test_registry_has_12_entries() -> None:
    reg = RelationRegistry()
    assert len(reg) == 12


def test_all_relation_kinds_present() -> None:
    reg = RelationRegistry()
    kinds = {e.kind for e in reg.entries}
    for rk in RelationKind:
        assert rk in kinds, f"missing relation kind {rk.name}"


def test_lookup_by_kind() -> None:
    reg = RelationRegistry()
    entry = reg.by_kind(RelationKind.SUBJECT)
    assert entry is not None
    assert entry.source_node == NodeIndex.REALITY
    assert entry.target_node == NodeIndex.SENSE


def test_lookup_by_source() -> None:
    reg = RelationRegistry()
    entries = reg.by_source(NodeIndex.REALITY)
    assert len(entries) == 1
    assert entries[0].kind == RelationKind.SUBJECT


def test_lookup_by_target() -> None:
    reg = RelationRegistry()
    entries = reg.by_target(NodeIndex.SENSE)
    assert len(entries) == 1
    assert entries[0].kind == RelationKind.SUBJECT


def test_lookup_between() -> None:
    reg = RelationRegistry()
    entry = reg.between(NodeIndex.SIGNIFIER, NodeIndex.COMPOSITION)
    assert entry is not None
    assert entry.kind == RelationKind.REPRESENT


def test_feedback_relation() -> None:
    reg = RelationRegistry()
    entry = reg.by_kind(RelationKind.FEEDBACK)
    assert entry is not None
    assert entry.source_node == NodeIndex.OUTCOME
    assert entry.target_node == NodeIndex.PRIOR_KNOWLEDGE


# ── Relation entries have labels ─────────────────────────────────────


def test_entries_have_bilingual_labels() -> None:
    reg = RelationRegistry()
    for entry in reg.entries:
        assert entry.label_ar, f"missing Arabic label for {entry.kind.name}"
        assert entry.label_en, f"missing English label for {entry.kind.name}"


# ── Concept gate ─────────────────────────────────────────────────────


def test_valid_concept_passes() -> None:
    proposal = ConceptProposal(
        name_ar="مفهوم اختباري",
        name_en="test concept",
        source_node=NodeIndex.SENSE,
        target_node=NodeIndex.PRIOR_KNOWLEDGE,
        upstream_kind=RelationKind.SUBJECT,      # Reality → Sense
        downstream_kind=RelationKind.INTERPRET,   # Prior Knowledge → Binding
    )
    errors = validate_concept(proposal)
    assert errors == []


def test_concept_missing_upstream_rejected() -> None:
    proposal = ConceptProposal(
        name_ar="مفهوم خاطئ",
        name_en="bad concept",
        source_node=NodeIndex.REALITY,
        target_node=NodeIndex.SENSE,
        upstream_kind=RelationKind.FEEDBACK,  # No feedback targets Reality
        downstream_kind=RelationKind.TRANSFER,
    )
    errors = validate_concept(proposal)
    assert len(errors) >= 1


def test_concept_missing_downstream_rejected() -> None:
    proposal = ConceptProposal(
        name_ar="مفهوم خاطئ ٢",
        name_en="bad concept 2",
        source_node=NodeIndex.SENSE,
        target_node=NodeIndex.OUTCOME,
        upstream_kind=RelationKind.SUBJECT,
        downstream_kind=RelationKind.SUBJECT,  # Outcome does not source SUBJECT
    )
    errors = validate_concept(proposal)
    assert len(errors) >= 1


def test_concept_missing_both_rejected() -> None:
    proposal = ConceptProposal(
        name_ar="مفهوم خاطئ تمامًا",
        name_en="totally bad",
        source_node=NodeIndex.REALITY,
        target_node=NodeIndex.OUTCOME,
        upstream_kind=RelationKind.EVALUATE,   # nothing of this kind targets REALITY
        downstream_kind=RelationKind.SUBJECT,  # OUTCOME does not source SUBJECT
    )
    errors = validate_concept(proposal)
    assert len(errors) == 2


def test_error_messages_in_arabic() -> None:
    proposal = ConceptProposal(
        name_ar="خطأ",
        name_en="error",
        source_node=NodeIndex.REALITY,
        target_node=NodeIndex.OUTCOME,
        upstream_kind=RelationKind.EVALUATE,
        downstream_kind=RelationKind.SUBJECT,
    )
    errors = validate_concept(proposal)
    for msg in errors:
        assert "لا علاقة" in msg
