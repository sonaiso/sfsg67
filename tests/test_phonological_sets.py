"""Tests for phonological_sets.py — consonant, vowel, and diacritic classification."""

from creative_tokenizer.morphology.phonological_sets import (
    ALL_VOWELS,
    VOWEL_LONG,
    VOWEL_NULL,
    VOWEL_SHORT,
    VOWEL_TANWEEN,
    ConsonantRole,
    DiacriticKind,
    DiacriticRole,
    PlaceOfArticulation,
    VowelKind,
    VowelRole,
    consonant_role,
    consonant_set_id,
    diacritic_kind,
    diacritic_roles,
    phonological_layer_id,
    place_of_articulation,
    vowel_kind,
    vowel_roles,
    vowel_set_id,
)

# ---------------------------------------------------------------------------
# §2.1 Consonant tests
# ---------------------------------------------------------------------------


def test_ba_is_root_consonant() -> None:
    """ب (U+0628) is a root consonant."""
    assert ConsonantRole.ROOT in consonant_role(0x0628)


def test_ta_is_augment() -> None:
    """ت (U+062A) is an augmentation letter (سألتمونيها)."""
    assert ConsonantRole.AUGMENT in consonant_role(0x062A)


def test_waw_has_dual_role() -> None:
    """و (U+0648) can be both augmentation and functional."""
    roles = consonant_role(0x0648)
    assert ConsonantRole.AUGMENT in roles
    assert ConsonantRole.FUNC in roles


def test_ba_is_labial() -> None:
    assert place_of_articulation(0x0628) == PlaceOfArticulation.LABIAL


def test_ta_is_alveolar() -> None:
    assert place_of_articulation(0x062A) == PlaceOfArticulation.ALVEOLAR


def test_shin_is_palatal() -> None:
    assert place_of_articulation(0x0634) == PlaceOfArticulation.PALATAL


def test_qaf_is_uvular() -> None:
    assert place_of_articulation(0x0642) == PlaceOfArticulation.UVULAR


def test_ha_is_pharyngeal() -> None:
    """ح (U+062D) is pharyngeal."""
    assert place_of_articulation(0x062D) == PlaceOfArticulation.PHARYNGEAL


def test_hamza_is_glottal() -> None:
    """ء (U+0621) is glottal."""
    assert place_of_articulation(0x0621) == PlaceOfArticulation.GLOTTAL


def test_non_arabic_no_place() -> None:
    assert place_of_articulation(ord("a")) is None


def test_consonant_set_id_deterministic() -> None:
    s = frozenset({0x0628, 0x062A})
    assert consonant_set_id(s) == consonant_set_id(s)


def test_consonant_set_id_distinct() -> None:
    s1 = frozenset({0x0628})
    s2 = frozenset({0x062A})
    assert consonant_set_id(s1) != consonant_set_id(s2)


def test_consonant_set_id_empty() -> None:
    assert consonant_set_id(frozenset()) == 0


# ---------------------------------------------------------------------------
# §2.2 Vowel tests
# ---------------------------------------------------------------------------


def test_fatha_is_short() -> None:
    assert vowel_kind(0x064E) == VowelKind.SHORT


def test_alif_is_long_vowel() -> None:
    assert vowel_kind(0x0627) == VowelKind.LONG


def test_sukun_is_null() -> None:
    assert vowel_kind(0x0652) == VowelKind.NULL


def test_tanween_fath_is_tanween() -> None:
    assert vowel_kind(0x064B) == VowelKind.TANWEEN


def test_non_vowel_returns_none() -> None:
    assert vowel_kind(0x0628) is None  # ب is a consonant


def test_fatha_has_phonetic_and_derivational_roles() -> None:
    roles = vowel_roles(0x064E)
    assert VowelRole.PHONETIC in roles
    assert VowelRole.DERIVATIONAL in roles
    assert VowelRole.INFLECTIONAL in roles


def test_tanween_has_indefinite_role() -> None:
    roles = vowel_roles(0x064B)
    assert VowelRole.INDEFINITE in roles
    assert VowelRole.INFLECTIONAL in roles


def test_long_vowel_is_derivational() -> None:
    roles = vowel_roles(0x0627)  # alif
    assert VowelRole.DERIVATIONAL in roles
    assert VowelRole.PHONETIC in roles


def test_consonant_has_no_vowel_roles() -> None:
    assert vowel_roles(0x0628) == frozenset()


def test_all_vowels_is_union() -> None:
    assert ALL_VOWELS == VOWEL_SHORT | VOWEL_LONG | VOWEL_NULL | VOWEL_TANWEEN


def test_vowel_set_id_deterministic() -> None:
    assert vowel_set_id(VOWEL_SHORT) == vowel_set_id(VOWEL_SHORT)


# ---------------------------------------------------------------------------
# §2.3 Diacritic tests
# ---------------------------------------------------------------------------


def test_shadda_kind() -> None:
    assert diacritic_kind(0x0651) == DiacriticKind.SHADDA


def test_hamza_kind() -> None:
    assert diacritic_kind(0x0621) == DiacriticKind.HAMZA


def test_madda_kind() -> None:
    assert diacritic_kind(0x0653) == DiacriticKind.MADDA


def test_shadda_roles() -> None:
    roles = diacritic_roles(0x0651)
    assert DiacriticRole.PHONOLOGICAL in roles
    assert DiacriticRole.MORPHOLOGICAL in roles


def test_hamza_roles() -> None:
    roles = diacritic_roles(0x0621)
    assert DiacriticRole.PHONOLOGICAL in roles
    assert DiacriticRole.ORTHOGRAPHIC in roles


def test_non_diacritic_returns_none() -> None:
    assert diacritic_kind(0x0628) is None


def test_non_diacritic_empty_roles() -> None:
    assert diacritic_roles(0x0628) == frozenset()


# ---------------------------------------------------------------------------
# Phonological layer identity
# ---------------------------------------------------------------------------


def test_phonological_layer_id_consonant() -> None:
    """ب should produce a non-zero phonological layer ID."""
    assert phonological_layer_id("ب") > 0


def test_phonological_layer_id_vowel() -> None:
    """Fatha should produce a non-zero ID (via vowel kind)."""
    assert phonological_layer_id("\u064e") > 0


def test_phonological_layer_id_non_arabic_is_zero() -> None:
    """Latin 'a' is outside the Arabic phonological system."""
    assert phonological_layer_id("a") == 0


def test_phonological_layer_id_deterministic() -> None:
    assert phonological_layer_id("ك") == phonological_layer_id("ك")


def test_phonological_layer_id_distinct() -> None:
    """Different Arabic letters produce distinct IDs."""
    assert phonological_layer_id("ك") != phonological_layer_id("ب")
