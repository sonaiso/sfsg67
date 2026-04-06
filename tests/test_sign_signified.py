"""Tests for sign-signified coupling, conceptual classification, transfer,
metaphor, semantic resolution functions, and conflict resolution.
"""

from __future__ import annotations

import pytest

from creative_tokenizer.morphology.conceptual_class import (
    ConceptualClass,
    make_concept,
)
from creative_tokenizer.morphology.conflict_resolution import (
    InterpretationPath,
    resolve_conflict,
    score_path,
)
from creative_tokenizer.morphology.epistemic_hub import EpistemicMode, epistemic_mode_id
from creative_tokenizer.morphology.metaphor import (
    MetaphorType,
    make_compositional_metaphor,
    make_lexical_metaphor,
)
from creative_tokenizer.morphology.ontology_hub import (
    DomainHub,
    OntologyCategory,
    make_ontology_node,
)
from creative_tokenizer.morphology.semantic_functions import (
    resolve_idmar,
    resolve_ishtirak,
    resolve_takhsis,
)
from creative_tokenizer.morphology.sign_signified import (
    CouplingType,
    make_coupling,
    make_signified,
)
from creative_tokenizer.morphology.transfer_sense import TransferType, make_transfer

# ---------------------------------------------------------------------------
# SignifiedNode
# ---------------------------------------------------------------------------


class TestSignifiedNode:
    def test_basic_construction(self) -> None:
        onto = make_ontology_node(OntologyCategory.ENTITY, DomainHub.KAWN)
        ep = epistemic_mode_id(EpistemicMode.EMPIRICAL)
        c = make_concept(ConceptualClass.UNIVERSAL)
        sg = make_signified(
            ontology_id=onto.hub_id,
            epistemic_id=ep,
            universality=2,
            kind_id=c.concept_id,
        )
        assert sg.ontology_id == onto.hub_id
        assert sg.epistemic_id == ep
        assert sg.universality == 2

    def test_different_ontology_different_signified(self) -> None:
        entity = make_ontology_node(OntologyCategory.ENTITY, DomainHub.KAWN)
        process = make_ontology_node(OntologyCategory.PROCESS, DomainHub.INSAN)
        sg_e = make_signified(entity.hub_id, 1, 2, 0)
        sg_p = make_signified(process.hub_id, 1, 2, 0)
        assert sg_e.signified_id != sg_p.signified_id

    def test_relations_id_optional(self) -> None:
        sg = make_signified(1, 1, 1, 1)
        assert sg.relations_id == 0

    def test_deterministic(self) -> None:
        sg1 = make_signified(10, 2, 1, 5, 3)
        sg2 = make_signified(10, 2, 1, 5, 3)
        assert sg1.signified_id == sg2.signified_id


# ---------------------------------------------------------------------------
# SignSignifiedCoupling — mutabaqa vs tadammun vs iltizam
# ---------------------------------------------------------------------------


class TestSignSignifiedCoupling:
    def _sig(self, onto_cat: OntologyCategory) -> int:
        onto = make_ontology_node(onto_cat, DomainHub.KAWN)
        concept = make_concept(ConceptualClass.UNIVERSAL)
        sg = make_signified(onto.hub_id, 1, 2, concept.concept_id)
        return sg.signified_id

    def test_wadi_asli_coupling(self) -> None:
        c = make_coupling(sign_id=1, signified_id=100, coupling_type=CouplingType.WADI_ASLI)
        assert c.coupling_type == CouplingType.WADI_ASLI

    def test_mutabaqa_vs_majazi_differ(self) -> None:
        c_lit = make_coupling(1, 100, CouplingType.WADI_ASLI)
        c_maj = make_coupling(1, 100, CouplingType.MAJAZI)
        assert c_lit.coupling_id != c_maj.coupling_id

    def test_strength_affects_coupling_id(self) -> None:
        c_full = make_coupling(1, 100, CouplingType.WADI_ASLI, (1000, 3))
        c_half = make_coupling(1, 100, CouplingType.WADI_ASLI, (500, 3))
        assert c_full.coupling_id != c_half.coupling_id

    def test_same_sign_different_signifieds_differ(self) -> None:
        c1 = make_coupling(1, 10, CouplingType.MUSHTARAK)
        c2 = make_coupling(1, 20, CouplingType.MUSHTARAK)
        assert c1.coupling_id != c2.coupling_id

    def test_mutaradif_same_signified_different_signs(self) -> None:
        """Synonym hub: two signs map to the same signified."""
        c1 = make_coupling(sign_id=5, signified_id=99, coupling_type=CouplingType.MUTARADIF)
        c2 = make_coupling(sign_id=6, signified_id=99, coupling_type=CouplingType.MUTARADIF)
        # Different signs → different coupling_ids, but same signified_id
        assert c1.signified_id == c2.signified_id
        assert c1.coupling_id != c2.coupling_id


# ---------------------------------------------------------------------------
# ConceptualClass — universal subtypes
# ---------------------------------------------------------------------------


class TestConceptualClass:
    def test_universal_mutawati_no_gradation(self) -> None:
        c = make_concept(ConceptualClass.MUTAWATI, uniformity=1, gradation=0)
        assert c.concept_class == ConceptualClass.MUTAWATI
        assert c.gradation == 0

    def test_universal_mushakkak_has_gradation(self) -> None:
        """نور: graded universal — intensity varies (dim candle to bright sun)."""
        c = make_concept(ConceptualClass.MUSHAKKAK, uniformity=0, gradation=3)
        assert c.concept_class == ConceptualClass.MUSHAKKAK
        assert c.gradation == 3

    def test_mushakkak_different_grades_differ(self) -> None:
        c1 = make_concept(ConceptualClass.MUSHAKKAK, uniformity=0, gradation=1)
        c2 = make_concept(ConceptualClass.MUSHAKKAK, uniformity=0, gradation=5)
        assert c1.concept_id != c2.concept_id

    def test_mutabayin_no_shared_core(self) -> None:
        c = make_concept(ConceptualClass.MUTABAYIN, shared_core=0)
        assert c.shared_core == 0

    def test_mushtarak_polysemy_context_separates(self) -> None:
        """عين — one sign, multiple signifieds: polysemy_n > 1."""
        c = make_concept(ConceptualClass.MUSHTARAK, polysemy_n=4)
        assert c.polysemy_n == 4

    def test_particular_vs_universal_distinct(self) -> None:
        part = make_concept(ConceptualClass.PARTICULAR)
        univ = make_concept(ConceptualClass.UNIVERSAL)
        assert part.concept_id != univ.concept_id


# ---------------------------------------------------------------------------
# TransferSense
# ---------------------------------------------------------------------------


class TestTransferSense:
    def test_wadi_asli_transfer(self) -> None:
        t = make_transfer(10, 10, TransferType.WADI_ASLI)
        assert t.transfer_type == TransferType.WADI_ASLI

    def test_urfi_transfer(self) -> None:
        t = make_transfer(source_sense_id=10, target_sense_id=11, transfer_type=TransferType.URFI)
        assert t.transfer_type == TransferType.URFI
        assert t.source_sense_id == 10
        assert t.target_sense_id == 11

    def test_istilahi_transfer(self) -> None:
        t = make_transfer(10, 15, TransferType.ISTILAHI)
        assert t.transfer_type == TransferType.ISTILAHI

    def test_domain_specific_with_domain_id(self) -> None:
        t = make_transfer(10, 20, TransferType.DOMAIN_SPEC, domain_id=5)
        assert t.domain_id == 5

    def test_different_target_different_transfer(self) -> None:
        t1 = make_transfer(10, 11, TransferType.URFI)
        t2 = make_transfer(10, 12, TransferType.URFI)
        assert t1.transfer_id != t2.transfer_id

    def test_same_transfer_deterministic(self) -> None:
        t1 = make_transfer(5, 8, TransferType.ISTILAHI, 3)
        t2 = make_transfer(5, 8, TransferType.ISTILAHI, 3)
        assert t1.transfer_id == t2.transfer_id


# ---------------------------------------------------------------------------
# Metaphor nodes
# ---------------------------------------------------------------------------


class TestLexicalMetaphor:
    def test_basic_lexical_metaphor(self) -> None:
        """علي أسد — Ali is a lion (metaphor by similarity)."""
        m = make_lexical_metaphor(
            literal_source_id=100,
            blocking_condition=1,   # person ≠ animal: literal blocked
            qarina_id=5,            # قرينة: human subject
            figurative_target_id=200,
            metaphor_type=MetaphorType.MUSHABAHA,
        )
        assert m.metaphor_type == MetaphorType.MUSHABAHA
        assert m.literal_source_id == 100

    def test_different_qarina_different_metaphor(self) -> None:
        m1 = make_lexical_metaphor(10, 1, 3, 20, MetaphorType.MUSHABAHA)
        m2 = make_lexical_metaphor(10, 1, 7, 20, MetaphorType.MUSHABAHA)
        assert m1.metaphor_id != m2.metaphor_id

    def test_different_metaphor_types_differ(self) -> None:
        m1 = make_lexical_metaphor(10, 1, 1, 20, MetaphorType.MUSHABAHA)
        m2 = make_lexical_metaphor(10, 1, 1, 20, MetaphorType.MUJAWARA)
        assert m1.metaphor_id != m2.metaphor_id

    def test_deterministic(self) -> None:
        m1 = make_lexical_metaphor(1, 2, 3, 4, MetaphorType.SABABIYYA)
        m2 = make_lexical_metaphor(1, 2, 3, 4, MetaphorType.SABABIYYA)
        assert m1.metaphor_id == m2.metaphor_id


class TestCompositionalMetaphor:
    def test_basic_compositional_metaphor(self) -> None:
        m = make_compositional_metaphor(
            sentence_id=500,
            blocking_condition=2,
            qarina_id=9,
            metaphor_type=MetaphorType.MUSHABAHA,
        )
        assert m.sentence_id == 500
        assert m.metaphor_type == MetaphorType.MUSHABAHA

    def test_different_sentence_different_metaphor(self) -> None:
        m1 = make_compositional_metaphor(10, 1, 2, MetaphorType.KULLIYYA)
        m2 = make_compositional_metaphor(20, 1, 2, MetaphorType.KULLIYYA)
        assert m1.metaphor_id != m2.metaphor_id


# ---------------------------------------------------------------------------
# Semantic resolution functions
# ---------------------------------------------------------------------------


class TestIstirakResolution:
    def test_first_candidate_selected(self) -> None:
        result = resolve_ishtirak(
            word_id=7,
            context_id=3,
            candidate_signifieds=[100, 200, 300],
        )
        assert result.selected_id == 100

    def test_different_context_different_resolution(self) -> None:
        r1 = resolve_ishtirak(7, 1, [100, 200])
        r2 = resolve_ishtirak(7, 2, [100, 200])
        assert r1.resolution_id != r2.resolution_id

    def test_candidate_tuple_preserved(self) -> None:
        result = resolve_ishtirak(1, 1, [10, 20, 30])
        assert result.candidate_signifieds == (10, 20, 30)

    def test_empty_candidates_selects_zero(self) -> None:
        result = resolve_ishtirak(1, 1, [])
        assert result.selected_id == 0


class TestIdmarResolution:
    def test_basic_idmar(self) -> None:
        result = resolve_idmar(
            clause_id=50,
            missing_element_type=1,
            reconstructed_id=99,
        )
        assert result.clause_id == 50
        assert result.reconstructed_id == 99

    def test_restoration_mode_default_zero(self) -> None:
        result = resolve_idmar(50, 1, 99)
        assert result.restoration_mode == 0

    def test_different_reconstruction_differ(self) -> None:
        r1 = resolve_idmar(50, 1, 99)
        r2 = resolve_idmar(50, 1, 88)
        assert r1.resolution_id != r2.resolution_id

    def test_deterministic(self) -> None:
        r1 = resolve_idmar(10, 2, 33, 1)
        r2 = resolve_idmar(10, 2, 33, 1)
        assert r1.resolution_id == r2.resolution_id


class TestTakhsisResolution:
    def test_basic_takhsis(self) -> None:
        result = resolve_takhsis(
            general_class_id=1000,
            restriction_ids=[5, 8],
        )
        assert result.general_class_id == 1000
        assert set(result.restriction_ids) == {5, 8}

    def test_restriction_ids_sorted(self) -> None:
        result = resolve_takhsis(1000, [9, 3, 7])
        assert result.restriction_ids == (3, 7, 9)

    def test_more_restrictions_narrower_space(self) -> None:
        r1 = resolve_takhsis(1000, [5])
        r2 = resolve_takhsis(1000, [5, 8])
        assert r1.remaining_space_id != r2.remaining_space_id

    def test_no_restriction_empty_tuple(self) -> None:
        r = resolve_takhsis(1000, [])
        assert r.restriction_ids == ()
        # remaining_space_id = π(general_class_id, 0) — cantor_pair, not identity
        from creative_tokenizer.morphology.fractal_storage import cantor_pair
        assert r.remaining_space_id == cantor_pair(r.general_class_id, 0)

    def test_deterministic(self) -> None:
        r1 = resolve_takhsis(50, [2, 4])
        r2 = resolve_takhsis(50, [2, 4])
        assert r1.resolution_id == r2.resolution_id


# ---------------------------------------------------------------------------
# Conflict resolution
# ---------------------------------------------------------------------------


class TestConflictResolution:
    def test_literal_beats_majazi_by_default(self) -> None:
        """LITERAL priority=7 × 10 = 70; MAJAZI=3 × 10=30; literal wins."""
        lit = score_path(InterpretationPath.LITERAL, signified_id=10)
        maj = score_path(InterpretationPath.MAJAZI, signified_id=20)
        resolution = resolve_conflict([maj, lit])
        assert resolution.winner.path_type == InterpretationPath.LITERAL

    def test_literal_beats_transferred(self) -> None:
        lit = score_path(InterpretationPath.LITERAL, signified_id=10)
        tra = score_path(InterpretationPath.TRANSFERRED, signified_id=11)
        resolution = resolve_conflict([tra, lit])
        assert resolution.winner.path_type == InterpretationPath.LITERAL

    def test_transferred_beats_takhsis(self) -> None:
        tra = score_path(InterpretationPath.TRANSFERRED, signified_id=11)
        tak = score_path(InterpretationPath.TAKHSIS, signified_id=12)
        resolution = resolve_conflict([tra, tak])
        assert resolution.winner.path_type == InterpretationPath.TRANSFERRED

    def test_single_path_wins(self) -> None:
        p = score_path(InterpretationPath.PROBABLE, signified_id=1)
        resolution = resolve_conflict([p])
        assert resolution.winner.path_type == InterpretationPath.PROBABLE

    def test_paths_ranked_descending(self) -> None:
        lit = score_path(InterpretationPath.LITERAL, signified_id=1)
        maj = score_path(InterpretationPath.MAJAZI, signified_id=2)
        prob = score_path(InterpretationPath.PROBABLE, signified_id=3)
        resolution = resolve_conflict([maj, prob, lit])
        scores = [p.total_score for p in resolution.paths]
        assert scores == sorted(scores, reverse=True)

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            resolve_conflict([])

    def test_total_score_reflects_priority(self) -> None:
        lit = score_path(InterpretationPath.LITERAL, signified_id=1)
        maj = score_path(InterpretationPath.MAJAZI, signified_id=1)
        assert lit.total_score > maj.total_score

    def test_context_fit_breaks_tie_between_same_type(self) -> None:
        """Two IDMAR paths with different context_fit: higher wins."""
        p1 = score_path(InterpretationPath.IDMAR, signified_id=1, context_fit=3)
        p2 = score_path(InterpretationPath.IDMAR, signified_id=2, context_fit=9)
        resolution = resolve_conflict([p1, p2])
        assert resolution.winner.signified_id == 2

    def test_resolution_id_deterministic(self) -> None:
        lit = score_path(InterpretationPath.LITERAL, signified_id=42)
        r1 = resolve_conflict([lit])
        r2 = resolve_conflict([lit])
        assert r1.resolution_id == r2.resolution_id
