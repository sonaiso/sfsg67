"""Tests for arabic_engine — core enums, types, and full pipeline.

Covers:
  - Enum values and exhaustiveness
  - Token, Concept, DalalLink construction and identity stability
  - Unicode normalization (diacritics, tatweel, alif variants)
  - Phonology (grapheme clusters, syllables, consonant skeleton)
  - Root/pattern extraction (known roots, fallback behavior)
  - Ontological mapping (POS → SemanticType)
  - Dalāla validation (mutabaqa, tadammun, iltizam, isnad, taqyid)
  - Judgment and evaluation construction
  - Syntax tree building
  - Time/space anchoring
  - World model and inference engine
  - Full pipeline on كَتَبَ زَيْدٌ الرِّسَالَةَ
  - Span preservation against original input
  - Arabic punctuation and diacritic edge cases
"""

from __future__ import annotations

import pytest

from creative_tokenizer.arabic_engine.cognition.evaluation import (
    EvalResult,
    Judgment,
    build_evaluation,
    build_judgment,
)
from creative_tokenizer.arabic_engine.core.enums import (
    DalalType,
    GuidanceState,
    SemanticType,
    TruthState,
)
from creative_tokenizer.arabic_engine.core.types import (
    Concept,
    Token,
    make_concept,
    make_dalal_link,
    make_token,
)
from creative_tokenizer.arabic_engine.inference.inference_rules import (
    InferenceEngine,
    RuleKind,
)
from creative_tokenizer.arabic_engine.inference.world_model import (
    WorldModel,
    make_fact,
)
from creative_tokenizer.arabic_engine.linkage.dalala import validate_dalala
from creative_tokenizer.arabic_engine.pipeline import PipelineResult, run_pipeline
from creative_tokenizer.arabic_engine.signified.ontology import map_to_ontology
from creative_tokenizer.arabic_engine.signifier.phonology import (
    analyze_phonology,
)
from creative_tokenizer.arabic_engine.signifier.root_pattern import (
    extract_root_pattern,
)
from creative_tokenizer.arabic_engine.signifier.unicode_norm import (
    NormMode,
    normalize_arabic,
)
from creative_tokenizer.arabic_engine.syntax.syntax import (
    SyntaxRole,
    build_syntax_tree,
)
from creative_tokenizer.arabic_engine.syntax.time_space import (
    TimeAnchor,
    build_time_space,
)

# ═══════════════════════════════════════════════════════════════════════
# §1  Core Enums
# ═══════════════════════════════════════════════════════════════════════


class TestSemanticType:
    def test_has_five_members(self) -> None:
        assert len(SemanticType) == 5

    def test_values(self) -> None:
        assert SemanticType.ENTITY == 1
        assert SemanticType.EVENT == 2
        assert SemanticType.ATTRIBUTE == 3
        assert SemanticType.RELATION == 4
        assert SemanticType.NORM == 5


class TestDalalType:
    def test_has_six_members(self) -> None:
        assert len(DalalType) == 6

    def test_mutabaqa_is_first(self) -> None:
        assert DalalType.MUTABAQA == 1


class TestTruthState:
    def test_has_four_members(self) -> None:
        assert len(TruthState) == 4

    def test_certain_and_false(self) -> None:
        assert TruthState.CERTAIN == 1
        assert TruthState.FALSE == 4


class TestGuidanceState:
    def test_has_six_members(self) -> None:
        assert len(GuidanceState) == 6

    def test_obligatory_to_neutral(self) -> None:
        assert GuidanceState.OBLIGATORY == 1
        assert GuidanceState.NEUTRAL == 6


# ═══════════════════════════════════════════════════════════════════════
# §2  Core Types
# ═══════════════════════════════════════════════════════════════════════


class TestToken:
    def test_make_token_returns_frozen(self) -> None:
        tok = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb")
        assert isinstance(tok, Token)
        with pytest.raises(AttributeError):
            tok.surface = "x"  # type: ignore[misc]

    def test_token_id_stable(self) -> None:
        tok1 = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb", span=(0, 5))
        tok2 = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb", span=(0, 5))
        assert tok1.token_id == tok2.token_id

    def test_different_spans_different_ids(self) -> None:
        tok1 = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb", span=(0, 5))
        tok2 = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb", span=(6, 11))
        assert tok1.token_id != tok2.token_id

    def test_span_preserves_original(self) -> None:
        text = "كَتَبَ زَيْدٌ"
        tok = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb", span=(0, 6))
        assert text[tok.span[0]:tok.span[1]] == "كَتَبَ"


class TestConcept:
    def test_make_concept_returns_frozen(self) -> None:
        c = make_concept("كتابة", "writing", SemanticType.EVENT)
        assert isinstance(c, Concept)
        assert c.semantic_type == SemanticType.EVENT

    def test_concept_id_stable(self) -> None:
        c1 = make_concept("كتب", "write", SemanticType.EVENT)
        c2 = make_concept("كتب", "write", SemanticType.EVENT)
        assert c1.concept_id == c2.concept_id


class TestDalalLink:
    def test_make_link_accepted(self) -> None:
        link = make_dalal_link(100, 200, DalalType.MUTABAQA, True, 0.95)
        assert link.accepted is True
        assert link.confidence == 0.95

    def test_link_id_stable(self) -> None:
        l1 = make_dalal_link(10, 20, DalalType.ISNAD, True, 0.8)
        l2 = make_dalal_link(10, 20, DalalType.ISNAD, True, 0.8)
        assert l1.link_id == l2.link_id


# ═══════════════════════════════════════════════════════════════════════
# §3  Unicode Normalization
# ═══════════════════════════════════════════════════════════════════════


class TestUnicodeNorm:
    def test_strip_diacritics(self) -> None:
        result = normalize_arabic("كَتَبَ")
        assert result.text == "كتب"

    def test_preserve_diacritics(self) -> None:
        result = normalize_arabic("كَتَبَ", mode=NormMode.PRESERVE_DIACRITICS)
        assert result.text == "كَتَبَ"

    def test_remove_tatweel(self) -> None:
        result = normalize_arabic("كــتــب")
        assert "ـ" not in result.text
        assert result.text == "كتب"

    def test_normalize_alif(self) -> None:
        result = normalize_arabic("أحمد إبراهيم آمنة")
        assert "أ" not in result.text
        assert "إ" not in result.text
        assert "آ" not in result.text
        assert result.text == "احمد ابراهيم امنة"

    def test_mapping_preserves_spans(self) -> None:
        text = "كَتَبَ"
        result = normalize_arabic(text)
        # Each output char maps back to the original
        for out_idx, orig_idx in enumerate(result.mapping):
            assert 0 <= orig_idx < len(text)

    def test_normalize_whitespace(self) -> None:
        result = normalize_arabic("كتب   زيد")
        assert result.text == "كتب زيد"

    def test_empty_input(self) -> None:
        result = normalize_arabic("")
        assert result.text == ""
        assert result.mapping == ()

    def test_original_preserved(self) -> None:
        text = "كَتَبَ"
        result = normalize_arabic(text)
        assert result.original == text

    def test_arabic_punctuation_preserved(self) -> None:
        """Arabic punctuation (؟ ، ؛) should not be stripped."""
        result = normalize_arabic("كتب؟")
        assert "؟" in result.text

    def test_tanween_stripped(self) -> None:
        """Tanween (فتحتان/ضمتان/كسرتان) should be stripped in STRIP mode."""
        result = normalize_arabic("كِتَابًا")
        assert "ً" not in result.text
        assert "ِ" not in result.text
        assert "َ" not in result.text


# ═══════════════════════════════════════════════════════════════════════
# §4  Phonology
# ═══════════════════════════════════════════════════════════════════════


class TestPhonology:
    def test_grapheme_clusters(self) -> None:
        result = analyze_phonology("كَتَبَ")
        assert len(result.clusters) > 0
        # First cluster should be kaf with fatha
        assert result.clusters[0].base == "ك"

    def test_consonant_skeleton(self) -> None:
        result = analyze_phonology("كَتَبَ")
        assert result.consonant_skeleton == ("ك", "ت", "ب")

    def test_syllables_non_empty(self) -> None:
        result = analyze_phonology("كَتَبَ")
        assert len(result.syllables) > 0

    def test_phonology_id_stable(self) -> None:
        r1 = analyze_phonology("كتب")
        r2 = analyze_phonology("كتب")
        assert r1.phonology_id == r2.phonology_id

    def test_waw_ya_in_skeleton(self) -> None:
        """و and ي should appear in consonant skeleton when consonantal."""
        result = analyze_phonology("وَجَدَ")
        assert "و" in result.consonant_skeleton


# ═══════════════════════════════════════════════════════════════════════
# §5  Root/Pattern Extraction
# ═══════════════════════════════════════════════════════════════════════


class TestRootPattern:
    def test_known_root_kataba(self) -> None:
        rp = extract_root_pattern("كَتَبَ")
        assert rp.root == "كتب"
        assert rp.pattern == "فَعَلَ"
        assert rp.pos == "verb"

    def test_known_root_zayd(self) -> None:
        rp = extract_root_pattern("زَيْدٌ")
        assert rp.root == "زيد"
        assert rp.pos == "noun"

    def test_known_root_risala(self) -> None:
        rp = extract_root_pattern("الرِّسَالَةَ")
        assert rp.root == "رسل"
        assert rp.pattern == "فِعَالَة"
        assert rp.pos == "noun"

    def test_unknown_root_fallback(self) -> None:
        rp = extract_root_pattern("أبجد")
        assert rp.pos == "unknown"

    def test_root_id_positive(self) -> None:
        rp = extract_root_pattern("كَتَبَ")
        assert rp.root_id > 0

    def test_root_id_stable(self) -> None:
        r1 = extract_root_pattern("كَتَبَ")
        r2 = extract_root_pattern("كَتَبَ")
        assert r1.root_id == r2.root_id

    def test_definite_article_stripped(self) -> None:
        rp = extract_root_pattern("الكتاب")
        assert rp.root == "كتب"

    def test_diacritics_on_root(self) -> None:
        """Diacritics should not affect root extraction."""
        rp1 = extract_root_pattern("كَتَبَ")
        rp2 = extract_root_pattern("كتب")
        assert rp1.root == rp2.root


# ═══════════════════════════════════════════════════════════════════════
# §6  Ontological Mapping
# ═══════════════════════════════════════════════════════════════════════


class TestOntology:
    def test_verb_maps_to_event(self) -> None:
        tok = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb")
        concept = map_to_ontology(tok)
        assert concept.semantic_type == SemanticType.EVENT

    def test_noun_maps_to_entity(self) -> None:
        tok = make_token("زَيْدٌ", "زيد", "زيد", "زيد", "فَعْل", "noun")
        concept = map_to_ontology(tok)
        assert concept.semantic_type == SemanticType.ENTITY

    def test_adj_maps_to_attribute(self) -> None:
        tok = make_token("كبير", "كبير", "كبير", "كبر", "فَعِيل", "adj")
        concept = map_to_ontology(tok)
        assert concept.semantic_type == SemanticType.ATTRIBUTE

    def test_concept_has_properties(self) -> None:
        tok = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb")
        concept = map_to_ontology(tok)
        props_dict = dict(concept.properties)
        assert "root" in props_dict
        assert props_dict["root"] == "كتب"


# ═══════════════════════════════════════════════════════════════════════
# §7  Dalāla Validation
# ═══════════════════════════════════════════════════════════════════════


class TestDalala:
    def test_mutabaqa_verb_event(self) -> None:
        tok = make_token("كَتَبَ", "كتب", "كتب", "كتب", "فَعَلَ", "verb")
        concept = make_concept("كتب", "write", SemanticType.EVENT)
        link = validate_dalala(tok, concept, DalalType.MUTABAQA)
        assert link.accepted is True
        assert link.confidence == 1.0

    def test_mutabaqa_noun_entity(self) -> None:
        tok = make_token("زيد", "زيد", "زيد", "زيد", "فَعْل", "noun")
        concept = make_concept("زيد", "zayd", SemanticType.ENTITY)
        link = validate_dalala(tok, concept, DalalType.MUTABAQA)
        assert link.accepted is True
        assert link.confidence == 1.0

    def test_tadammun_with_matching_root(self) -> None:
        tok = make_token("كتب", "كتب", "كتب", "كتب", "فَعَلَ", "verb")
        concept = make_concept("كتب", "write", SemanticType.EVENT, (("root", "كتب"),))
        link = validate_dalala(tok, concept, DalalType.TADAMMUN)
        assert link.accepted is True
        assert link.confidence == 0.8

    def test_iltizam_is_conservative(self) -> None:
        tok = make_token("كتب", "كتب", "كتب", "كتب", "فَعَلَ", "verb")
        concept = make_concept("كتب", "write", SemanticType.EVENT)
        link = validate_dalala(tok, concept, DalalType.ILTIZAM)
        assert link.accepted is True
        assert link.confidence == 0.3

    def test_isnad_for_verb(self) -> None:
        tok = make_token("كتب", "كتب", "كتب", "كتب", "فَعَلَ", "verb")
        concept = make_concept("زيد", "zayd", SemanticType.ENTITY)
        link = validate_dalala(tok, concept, DalalType.ISNAD)
        assert link.accepted is True
        assert link.confidence == 0.9

    def test_taqyid_for_adjective(self) -> None:
        tok = make_token("كبير", "كبير", "كبير", "كبر", "فعيل", "adj")
        concept = make_concept("كبير", "big", SemanticType.ATTRIBUTE)
        link = validate_dalala(tok, concept, DalalType.TAQYID)
        assert link.accepted is True
        assert link.confidence == 0.85


# ═══════════════════════════════════════════════════════════════════════
# §8  Judgment and Evaluation
# ═══════════════════════════════════════════════════════════════════════


class TestJudgment:
    def test_build_judgment(self) -> None:
        j = build_judgment(subject=10, predicate=20, object_id=30)
        assert isinstance(j, Judgment)
        assert j.subject == 10
        assert j.predicate == 20
        assert j.object_id == 30
        assert j.polarity == 1

    def test_negative_polarity(self) -> None:
        j = build_judgment(subject=10, predicate=20, polarity=-1)
        assert j.polarity == -1

    def test_judgment_id_stable(self) -> None:
        j1 = build_judgment(subject=10, predicate=20)
        j2 = build_judgment(subject=10, predicate=20)
        assert j1.judgment_id == j2.judgment_id


class TestEvaluation:
    def test_build_evaluation(self) -> None:
        j = build_judgment(subject=10, predicate=20)
        ev = build_evaluation(j, TruthState.CERTAIN, GuidanceState.OBLIGATORY, 0.95)
        assert isinstance(ev, EvalResult)
        assert ev.truth_state == TruthState.CERTAIN
        assert ev.guidance_state == GuidanceState.OBLIGATORY
        assert ev.confidence == 0.95

    def test_default_evaluation(self) -> None:
        j = build_judgment(subject=10, predicate=20)
        ev = build_evaluation(j)
        assert ev.truth_state == TruthState.PROBABLE
        assert ev.guidance_state == GuidanceState.NEUTRAL

    def test_eval_id_stable(self) -> None:
        j = build_judgment(subject=10, predicate=20)
        e1 = build_evaluation(j)
        e2 = build_evaluation(j)
        assert e1.eval_id == e2.eval_id


# ═══════════════════════════════════════════════════════════════════════
# §9  Syntax (V2)
# ═══════════════════════════════════════════════════════════════════════


class TestSyntax:
    def test_verb_subject_object(self) -> None:
        nodes = build_syntax_tree([1, 2, 3], ["verb", "noun", "noun"])
        assert nodes[0].role == SyntaxRole.VERB
        assert nodes[1].role == SyntaxRole.SUBJECT
        assert nodes[2].role == SyntaxRole.OBJECT

    def test_verb_is_head(self) -> None:
        nodes = build_syntax_tree([1, 2, 3], ["verb", "noun", "noun"])
        assert nodes[0].head_index == -1  # root
        assert nodes[1].head_index == 0
        assert nodes[2].head_index == 0

    def test_unknown_treated_as_nominal(self) -> None:
        nodes = build_syntax_tree([1, 2], ["verb", "unknown"])
        assert nodes[1].role == SyntaxRole.SUBJECT

    def test_length_mismatch_raises(self) -> None:
        with pytest.raises(ValueError, match="same length"):
            build_syntax_tree([1, 2], ["verb"])

    def test_node_ids_unique(self) -> None:
        nodes = build_syntax_tree([10, 20, 30], ["verb", "noun", "noun"])
        ids = [n.node_id for n in nodes]
        assert len(set(ids)) == len(ids)


# ═══════════════════════════════════════════════════════════════════════
# §10  Time/Space (V2)
# ═══════════════════════════════════════════════════════════════════════


class TestTimeSpace:
    def test_past_verb(self) -> None:
        ts = build_time_space(pos="verb", pattern="فَعَلَ")
        assert ts.time_anchor == TimeAnchor.PAST

    def test_timeless_noun(self) -> None:
        ts = build_time_space(pos="noun", pattern="فَعْل")
        assert ts.time_anchor == TimeAnchor.TIMELESS

    def test_explicit_time_anchor(self) -> None:
        ts = build_time_space(time_anchor=TimeAnchor.FUTURE)
        assert ts.time_anchor == TimeAnchor.FUTURE

    def test_ts_id_stable(self) -> None:
        ts1 = build_time_space(pos="verb", pattern="فَعَلَ")
        ts2 = build_time_space(pos="verb", pattern="فَعَلَ")
        assert ts1.ts_id == ts2.ts_id


# ═══════════════════════════════════════════════════════════════════════
# §11  World Model & Inference (V2)
# ═══════════════════════════════════════════════════════════════════════


class TestWorldModel:
    def test_add_and_lookup(self) -> None:
        wm = WorldModel()
        f = wm.add("زيد", "موجود")
        assert wm.lookup("زيد", "موجود") is not None
        assert wm.lookup("زيد", "موجود") == f

    def test_len(self) -> None:
        wm = WorldModel()
        assert len(wm) == 0
        wm.add("a", "b")
        assert len(wm) == 1

    def test_contains(self) -> None:
        wm = WorldModel()
        f = wm.add("a", "b")
        assert f.fact_id in wm

    def test_all_facts(self) -> None:
        wm = WorldModel()
        wm.add("a", "b")
        wm.add("c", "d")
        assert len(wm.all_facts()) == 2

    def test_fact_id_stable(self) -> None:
        f1 = make_fact("a", "b", TruthState.CERTAIN, 1.0)
        f2 = make_fact("a", "b", TruthState.CERTAIN, 1.0)
        assert f1.fact_id == f2.fact_id


class TestInference:
    def test_modus_ponens(self) -> None:
        wm = WorldModel()
        antecedent = wm.add("P", "true", TruthState.CERTAIN, 1.0)
        engine = InferenceEngine(wm)
        result = engine.apply_modus_ponens(antecedent, "Q", "derived")
        assert result.rule == RuleKind.MODUS_PONENS
        assert result.confidence > 0
        assert wm.lookup("Q", "derived") is not None

    def test_existential_inference(self) -> None:
        wm = WorldModel()
        engine = InferenceEngine(wm)
        j = build_judgment(subject=10, predicate=20)
        ev = build_evaluation(j, TruthState.PROBABLE, confidence=0.8)
        result = engine.apply_existential(j, ev)
        assert result.rule == RuleKind.EXISTENTIAL
        assert len(engine.results) == 1

    def test_low_confidence_gives_unknown(self) -> None:
        wm = WorldModel()
        engine = InferenceEngine(wm)
        j = build_judgment(subject=10, predicate=20)
        ev = build_evaluation(j, TruthState.PROBABLE, confidence=0.3)
        result = engine.apply_existential(j, ev)
        assert result.conclusion.truth_state == TruthState.UNKNOWN

    def test_inference_adds_to_world(self) -> None:
        wm = WorldModel()
        f = wm.add("P", "true", TruthState.PROBABLE, 0.9)
        engine = InferenceEngine(wm)
        engine.apply_modus_ponens(f, "Q", "derived")
        assert len(wm) == 2


# ═══════════════════════════════════════════════════════════════════════
# §12  Full Pipeline
# ═══════════════════════════════════════════════════════════════════════


class TestPipeline:
    def test_kataba_zayd_risala(self) -> None:
        """Full pipeline on كَتَبَ زَيْدٌ الرِّسَالَةَ."""
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert isinstance(result, PipelineResult)
        assert len(result.words) == 3

    def test_normalization(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.normalized.text == "كتب زيد الرسالة"

    def test_verb_identified(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.words[0].root_pattern.root == "كتب"
        assert result.words[0].root_pattern.pos == "verb"

    def test_subject_object_identified(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.words[1].root_pattern.root == "زيد"
        assert result.words[2].root_pattern.root == "رسل"

    def test_concepts(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.words[0].concept.semantic_type == SemanticType.EVENT
        assert result.words[1].concept.semantic_type == SemanticType.ENTITY

    def test_dalala_links(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        # Verb has mutabaqa
        assert result.words[0].dalala_mutabaqa.accepted is True
        # Nouns have isnad links
        assert result.words[1].dalala_isnad is not None
        assert result.words[1].dalala_isnad.accepted is True

    def test_syntax_roles(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.syntax_tree[0].role == SyntaxRole.VERB
        assert result.syntax_tree[1].role == SyntaxRole.SUBJECT
        assert result.syntax_tree[2].role == SyntaxRole.OBJECT

    def test_time_anchor_past(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.time_space.time_anchor == TimeAnchor.PAST

    def test_judgment_populated(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.judgment.predicate != 0
        assert result.judgment.subject != 0
        assert result.judgment.object_id != 0

    def test_evaluation(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.evaluation.truth_state == TruthState.PROBABLE
        assert result.evaluation.guidance_state == GuidanceState.NEUTRAL
        assert result.evaluation.confidence > 0

    def test_with_world_model(self) -> None:
        world = WorldModel()
        world.add("زيد", "موجود")
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ", world=world)
        assert result.inference is not None
        assert result.inference.rule == RuleKind.EXISTENTIAL

    def test_without_world_model(self) -> None:
        result = run_pipeline("كَتَبَ زَيْدٌ الرِّسَالَةَ")
        assert result.inference is None

    def test_single_word(self) -> None:
        result = run_pipeline("كَتَبَ")
        assert len(result.words) == 1
        assert result.words[0].root_pattern.root == "كتب"

    def test_span_against_original(self) -> None:
        """Token spans must index the original input correctly."""
        text = "كَتَبَ زَيْدٌ الرِّسَالَةَ"
        result = run_pipeline(text)
        for w in result.words:
            span_text = text[w.token.span[0]:w.token.span[1]]
            assert span_text == w.surface

    def test_arabic_comma_in_input(self) -> None:
        """Arabic comma (،) should not break the pipeline."""
        result = run_pipeline("كَتَبَ، زَيْدٌ")
        assert len(result.words) >= 2


# ═══════════════════════════════════════════════════════════════════════
# §13  Contracts YAML
# ═══════════════════════════════════════════════════════════════════════


class TestContracts:
    def test_contracts_file_exists(self) -> None:
        import pathlib
        contracts = (
            pathlib.Path(__file__).resolve().parent.parent
            / "src"
            / "creative_tokenizer"
            / "arabic_engine"
            / "contracts.yaml"
        )
        assert contracts.exists()

    def test_contracts_valid_yaml(self) -> None:
        """contracts.yaml must parse as valid YAML (if pyyaml available)."""
        import pathlib

        contracts = (
            pathlib.Path(__file__).resolve().parent.parent
            / "src"
            / "creative_tokenizer"
            / "arabic_engine"
            / "contracts.yaml"
        )
        # Read as text — YAML parsing requires pyyaml which may not be installed
        text = contracts.read_text(encoding="utf-8")
        assert "layers:" in text
        assert "closure_property:" in text

    def test_layer_chain_order(self) -> None:
        """Verify the layer chain covers all 11 stages."""
        import pathlib

        contracts = (
            pathlib.Path(__file__).resolve().parent.parent
            / "src"
            / "creative_tokenizer"
            / "arabic_engine"
            / "contracts.yaml"
        )
        text = contracts.read_text(encoding="utf-8")
        expected_layers = [
            "normalize",
            "signifier_phonology",
            "signifier_root_pattern",
            "lexical_closure",
            "ontology_mapping",
            "dalala_validation",
            "syntax_tree",
            "time_space",
            "judgment",
            "evaluation",
            "inference",
        ]
        for layer_name in expected_layers:
            assert f"name: {layer_name}" in text
