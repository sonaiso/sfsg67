"""Tests for epistemic principles."""

from creative_tokenizer.morphology.epistemic_principles import (
    EPISTEMIC_PRINCIPLES,
    PrincipleIndex,
    all_principles,
    epistemic_principle,
)
from creative_tokenizer.morphology.upper_ontology import NodeIndex


class TestPrinciples:
    def test_ten_principles(self):
        assert len(EPISTEMIC_PRINCIPLES) == 10

    def test_principle_ids_unique(self):
        ids = [p.principle_id for p in EPISTEMIC_PRINCIPLES]
        assert len(ids) == len(set(ids))

    def test_principle_lookup(self):
        p = epistemic_principle(PrincipleIndex.REALITY)
        assert p.label_en == "Principle of Reality"
        assert p.governs == (NodeIndex.REALITY,)

    def test_input_purity_governs_two_nodes(self):
        p = epistemic_principle(PrincipleIndex.INPUT_PURITY)
        assert p.governs == (NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING)

    def test_practical_guidance_governs_three_nodes(self):
        p = epistemic_principle(PrincipleIndex.PRACTICAL_GUIDANCE)
        assert p.governs == (NodeIndex.GUIDANCE, NodeIndex.ACTION, NodeIndex.OUTCOME)

    def test_convention_governs_signifier_through_signification(self):
        p = epistemic_principle(PrincipleIndex.CONVENTION)
        assert NodeIndex.SIGNIFIER in p.governs
        assert NodeIndex.COMPOSITION in p.governs
        assert NodeIndex.SIGNIFICATION in p.governs

    def test_all_principles_returns_same_tuple(self):
        assert all_principles() is EPISTEMIC_PRINCIPLES

    def test_principle_ids_stable(self):
        a = epistemic_principle(PrincipleIndex.BINDING)
        b = epistemic_principle(PrincipleIndex.BINDING)
        assert a.principle_id == b.principle_id

    def test_every_principle_has_governs(self):
        for p in EPISTEMIC_PRINCIPLES:
            assert len(p.governs) >= 1

    def test_every_principle_has_bilingual_labels(self):
        for p in EPISTEMIC_PRINCIPLES:
            assert p.label_ar
            assert p.label_en
            assert p.summary_ar
            assert p.summary_en
