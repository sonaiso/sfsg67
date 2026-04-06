"""Tests for corpus stores: examples, bayān, cognitive domains,
generation templates, and trace records.
"""

from __future__ import annotations

from creative_tokenizer.morphology.bayan_record import make_bayan
from creative_tokenizer.morphology.cognitive_domain import (
    CognitiveDomain,
    DiscourseTag,
    FormalTag,
    PhysicalTag,
    make_cognitive,
)
from creative_tokenizer.morphology.example_record import (
    ExampleSource,
    make_example,
    make_secondary_semantics,
)
from creative_tokenizer.morphology.generation_template import (
    GenerationPurpose,
    make_template,
)
from creative_tokenizer.morphology.trace_record import make_trace

# ---------------------------------------------------------------------------
# SecondarySemantics
# ---------------------------------------------------------------------------


class TestSecondarySemantics:
    def test_pack_id_positive(self) -> None:
        ss = make_secondary_semantics(condition_id=5)
        assert ss.pack_id > 0

    def test_all_zeros_deterministic(self) -> None:
        ss1 = make_secondary_semantics()
        ss2 = make_secondary_semantics()
        assert ss1.pack_id == ss2.pack_id

    def test_condition_id_stored(self) -> None:
        ss = make_secondary_semantics(condition_id=10)
        assert ss.condition_id == 10

    def test_mafhum_id_stored(self) -> None:
        ss = make_secondary_semantics(mafhum_id=7)
        assert ss.mafhum_id == 7

    def test_different_dimensions_differ(self) -> None:
        ss1 = make_secondary_semantics(condition_id=3)
        ss2 = make_secondary_semantics(mafhum_id=3)
        assert ss1.pack_id != ss2.pack_id

    def test_ghaya_and_ishara_stored(self) -> None:
        ss = make_secondary_semantics(ghaya_id=2, ishara_id=4)
        assert ss.ghaya_id == 2
        assert ss.ishara_id == 4


# ---------------------------------------------------------------------------
# ExampleRecord
# ---------------------------------------------------------------------------


class TestExampleRecord:
    def _ss(self) -> object:
        return make_secondary_semantics()

    def test_example_id_positive(self) -> None:
        ss = make_secondary_semantics()
        ex = make_example(
            domain_id=1,
            source_type=ExampleSource.CORPUS,
            unicode_trace_id=100,
            token_node_ids=[10, 20, 30],
            compositional_graph_id=5,
            mantuq_id=3,
            secondary_semantics=ss,
            style_hub_id=7,
            i3rab_trace_id=2,
        )
        assert ex.example_id > 0

    def test_raw_text_preserved(self) -> None:
        ss = make_secondary_semantics()
        ex = make_example(
            domain_id=1,
            source_type=ExampleSource.MANUAL,
            unicode_trace_id=100,
            token_node_ids=[],
            compositional_graph_id=1,
            mantuq_id=1,
            secondary_semantics=ss,
            style_hub_id=1,
            i3rab_trace_id=1,
            raw_text="إن جاء زيد فأكرمه",
        )
        assert ex.raw_text == "إن جاء زيد فأكرمه"

    def test_token_node_ids_as_tuple(self) -> None:
        ss = make_secondary_semantics()
        ex = make_example(
            domain_id=1,
            source_type=ExampleSource.CORPUS,
            unicode_trace_id=10,
            token_node_ids=[1, 2, 3],
            compositional_graph_id=4,
            mantuq_id=5,
            secondary_semantics=ss,
            style_hub_id=6,
            i3rab_trace_id=7,
        )
        assert ex.token_node_ids == (1, 2, 3)

    def test_different_unicode_trace_different_example_id(self) -> None:
        ss = make_secondary_semantics()
        kw = dict(
            domain_id=1,
            source_type=ExampleSource.CORPUS,
            token_node_ids=[],
            compositional_graph_id=5,
            mantuq_id=3,
            secondary_semantics=ss,
            style_hub_id=7,
            i3rab_trace_id=2,
        )
        ex1 = make_example(unicode_trace_id=10, **kw)
        ex2 = make_example(unicode_trace_id=20, **kw)
        assert ex1.example_id != ex2.example_id

    def test_different_style_hub_different_example_id(self) -> None:
        ss = make_secondary_semantics()
        kw = dict(
            domain_id=1,
            source_type=ExampleSource.CORPUS,
            unicode_trace_id=10,
            token_node_ids=[],
            compositional_graph_id=5,
            mantuq_id=3,
            secondary_semantics=ss,
            i3rab_trace_id=2,
        )
        ex1 = make_example(style_hub_id=1, **kw)
        ex2 = make_example(style_hub_id=2, **kw)
        assert ex1.example_id != ex2.example_id

    def test_same_inputs_same_example_id(self) -> None:
        ss = make_secondary_semantics(condition_id=3)
        kw = dict(
            domain_id=1,
            source_type=ExampleSource.GENERATED,
            unicode_trace_id=55,
            token_node_ids=[5, 6],
            compositional_graph_id=9,
            mantuq_id=2,
            secondary_semantics=ss,
            style_hub_id=4,
            i3rab_trace_id=1,
        )
        assert make_example(**kw).example_id == make_example(**kw).example_id

    def test_source_type_affects_example_id(self) -> None:
        ss = make_secondary_semantics()
        kw = dict(
            domain_id=1,
            unicode_trace_id=10,
            token_node_ids=[],
            compositional_graph_id=5,
            mantuq_id=3,
            secondary_semantics=ss,
            style_hub_id=7,
            i3rab_trace_id=2,
        )
        ex_corp = make_example(source_type=ExampleSource.CORPUS, **kw)
        ex_gen = make_example(source_type=ExampleSource.GENERATED, **kw)
        assert ex_corp.example_id != ex_gen.example_id


# ---------------------------------------------------------------------------
# BayanRecord
# ---------------------------------------------------------------------------


class TestBayanRecord:
    def test_literal_not_blocked_default(self) -> None:
        bayan = make_bayan(target_node_id=100, rule_path=[1, 2])
        assert bayan.literal_blocking_condition == 0

    def test_qarina_default_zero(self) -> None:
        bayan = make_bayan(target_node_id=100, rule_path=[])
        assert bayan.qarina_id == 0

    def test_semantic_rank_default_one(self) -> None:
        bayan = make_bayan(target_node_id=50, rule_path=[3])
        assert bayan.semantic_rank == 1

    def test_rule_path_stored(self) -> None:
        bayan = make_bayan(target_node_id=1, rule_path=[10, 20, 30])
        assert bayan.rule_path == (10, 20, 30)

    def test_empty_rule_path_gives_zero_reason_chain(self) -> None:
        bayan = make_bayan(target_node_id=1, rule_path=[])
        assert bayan.reason_chain_id == 0

    def test_non_empty_rule_path_positive_reason_chain(self) -> None:
        bayan = make_bayan(target_node_id=1, rule_path=[5])
        assert bayan.reason_chain_id > 0

    def test_different_rule_paths_differ(self) -> None:
        b1 = make_bayan(target_node_id=1, rule_path=[1, 2])
        b2 = make_bayan(target_node_id=1, rule_path=[1, 3])
        assert b1.reason_chain_id != b2.reason_chain_id

    def test_blocking_condition_stored(self) -> None:
        bayan = make_bayan(
            target_node_id=1,
            rule_path=[],
            literal_blocking_condition=5,
        )
        assert bayan.literal_blocking_condition == 5

    def test_qarina_stored(self) -> None:
        bayan = make_bayan(target_node_id=1, rule_path=[], qarina_id=9)
        assert bayan.qarina_id == 9

    def test_explanation_id_deterministic(self) -> None:
        b1 = make_bayan(target_node_id=42, rule_path=[1, 2], qarina_id=7)
        b2 = make_bayan(target_node_id=42, rule_path=[1, 2], qarina_id=7)
        assert b1.explanation_id == b2.explanation_id

    def test_traceback_ids_stored(self) -> None:
        bayan = make_bayan(target_node_id=1, rule_path=[], traceback_ids=[100, 200])
        assert bayan.traceback_ids == (100, 200)

    def test_no_traceback_empty_tuple(self) -> None:
        bayan = make_bayan(target_node_id=1, rule_path=[])
        assert bayan.traceback_ids == ()


# ---------------------------------------------------------------------------
# CognitiveDomain
# ---------------------------------------------------------------------------


class TestCognitiveDomain:
    def test_physical_motion(self) -> None:
        c = make_cognitive(CognitiveDomain.PHYSICAL, PhysicalTag.MOTION)
        assert c.domain == CognitiveDomain.PHYSICAL
        assert c.tag == int(PhysicalTag.MOTION)

    def test_formal_unity(self) -> None:
        c = make_cognitive(CognitiveDomain.FORMAL, FormalTag.UNITY)
        assert c.domain == CognitiveDomain.FORMAL

    def test_discourse_intent(self) -> None:
        c = make_cognitive(CognitiveDomain.DISCOURSE, DiscourseTag.INTENT)
        assert c.domain == CognitiveDomain.DISCOURSE

    def test_different_domains_different_concept_id(self) -> None:
        c_phys = make_cognitive(CognitiveDomain.PHYSICAL, 1)
        c_form = make_cognitive(CognitiveDomain.FORMAL, 1)
        assert c_phys.concept_id != c_form.concept_id

    def test_different_tags_different_concept_id(self) -> None:
        c1 = make_cognitive(CognitiveDomain.PHYSICAL, PhysicalTag.MOTION)
        c2 = make_cognitive(CognitiveDomain.PHYSICAL, PhysicalTag.HEAT)
        assert c1.concept_id != c2.concept_id

    def test_all_physical_tags_distinct(self) -> None:
        ids = {
            make_cognitive(CognitiveDomain.PHYSICAL, t).concept_id
            for t in PhysicalTag
        }
        assert len(ids) == len(PhysicalTag)

    def test_all_formal_tags_distinct(self) -> None:
        ids = {
            make_cognitive(CognitiveDomain.FORMAL, t).concept_id for t in FormalTag
        }
        assert len(ids) == len(FormalTag)

    def test_all_discourse_tags_distinct(self) -> None:
        ids = {
            make_cognitive(CognitiveDomain.DISCOURSE, t).concept_id
            for t in DiscourseTag
        }
        assert len(ids) == len(DiscourseTag)

    def test_deterministic(self) -> None:
        c1 = make_cognitive(CognitiveDomain.FORMAL, FormalTag.NECESSITY)
        c2 = make_cognitive(CognitiveDomain.FORMAL, FormalTag.NECESSITY)
        assert c1.concept_id == c2.concept_id

    def test_physical_light_kawn_linked(self) -> None:
        """Light (ضوء) maps to PHYSICAL domain — confirms cosmos connectivity."""
        c = make_cognitive(CognitiveDomain.PHYSICAL, PhysicalTag.LIGHT)
        assert c.domain == CognitiveDomain.PHYSICAL

    def test_formal_condition_links_to_shart(self) -> None:
        """Condition (شرط) maps to FORMAL domain — structural prerequisite."""
        c = make_cognitive(CognitiveDomain.FORMAL, FormalTag.CONDITION)
        assert c.tag == int(FormalTag.CONDITION)


# ---------------------------------------------------------------------------
# GenerationTemplate
# ---------------------------------------------------------------------------


class TestGenerationTemplate:
    def test_template_id_positive(self) -> None:
        t = make_template(
            root_id=1,
            pattern_id=2,
            family_id=3,
            concept_class_id=4,
            generation_purpose=GenerationPurpose.MORPHOLOGICAL,
        )
        assert t.template_id > 0

    def test_purpose_stored(self) -> None:
        t = make_template(
            root_id=1,
            pattern_id=2,
            family_id=3,
            concept_class_id=4,
            generation_purpose=GenerationPurpose.CONFLICT,
        )
        assert t.generation_purpose == GenerationPurpose.CONFLICT

    def test_different_root_different_template_id(self) -> None:
        kw = dict(
            pattern_id=2,
            family_id=3,
            concept_class_id=4,
            generation_purpose=GenerationPurpose.SYNTACTIC,
        )
        t1 = make_template(root_id=10, **kw)
        t2 = make_template(root_id=11, **kw)
        assert t1.template_id != t2.template_id

    def test_different_purpose_different_template_id(self) -> None:
        kw = dict(root_id=1, pattern_id=2, family_id=3, concept_class_id=4)
        t1 = make_template(generation_purpose=GenerationPurpose.MORPHOLOGICAL, **kw)
        t2 = make_template(generation_purpose=GenerationPurpose.STYLISTIC, **kw)
        assert t1.template_id != t2.template_id

    def test_same_inputs_same_template_id(self) -> None:
        kw = dict(
            root_id=5,
            pattern_id=6,
            family_id=7,
            concept_class_id=8,
            generation_purpose=GenerationPurpose.SEMANTIC,
        )
        assert make_template(**kw).template_id == make_template(**kw).template_id

    def test_value_constraints_sorted(self) -> None:
        t = make_template(
            root_id=1,
            pattern_id=1,
            family_id=1,
            concept_class_id=1,
            generation_purpose=GenerationPurpose.MORPHOLOGICAL,
            value_constraints=[9, 3, 7],
        )
        assert t.value_constraints == (3, 7, 9)

    def test_no_constraints_empty_tuple(self) -> None:
        t = make_template(
            root_id=1,
            pattern_id=1,
            family_id=1,
            concept_class_id=1,
            generation_purpose=GenerationPurpose.MORPHOLOGICAL,
        )
        assert t.value_constraints == ()

    def test_with_constraints_differs_from_without(self) -> None:
        kw = dict(
            root_id=1,
            pattern_id=1,
            family_id=1,
            concept_class_id=1,
            generation_purpose=GenerationPurpose.MORPHOLOGICAL,
        )
        t_free = make_template(**kw)
        t_constrained = make_template(**kw, value_constraints=[5])
        assert t_free.template_id != t_constrained.template_id


# ---------------------------------------------------------------------------
# TraceRecord
# ---------------------------------------------------------------------------


class TestTraceRecord:
    def test_trace_id_positive(self) -> None:
        tr = make_trace(
            input_trace_id=1,
            normalization_trace_id=2,
            lexical_trace_id=3,
            compositional_trace_id=4,
            semantic_trace_id=5,
            economy_trace_id=6,
            output_trace_id=7,
        )
        assert tr.trace_id > 0

    def test_all_fields_preserved(self) -> None:
        tr = make_trace(
            input_trace_id=10,
            normalization_trace_id=20,
            lexical_trace_id=30,
            compositional_trace_id=40,
            semantic_trace_id=50,
            economy_trace_id=60,
            output_trace_id=70,
        )
        assert tr.input_trace_id == 10
        assert tr.normalization_trace_id == 20
        assert tr.lexical_trace_id == 30
        assert tr.compositional_trace_id == 40
        assert tr.semantic_trace_id == 50
        assert tr.economy_trace_id == 60
        assert tr.output_trace_id == 70

    def test_deterministic(self) -> None:
        kw = dict(
            input_trace_id=1,
            normalization_trace_id=2,
            lexical_trace_id=3,
            compositional_trace_id=4,
            semantic_trace_id=5,
            economy_trace_id=6,
            output_trace_id=7,
        )
        assert make_trace(**kw).trace_id == make_trace(**kw).trace_id

    def test_input_change_changes_trace(self) -> None:
        base = dict(
            normalization_trace_id=2,
            lexical_trace_id=3,
            compositional_trace_id=4,
            semantic_trace_id=5,
            economy_trace_id=6,
            output_trace_id=7,
        )
        tr1 = make_trace(input_trace_id=1, **base)
        tr2 = make_trace(input_trace_id=99, **base)
        assert tr1.trace_id != tr2.trace_id

    def test_output_change_changes_trace(self) -> None:
        base = dict(
            input_trace_id=1,
            normalization_trace_id=2,
            lexical_trace_id=3,
            compositional_trace_id=4,
            semantic_trace_id=5,
            economy_trace_id=6,
        )
        tr1 = make_trace(output_trace_id=7, **base)
        tr2 = make_trace(output_trace_id=8, **base)
        assert tr1.trace_id != tr2.trace_id

    def test_semantic_change_changes_trace(self) -> None:
        base = dict(
            input_trace_id=1,
            normalization_trace_id=2,
            lexical_trace_id=3,
            compositional_trace_id=4,
            economy_trace_id=6,
            output_trace_id=7,
        )
        tr1 = make_trace(semantic_trace_id=5, **base)
        tr2 = make_trace(semantic_trace_id=50, **base)
        assert tr1.trace_id != tr2.trace_id

    def test_full_pipeline_recoverable(self) -> None:
        """All seven layer IDs recoverable from the trace record."""
        from creative_tokenizer.morphology.unicode_identity import unicode_surface

        uid = unicode_surface("الشمس")
        tr = make_trace(
            input_trace_id=uid,
            normalization_trace_id=uid,
            lexical_trace_id=10,
            compositional_trace_id=20,
            semantic_trace_id=30,
            economy_trace_id=40,
            output_trace_id=50,
        )
        assert tr.input_trace_id == uid  # raw unicode never lost
        assert tr.output_trace_id == 50


# ---------------------------------------------------------------------------
# Integration: ExampleRecord ↔ BayanRecord ↔ TraceRecord
# ---------------------------------------------------------------------------


class TestCorpusIntegration:
    def test_bayan_target_is_example_id(self) -> None:
        """BayanRecord.target_node_id = ExampleRecord.example_id."""
        ss = make_secondary_semantics(condition_id=3)
        ex = make_example(
            domain_id=1,
            source_type=ExampleSource.MANUAL,
            unicode_trace_id=100,
            token_node_ids=[1, 2],
            compositional_graph_id=5,
            mantuq_id=3,
            secondary_semantics=ss,
            style_hub_id=7,
            i3rab_trace_id=2,
            raw_text="جاء زيد",
        )
        bayan = make_bayan(
            target_node_id=ex.example_id,
            rule_path=[1],
        )
        assert bayan.target_node_id == ex.example_id

    def test_trace_links_unicode_to_output(self) -> None:
        """TraceRecord links raw unicode to final output via intermediate ids."""
        ss = make_secondary_semantics()
        ex = make_example(
            domain_id=1,
            source_type=ExampleSource.CORPUS,
            unicode_trace_id=200,
            token_node_ids=[],
            compositional_graph_id=10,
            mantuq_id=4,
            secondary_semantics=ss,
            style_hub_id=3,
            i3rab_trace_id=5,
        )
        tr = make_trace(
            input_trace_id=ex.unicode_trace_id,
            normalization_trace_id=ex.unicode_trace_id,
            lexical_trace_id=ex.mantuq_id,
            compositional_trace_id=ex.compositional_graph_id,
            semantic_trace_id=ex.secondary_semantics.pack_id,
            economy_trace_id=ex.economy_trace_id,
            output_trace_id=ex.example_id,
        )
        assert tr.input_trace_id == 200
        assert tr.output_trace_id == ex.example_id
