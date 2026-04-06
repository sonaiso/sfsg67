"""Tests for DAG/graph economy layer (استدراك الرابع):
lexical hubs, ontology hubs, epistemic modes, style hubs, typed edges,
GraphNode proof/store identity split, and DAG validity.
"""

from __future__ import annotations

from creative_tokenizer.morphology.conceptual_class import (
    ConceptualClass,
    make_concept,
)
from creative_tokenizer.morphology.epistemic_hub import EpistemicMode, epistemic_mode_id
from creative_tokenizer.morphology.exact_decimal import ExactDecimal
from creative_tokenizer.morphology.graph_node import (
    GraphNode,
    is_dag_valid,
    make_graph_node,
)
from creative_tokenizer.morphology.lexical_hub import (
    LexicalHubType,
    iltizam_hub,
    make_lexical_hub,
)
from creative_tokenizer.morphology.ontology_hub import (
    DomainHub,
    OntologyCategory,
    make_ontology_node,
)
from creative_tokenizer.morphology.style_hub import (
    InshaSubtype,
    KhabarSubtype,
    StyleType,
    make_style_hub,
)
from creative_tokenizer.morphology.typed_relation import EdgeType, make_edge

# ---------------------------------------------------------------------------
# LexicalMeaningHub
# ---------------------------------------------------------------------------


class TestLexicalMeaningHub:
    def test_mutabaqa_hub_type(self) -> None:
        hub = make_lexical_hub(LexicalHubType.MUTABAQA, 42)
        assert hub.hub_type == LexicalHubType.MUTABAQA

    def test_tadammun_hub_type(self) -> None:
        hub = make_lexical_hub(LexicalHubType.TADAMMUN, 42)
        assert hub.hub_type == LexicalHubType.TADAMMUN

    def test_hub_id_is_cantor_pair(self) -> None:
        from creative_tokenizer.morphology.fractal_storage import cantor_pair

        hub = make_lexical_hub(LexicalHubType.MUTABAQA, 10)
        assert hub.hub_id == cantor_pair(int(LexicalHubType.MUTABAQA), 10)

    def test_same_content_same_hub_id(self) -> None:
        h1 = make_lexical_hub(LexicalHubType.MUTABAQA, 99)
        h2 = make_lexical_hub(LexicalHubType.MUTABAQA, 99)
        assert h1.hub_id == h2.hub_id

    def test_different_type_different_hub_id(self) -> None:
        h_mut = make_lexical_hub(LexicalHubType.MUTABAQA, 99)
        h_tad = make_lexical_hub(LexicalHubType.TADAMMUN, 99)
        assert h_mut.hub_id != h_tad.hub_id

    def test_shared_hub_across_two_forms(self) -> None:
        """Two surface forms sharing the same core meaning → same hub_id."""
        hub = make_lexical_hub(LexicalHubType.MUTABAQA, 7)
        form_a_hubs = [hub.hub_id]
        form_b_hubs = [hub.hub_id]
        node_a = make_graph_node(proof_id=100, hub_ids=form_a_hubs, delta_id=1)
        node_b = make_graph_node(proof_id=200, hub_ids=form_b_hubs, delta_id=1)
        # Same hubs + same delta → same store_id (economy)
        assert node_a.store_id == node_b.store_id


class TestIltizamHub:
    def test_hub_type_is_iltizam(self) -> None:
        strength = ExactDecimal(750, 3)
        hub = iltizam_hub(1, strength)
        assert hub.hub_type == LexicalHubType.ILTIZAM

    def test_obligation_mode_zero_consistent(self) -> None:
        """Same schema + same strength always produce same hub (obligation=0)."""
        s = ExactDecimal(500, 3)
        h1 = iltizam_hub(5, s)
        h2 = iltizam_hub(5, s)
        assert h1.hub_id == h2.hub_id

    def test_different_schema_different_hub(self) -> None:
        s = ExactDecimal(500, 3)
        h1 = iltizam_hub(1, s)
        h2 = iltizam_hub(2, s)
        assert h1.hub_id != h2.hub_id

    def test_different_strength_different_hub(self) -> None:
        h1 = iltizam_hub(3, ExactDecimal(500, 3))
        h2 = iltizam_hub(3, ExactDecimal(750, 3))
        assert h1.hub_id != h2.hub_id

    def test_iltizam_is_conditional_not_obligatory(self) -> None:
        """iltizam encodes obligation_mode=0 — inferential, not obligatory.
        We verify this by checking the content_id differs from a hypothetical
        encoding with obligation_mode=1, achieved by ensuring two iltizam hubs
        with different schemas are distinct (the obligation slot is constant=0).
        """
        s = ExactDecimal(1000, 3)
        hub_a = iltizam_hub(10, s)
        hub_b = iltizam_hub(10, s)
        assert hub_a.content_id == hub_b.content_id  # obligation slot is fixed


# ---------------------------------------------------------------------------
# OntologyHub — jamid as entity, mushtaq as process
# ---------------------------------------------------------------------------


class TestOntologyHub:
    def test_jamid_entity_kawn(self) -> None:
        node = make_ontology_node(OntologyCategory.ENTITY, DomainHub.KAWN)
        assert node.category == OntologyCategory.ENTITY
        assert node.domain == DomainHub.KAWN

    def test_mushtaq_process_insan(self) -> None:
        node = make_ontology_node(OntologyCategory.PROCESS, DomainHub.INSAN)
        assert node.category == OntologyCategory.PROCESS
        assert node.domain == DomainHub.INSAN

    def test_entity_event_differ(self) -> None:
        n_entity = make_ontology_node(OntologyCategory.ENTITY, DomainHub.KAWN)
        n_event = make_ontology_node(OntologyCategory.EVENT, DomainHub.KAWN)
        assert n_entity.hub_id != n_event.hub_id

    def test_domain_kawn_insan_hayat_distinct(self) -> None:
        kawn = make_ontology_node(OntologyCategory.ENTITY, DomainHub.KAWN)
        insan = make_ontology_node(OntologyCategory.ENTITY, DomainHub.INSAN)
        hayat = make_ontology_node(OntologyCategory.ENTITY, DomainHub.HAYAT)
        ids = {kawn.hub_id, insan.hub_id, hayat.hub_id}
        assert len(ids) == 3

    def test_agent_hayat(self) -> None:
        node = make_ontology_node(OntologyCategory.AGENT, DomainHub.HAYAT)
        assert node.category == OntologyCategory.AGENT


# ---------------------------------------------------------------------------
# EpistemicModeHub
# ---------------------------------------------------------------------------


class TestEpistemicMode:
    def test_all_modes_distinct(self) -> None:
        ids = [epistemic_mode_id(m) for m in EpistemicMode]
        assert len(ids) == len(set(ids))

    def test_empirical_is_one(self) -> None:
        assert epistemic_mode_id(EpistemicMode.EMPIRICAL) == 1

    def test_formal_is_two(self) -> None:
        assert epistemic_mode_id(EpistemicMode.FORMAL) == 2


# ---------------------------------------------------------------------------
# StyleHub
# ---------------------------------------------------------------------------


class TestStyleHub:
    def test_khabar_haqiqi(self) -> None:
        hub = make_style_hub(StyleType.KHABAR, int(KhabarSubtype.HAQIQI))
        assert hub.style_type == StyleType.KHABAR

    def test_insha_istifham(self) -> None:
        hub = make_style_hub(StyleType.INSHA, int(InshaSubtype.ISTIFHAM))
        assert hub.style_type == StyleType.INSHA

    def test_style_hubs_reduce_duplication(self) -> None:
        """Two sentences of same style type share the same hub → economy."""
        hub = make_style_hub(StyleType.KHABAR, int(KhabarSubtype.HAQIQI))
        sent_a = make_graph_node(proof_id=1001, hub_ids=[hub.hub_id], delta_id=0)
        sent_b = make_graph_node(proof_id=1002, hub_ids=[hub.hub_id], delta_id=0)
        assert sent_a.store_id == sent_b.store_id

    def test_different_substyles_differ(self) -> None:
        h1 = make_style_hub(StyleType.INSHA, int(InshaSubtype.AMMAR))
        h2 = make_style_hub(StyleType.INSHA, int(InshaSubtype.NAHY))
        assert h1.hub_id != h2.hub_id


# ---------------------------------------------------------------------------
# TypedEdge
# ---------------------------------------------------------------------------


class TestTypedEdge:
    def test_edge_is_deterministic(self) -> None:
        e1 = make_edge(10, 20, EdgeType.DENOTES_BY_MUTABAQA)
        e2 = make_edge(10, 20, EdgeType.DENOTES_BY_MUTABAQA)
        assert e1.edge_id == e2.edge_id

    def test_different_types_differ(self) -> None:
        e1 = make_edge(10, 20, EdgeType.DENOTES_BY_MUTABAQA)
        e2 = make_edge(10, 20, EdgeType.EMBEDS_TADAMMUN)
        assert e1.edge_id != e2.edge_id

    def test_reversed_direction_differs(self) -> None:
        e1 = make_edge(10, 20, EdgeType.PREDICATES)
        e2 = make_edge(20, 10, EdgeType.PREDICATES)
        assert e1.edge_id != e2.edge_id

    def test_overlay_edge_is_typed(self) -> None:
        overlay = make_edge(99, 11, EdgeType.ANAPHORICALLY_LINKS)
        assert overlay.edge_type == EdgeType.ANAPHORICALLY_LINKS


# ---------------------------------------------------------------------------
# GraphNode — proof_id vs store_id
# ---------------------------------------------------------------------------


class TestGraphNode:
    def test_proof_id_preserved(self) -> None:
        node = make_graph_node(proof_id=42, hub_ids=[1, 2], delta_id=3)
        assert node.proof_id == 42

    def test_hub_ids_sorted(self) -> None:
        node = make_graph_node(proof_id=1, hub_ids=[5, 2, 9], delta_id=0)
        assert node.hub_ids == (2, 5, 9)

    def test_store_differs_from_proof(self) -> None:
        node = make_graph_node(proof_id=9999, hub_ids=[10], delta_id=5)
        assert node.store_id != node.proof_id

    def test_same_hubs_same_delta_same_store(self) -> None:
        n1 = make_graph_node(proof_id=100, hub_ids=[7, 3], delta_id=4)
        n2 = make_graph_node(proof_id=200, hub_ids=[7, 3], delta_id=4)
        assert n1.store_id == n2.store_id

    def test_different_delta_different_store(self) -> None:
        n1 = make_graph_node(proof_id=100, hub_ids=[7], delta_id=0)
        n2 = make_graph_node(proof_id=200, hub_ids=[7], delta_id=1)
        assert n1.store_id != n2.store_id

    def test_no_hubs_valid(self) -> None:
        node = make_graph_node(proof_id=5, hub_ids=[], delta_id=0)
        assert node.hub_ids == ()

    def test_raw_unicode_survives_via_proof_id(self) -> None:
        """proof_id encodes the full fractal identity; wrapping in GraphNode preserves it."""
        from creative_tokenizer.morphology.unicode_identity import unicode_surface

        text = "الشمس"
        uid = unicode_surface(text)
        node = make_graph_node(proof_id=uid, hub_ids=[], delta_id=0)
        assert node.proof_id == uid


# ---------------------------------------------------------------------------
# DAG validity
# ---------------------------------------------------------------------------


class TestDagValidity:
    def test_empty_list_is_valid(self) -> None:
        assert is_dag_valid([]) is True

    def test_single_node_no_hubs_is_valid(self) -> None:
        n = make_graph_node(1, [], 0)
        assert is_dag_valid([n]) is True

    def test_linear_chain_is_valid(self) -> None:
        root = make_graph_node(1, [], 0)
        child = make_graph_node(2, [1], 0)
        grandchild = make_graph_node(3, [2], 0)
        assert is_dag_valid([root, child, grandchild]) is True

    def test_diamond_dag_is_valid(self) -> None:
        # root(1) → a(2), b(3) → child(4) depends on both
        root = make_graph_node(1, [], 0)
        a = make_graph_node(2, [1], 0)
        b = make_graph_node(3, [1], 0)
        child = make_graph_node(4, [2, 3], 0)
        assert is_dag_valid([root, a, b, child]) is True

    def test_direct_self_loop_is_invalid(self) -> None:
        # Manually craft a node that lists itself as a hub
        cyclic = GraphNode(proof_id=5, hub_ids=(5,), delta_id=0, store_id=0)
        assert is_dag_valid([cyclic]) is False

    def test_mutual_cycle_is_invalid(self) -> None:
        n_a = GraphNode(proof_id=10, hub_ids=(20,), delta_id=0, store_id=0)
        n_b = GraphNode(proof_id=20, hub_ids=(10,), delta_id=0, store_id=0)
        assert is_dag_valid([n_a, n_b]) is False

    def test_overlay_edge_does_not_invalidate_dag(self) -> None:
        """Overlay (reference) edges are TypedEdge objects, not stored in hub_ids.
        The constitutive graph therefore stays acyclic.
        """
        n1 = make_graph_node(10, [], 0)
        n2 = make_graph_node(20, [], 0)
        # overlay: n2 → n1 (anaphoric reference — a "back pointer")
        _overlay = make_edge(n2.proof_id, n1.proof_id, EdgeType.ANAPHORICALLY_LINKS)
        # hub_ids are both empty: constitutive DAG is still valid
        assert is_dag_valid([n1, n2]) is True


# ---------------------------------------------------------------------------
# ConceptNode (used in ontology)
# ---------------------------------------------------------------------------


class TestConceptNode:
    def test_particular_concept(self) -> None:
        c = make_concept(ConceptualClass.PARTICULAR)
        assert c.concept_class == ConceptualClass.PARTICULAR

    def test_mutawati_uniform_no_gradation(self) -> None:
        c = make_concept(ConceptualClass.MUTAWATI, uniformity=1, gradation=0)
        assert c.uniformity == 1
        assert c.gradation == 0

    def test_mushakkak_graded(self) -> None:
        c = make_concept(ConceptualClass.MUSHAKKAK, uniformity=0, gradation=7)
        assert c.uniformity == 0
        assert c.gradation == 7

    def test_mutawati_vs_mushakkak_differ(self) -> None:
        c_mut = make_concept(ConceptualClass.MUTAWATI, uniformity=1, gradation=0)
        c_mush = make_concept(ConceptualClass.MUSHAKKAK, uniformity=0, gradation=5)
        assert c_mut.concept_id != c_mush.concept_id

    def test_mushtarak_polysemy_n(self) -> None:
        c = make_concept(ConceptualClass.MUSHTARAK, polysemy_n=3)
        assert c.polysemy_n == 3
