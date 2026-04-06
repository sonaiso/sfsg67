"""Tests for LexicalNode — primary atom of the lexical store."""

from __future__ import annotations

from creative_tokenizer.morphology.lexical_node import LexicalNode, make_lexical_node


def _make(
    *,
    sign_id: int = 1,
    raw_unicode_id: int = 2,
    skeleton_id: int = 3,
    root_id: int = 4,
    pattern_id: int = 5,
    signified_id: int = 6,
    mutabaqa_id: int = 7,
    tadammun_id: int = 8,
    iltizam_id: int = 9,
    concept_class_id: int = 10,
    transfer_state_id: int = 0,
    metaphor_state_id: int = 0,
) -> LexicalNode:
    return make_lexical_node(
        sign_id=sign_id,
        raw_unicode_id=raw_unicode_id,
        skeleton_id=skeleton_id,
        root_id=root_id,
        pattern_id=pattern_id,
        signified_id=signified_id,
        mutabaqa_id=mutabaqa_id,
        tadammun_id=tadammun_id,
        iltizam_id=iltizam_id,
        concept_class_id=concept_class_id,
        transfer_state_id=transfer_state_id,
        metaphor_state_id=metaphor_state_id,
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestLexicalNodeBasic:
    def test_node_id_positive(self) -> None:
        assert _make().node_id > 0

    def test_lexeme_id_positive(self) -> None:
        assert _make().lexeme_id > 0

    def test_meaning_id_positive(self) -> None:
        assert _make().meaning_id > 0

    def test_default_transfer_state_zero(self) -> None:
        assert _make().transfer_state_id == 0

    def test_default_metaphor_state_zero(self) -> None:
        assert _make().metaphor_state_id == 0

    def test_transfer_state_stored(self) -> None:
        n = _make(transfer_state_id=3)
        assert n.transfer_state_id == 3

    def test_metaphor_state_stored(self) -> None:
        n = _make(metaphor_state_id=7)
        assert n.metaphor_state_id == 7

    def test_fields_preserved(self) -> None:
        n = _make(root_id=99, skeleton_id=88, pattern_id=77)
        assert n.root_id == 99
        assert n.skeleton_id == 88
        assert n.pattern_id == 77

    def test_meaning_fields_preserved(self) -> None:
        n = _make(mutabaqa_id=11, tadammun_id=22, iltizam_id=33)
        assert n.mutabaqa_id == 11
        assert n.tadammun_id == 22
        assert n.iltizam_id == 33

    def test_concept_class_preserved(self) -> None:
        n = _make(concept_class_id=5)
        assert n.concept_class_id == 5

    def test_raw_unicode_id_preserved(self) -> None:
        n = _make(raw_unicode_id=42)
        assert n.raw_unicode_id == 42


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestLexicalNodeDeterminism:
    def test_same_inputs_same_node_id(self) -> None:
        n1 = _make()
        n2 = _make()
        assert n1.node_id == n2.node_id

    def test_same_inputs_same_lexeme_id(self) -> None:
        n1 = _make(root_id=10, pattern_id=20)
        n2 = _make(root_id=10, pattern_id=20)
        assert n1.lexeme_id == n2.lexeme_id

    def test_same_inputs_same_meaning_id(self) -> None:
        n1 = _make(signified_id=100, mutabaqa_id=200)
        n2 = _make(signified_id=100, mutabaqa_id=200)
        assert n1.meaning_id == n2.meaning_id


# ---------------------------------------------------------------------------
# Sensitivity — each dimension independently changes the id
# ---------------------------------------------------------------------------


class TestLexicalNodeSensitivity:
    def test_different_root_different_lexeme_id(self) -> None:
        n1 = _make(root_id=10)
        n2 = _make(root_id=11)
        assert n1.lexeme_id != n2.lexeme_id

    def test_different_pattern_different_lexeme_id(self) -> None:
        n1 = _make(pattern_id=1)
        n2 = _make(pattern_id=2)
        assert n1.lexeme_id != n2.lexeme_id

    def test_different_unicode_different_lexeme_id(self) -> None:
        n1 = _make(raw_unicode_id=100)
        n2 = _make(raw_unicode_id=200)
        assert n1.lexeme_id != n2.lexeme_id

    def test_different_signified_different_meaning_id(self) -> None:
        n1 = _make(signified_id=50)
        n2 = _make(signified_id=51)
        assert n1.meaning_id != n2.meaning_id

    def test_different_mutabaqa_different_meaning_id(self) -> None:
        n1 = _make(mutabaqa_id=7)
        n2 = _make(mutabaqa_id=8)
        assert n1.meaning_id != n2.meaning_id

    def test_different_tadammun_different_meaning_id(self) -> None:
        n1 = _make(tadammun_id=3)
        n2 = _make(tadammun_id=4)
        assert n1.meaning_id != n2.meaning_id

    def test_different_iltizam_different_meaning_id(self) -> None:
        n1 = _make(iltizam_id=5)
        n2 = _make(iltizam_id=6)
        assert n1.meaning_id != n2.meaning_id

    def test_different_concept_class_different_node_id(self) -> None:
        n1 = _make(concept_class_id=1)
        n2 = _make(concept_class_id=2)
        assert n1.node_id != n2.node_id


# ---------------------------------------------------------------------------
# Arabic integration
# ---------------------------------------------------------------------------


class TestLexicalNodeArabic:
    def test_raw_unicode_from_unicode_surface(self) -> None:
        """unicode_surface('شمس') gives the raw_unicode_id; node stores it."""
        from creative_tokenizer.morphology.unicode_identity import unicode_surface

        text = "شمس"
        uid = unicode_surface(text)
        n = _make(raw_unicode_id=uid)
        assert n.raw_unicode_id == uid

    def test_jamid_no_metaphor(self) -> None:
        """A jamid noun (e.g. شمس) has metaphor_state_id=0 by default."""
        n = _make(metaphor_state_id=0)
        assert n.metaphor_state_id == 0

    def test_mushtaq_with_transfer_state(self) -> None:
        """A mushtaq word that has been transferred (e.g. كاتب urfi) records it."""
        n = _make(transfer_state_id=2)  # 2 = URFI
        assert n.transfer_state_id == 2

    def test_metaphor_state_is_annotation_not_id_component(self) -> None:
        """metaphor_state_id is a stored annotation tag; node_id depends on
        lexeme/meaning/concept layers only.  Two nodes that differ solely in
        metaphor_state_id may therefore share the same node_id.
        They are still distinguishable via metaphor_state_id directly.
        """
        n_literal = _make(metaphor_state_id=0)
        n_majazi = _make(metaphor_state_id=1)
        assert n_literal.metaphor_state_id != n_majazi.metaphor_state_id
