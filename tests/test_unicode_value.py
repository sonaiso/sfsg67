"""Tests for the composite interpretive Unicode value module.

Covers:
  - Feature extraction helpers  (script, category, layers, flags)
  - Bit-packed ``unicode_value`` and lossless ``unpack_unicode_value``
  - Fractal ``compose`` with relation tags
  - Arabic-specific behaviour  (letters, diacritics, punctuation)
  - Span / identity preservation
"""

from __future__ import annotations

import pytest

from creative_tokenizer.morphology.unicode_value import (
    DEFAULT_PRIME,
    RelationTag,
    arabic_layer_class,
    compose,
    general_category_code,
    morphological_potential,
    phonological_class,
    relational_potential,
    script_class,
    structural_flags,
    unicode_value,
    unpack_unicode_value,
)

# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

_FATHA = "\u064e"
_DAMMA = "\u064f"
_KASRA = "\u0650"
_SUKUN = "\u0652"
_SHADDA = "\u0651"
_TANWEEN_FATH = "\u064b"
_DAGGER_ALIF = "\u0670"
_TAA_MARBUTA = "\u0629"
_HAMZA = "\u0621"
_ALIF = "\u0627"
_WAW = "\u0648"
_YAA = "\u064a"
_KAF = "\u0643"
_BA = "\u0628"
_SHIN = "\u0634"


# ===================================================================
# 1. Feature extraction — script_class
# ===================================================================


class TestScriptClass:
    def test_arabic_letter(self) -> None:
        assert script_class(_KAF) == 1

    def test_arabic_diacritic(self) -> None:
        assert script_class(_FATHA) == 1

    def test_ascii_digit(self) -> None:
        assert script_class("5") == 2

    def test_whitespace(self) -> None:
        assert script_class(" ") == 3
        assert script_class("\t") == 3

    def test_latin_letter(self) -> None:
        assert script_class("A") == 0

    def test_other(self) -> None:
        assert script_class("!") == 0


# ===================================================================
# 2. Feature extraction — general_category_code
# ===================================================================


class TestGeneralCategoryCode:
    def test_arabic_letter_is_Lo(self) -> None:
        # Arabic letters have category Lo
        assert general_category_code(_KAF) == 3

    def test_arabic_diacritic_is_Mn(self) -> None:
        assert general_category_code(_FATHA) == 4

    def test_ascii_digit(self) -> None:
        assert general_category_code("5") == 6

    def test_space_is_Zs(self) -> None:
        assert general_category_code(" ") == 7

    def test_unknown_category_returns_zero(self) -> None:
        # Control characters have category Cc which is not in the table
        assert general_category_code("\x00") == 0


# ===================================================================
# 3. Feature extraction — arabic_layer_class
# ===================================================================


class TestArabicLayerClass:
    def test_letter(self) -> None:
        assert arabic_layer_class(_KAF) == 1

    def test_diacritic(self) -> None:
        assert arabic_layer_class(_FATHA) == 2

    def test_whitespace(self) -> None:
        assert arabic_layer_class(" ") == 5

    def test_punctuation(self) -> None:
        assert arabic_layer_class(".") == 6

    def test_digit(self) -> None:
        assert arabic_layer_class("5") == 7

    def test_other(self) -> None:
        assert arabic_layer_class("A") == 0


# ===================================================================
# 4. Feature extraction — phonological_class
# ===================================================================


class TestPhonologicalClass:
    def test_consonant(self) -> None:
        assert phonological_class(_KAF) == 1

    def test_vocalic_marker(self) -> None:
        assert phonological_class(_FATHA) == 2
        assert phonological_class(_DAMMA) == 2

    def test_non_arabic(self) -> None:
        assert phonological_class("A") == 0


# ===================================================================
# 5. Feature extraction — morphological_potential
# ===================================================================


class TestMorphologicalPotential:
    def test_letter_is_root_candidate(self) -> None:
        assert morphological_potential(_KAF) == 1

    def test_diacritic_is_pattern_slot(self) -> None:
        assert morphological_potential(_FATHA) == 2

    def test_other_is_zero(self) -> None:
        assert morphological_potential(" ") == 0


# ===================================================================
# 6. Feature extraction — relational_potential
# ===================================================================


class TestRelationalPotential:
    def test_diacritic_prior(self) -> None:
        assert relational_potential(_FATHA) == 1

    def test_letter_prior(self) -> None:
        assert relational_potential(_KAF) == 2

    def test_other(self) -> None:
        assert relational_potential(" ") == 0


# ===================================================================
# 7. Feature extraction — structural_flags
# ===================================================================


class TestStructuralFlags:
    def test_whitespace_flag(self) -> None:
        assert structural_flags(" ") & 1 == 1

    def test_diacritic_flag(self) -> None:
        assert structural_flags(_FATHA) & 2 == 2

    def test_long_vowel_alif(self) -> None:
        assert structural_flags(_ALIF) & 4 == 4

    def test_long_vowel_waw(self) -> None:
        assert structural_flags(_WAW) & 4 == 4

    def test_long_vowel_yaa(self) -> None:
        assert structural_flags(_YAA) & 4 == 4

    def test_taa_marbuta(self) -> None:
        assert structural_flags(_TAA_MARBUTA) & 8 == 8

    def test_hamza(self) -> None:
        assert structural_flags(_HAMZA) & 16 == 16

    def test_plain_letter_no_flags(self) -> None:
        assert structural_flags(_SHIN) == 0


# ===================================================================
# 8. unicode_value — basic contract
# ===================================================================


class TestUnicodeValue:
    def test_preserves_raw_codepoint(self) -> None:
        v = unicode_value(_KAF)
        assert v & ((1 << 21) - 1) == ord(_KAF)

    def test_different_chars_give_different_values(self) -> None:
        assert unicode_value(_KAF) != unicode_value(_BA)

    def test_letter_vs_diacritic_differ(self) -> None:
        assert unicode_value(_KAF) != unicode_value(_FATHA)

    def test_rejects_empty_string(self) -> None:
        with pytest.raises(ValueError):
            unicode_value("")

    def test_rejects_multi_char_string(self) -> None:
        with pytest.raises(ValueError):
            unicode_value("ab")

    def test_ascii_char(self) -> None:
        v = unicode_value("A")
        assert v & ((1 << 21) - 1) == ord("A")

    def test_value_encodes_more_than_codepoint(self) -> None:
        """The composite value must carry more information than ord()."""
        v = unicode_value(_KAF)
        assert v != ord(_KAF)


# ===================================================================
# 9. unpack roundtrip
# ===================================================================


class TestUnpackRoundtrip:
    def test_arabic_letter_roundtrip(self) -> None:
        v = unicode_value(_KAF)
        fields = unpack_unicode_value(v)
        assert fields.codepoint == ord(_KAF)
        assert fields.script == 1
        assert fields.arabic_layer == 1
        assert fields.phonological == 1
        assert fields.morphological == 1
        assert fields.relational == 2

    def test_arabic_diacritic_roundtrip(self) -> None:
        v = unicode_value(_FATHA)
        fields = unpack_unicode_value(v)
        assert fields.codepoint == ord(_FATHA)
        assert fields.script == 1
        assert fields.arabic_layer == 2
        assert fields.phonological == 2
        assert fields.morphological == 2
        assert fields.relational == 1
        assert fields.flags & 2 == 2

    def test_ascii_digit_roundtrip(self) -> None:
        v = unicode_value("5")
        fields = unpack_unicode_value(v)
        assert fields.codepoint == ord("5")
        assert fields.script == 2
        assert fields.general_category == 6

    def test_space_roundtrip(self) -> None:
        v = unicode_value(" ")
        fields = unpack_unicode_value(v)
        assert fields.codepoint == ord(" ")
        assert fields.script == 3
        assert fields.flags & 1 == 1

    def test_repack_equals_original(self) -> None:
        """Packing the unpacked fields must reproduce the original value."""
        for ch in [_KAF, _FATHA, " ", "A", "5", _HAMZA, _ALIF, _TAA_MARBUTA]:
            v = unicode_value(ch)
            f = unpack_unicode_value(v)
            repacked = (
                f.codepoint
                | (f.script << 21)
                | (f.general_category << 26)
                | (f.arabic_layer << 31)
                | (f.phonological << 37)
                | (f.morphological << 42)
                | (f.relational << 48)
                | (f.flags << 54)
            )
            assert repacked == v, f"Roundtrip failed for {ch!r}"


# ===================================================================
# 10. Determinism and distinctness
# ===================================================================


class TestDeterminismAndDistinctness:
    def test_deterministic(self) -> None:
        assert unicode_value(_KAF) == unicode_value(_KAF)
        assert unicode_value(_FATHA) == unicode_value(_FATHA)

    def test_distinct_arabic_letters(self) -> None:
        vals = {unicode_value(chr(cp)) for cp in range(0x0621, 0x064B)}
        assert len(vals) == 0x064B - 0x0621  # all unique

    def test_distinct_diacritics(self) -> None:
        marks = [_FATHA, _DAMMA, _KASRA, _SUKUN, _SHADDA, _TANWEEN_FATH, _DAGGER_ALIF]
        vals = {unicode_value(m) for m in marks}
        assert len(vals) == len(marks)


# ===================================================================
# 11. Fractal composition — compose
# ===================================================================


class TestCompose:
    def test_single_element(self) -> None:
        result = compose([42], [RelationTag.BASE])
        assert result == (42 + RelationTag.BASE)

    def test_two_elements(self) -> None:
        v0, v1 = 100, 200
        r0, r1 = RelationTag.BASE, RelationTag.DIACRITIC
        expected = (v0 + r0) + (v1 + r1) * DEFAULT_PRIME
        assert compose([v0, v1], [r0, r1]) == expected

    def test_order_sensitive(self) -> None:
        a = compose([10, 20], [RelationTag.BASE, RelationTag.DIACRITIC])
        b = compose([20, 10], [RelationTag.BASE, RelationTag.DIACRITIC])
        assert a != b

    def test_relation_tag_matters(self) -> None:
        a = compose([10, 20], [RelationTag.BASE, RelationTag.DIACRITIC])
        b = compose([10, 20], [RelationTag.DIACRITIC, RelationTag.BASE])
        assert a != b

    def test_mismatched_lengths_raises(self) -> None:
        with pytest.raises(ValueError):
            compose([1, 2], [RelationTag.BASE])

    def test_empty_input(self) -> None:
        assert compose([], []) == 0

    def test_custom_prime(self) -> None:
        result = compose([5], [1], prime=7)
        assert result == 6

    def test_grapheme_cluster_composition(self) -> None:
        """Compose a grapheme cluster (letter + diacritic)."""
        cluster_val = compose(
            [unicode_value(_KAF), unicode_value(_FATHA)],
            [RelationTag.BASE, RelationTag.DIACRITIC],
        )
        assert cluster_val > 0

    def test_different_clusters_are_distinct(self) -> None:
        c1 = compose(
            [unicode_value(_KAF), unicode_value(_FATHA)],
            [RelationTag.BASE, RelationTag.DIACRITIC],
        )
        c2 = compose(
            [unicode_value(_KAF), unicode_value(_KASRA)],
            [RelationTag.BASE, RelationTag.DIACRITIC],
        )
        assert c1 != c2


# ===================================================================
# 12. RelationTag enum
# ===================================================================


class TestRelationTag:
    def test_values(self) -> None:
        assert RelationTag.BASE == 1
        assert RelationTag.TEXT == 7

    def test_all_distinct(self) -> None:
        vals = [t.value for t in RelationTag]
        assert len(vals) == len(set(vals))


# ===================================================================
# 13. Arabic-specific regression: diacritics and punctuation
# ===================================================================


class TestArabicRegression:
    def test_all_named_diacritics_classified(self) -> None:
        """Every core Arabic diacritic must be classified as layer=2."""
        diacritic_cps = [
            0x064E,
            0x064F,
            0x0650,
            0x0652,
            0x0651,
            0x064B,
            0x064C,
            0x064D,
            0x0670,
        ]
        for cp in diacritic_cps:
            ch = chr(cp)
            fields = unpack_unicode_value(unicode_value(ch))
            assert fields.arabic_layer == 2, f"U+{cp:04X} not classified as diacritic"
            assert fields.phonological == 2
            assert fields.morphological == 2
            assert fields.relational == 1

    def test_arabic_punctuation(self) -> None:
        """Arabic comma (،) and semicolon (؛) should be classified as punctuation."""
        for ch in ["،", "؛"]:
            fields = unpack_unicode_value(unicode_value(ch))
            assert fields.arabic_layer == 6, f"{ch!r} not classified as punctuation"

    def test_word_span_values(self) -> None:
        """Tokenising كَتَبَ character-by-character must yield correct spans."""
        text = "كَتَبَ"
        vals = [unicode_value(ch) for ch in text]
        for i, (ch, v) in enumerate(zip(text, vals)):
            fields = unpack_unicode_value(v)
            assert fields.codepoint == ord(ch), f"Span mismatch at index {i}"
