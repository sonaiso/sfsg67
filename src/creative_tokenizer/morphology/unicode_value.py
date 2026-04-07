"""Composite interpretive value for each Unicode code point.

Every character receives a single integer ``V₀(u)`` that bit-packs:

*  c₀ – raw Unicode code point  (21 bits, positions 0–20)
*  c₁ – script class             (5 bits, positions 21–25)
*  c₂ – general category code    (5 bits, positions 26–30)
*  c₃ – Arabic / linguistic layer (6 bits, positions 31–36)
*  c₄ – phonological class        (5 bits, positions 37–41)
*  c₅ – morphological potential    (6 bits, positions 42–47)
*  c₆ – relational potential       (6 bits, positions 48–53)
*  c₇ – structural flags          (10 bits, positions 54–63)

The value is fully reversible via :func:`unpack_unicode_value`.

Higher-level fractal composition is provided by :func:`compose`, which
combines a sequence of ``(value, relation_tag)`` pairs into a single
integer using a weighted prime-power scheme.  Relation-tag constants
encode the structural role of an element inside its parent level.
"""

from __future__ import annotations

import enum
import unicodedata
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Arabic code-point sets  (reused from normalization / grapheme_atoms)
# ---------------------------------------------------------------------------

_ARABIC_DIACRITICS: dict[int, str] = {
    0x064E: "FATHA",
    0x064F: "DAMMA",
    0x0650: "KASRA",
    0x0652: "SUKUN",
    0x0651: "SHADDA",
    0x064B: "TANWEEN_FATH",
    0x064C: "TANWEEN_DAMM",
    0x064D: "TANWEEN_KASR",
    0x0670: "DAGGER_ALIF",
}

_ARABIC_LETTERS: frozenset[int] = frozenset(range(0x0621, 0x064B)) | frozenset(
    {0x0671, 0x067E, 0x0686, 0x06A4, 0x06AF}
)

# ---------------------------------------------------------------------------
# Bit-field widths & shifts
# ---------------------------------------------------------------------------

_SHIFT_SCRIPT = 21
_SHIFT_GENCAT = 26
_SHIFT_ARABIC = 31
_SHIFT_PHONO = 37
_SHIFT_MORPH = 42
_SHIFT_RELAT = 48
_SHIFT_FLAGS = 54

_MASK_21 = (1 << 21) - 1
_MASK_5 = (1 << 5) - 1
_MASK_6 = (1 << 6) - 1
_MASK_10 = (1 << 10) - 1

# ---------------------------------------------------------------------------
# Feature extraction helpers
# ---------------------------------------------------------------------------


def script_class(ch: str) -> int:
    """Return a small integer identifying the writing-system family.

    0 = other, 1 = Arabic block, 2 = ASCII digit, 3 = whitespace.
    """
    cp = ord(ch)
    if 0x0600 <= cp <= 0x06FF:
        return 1
    if 0x0030 <= cp <= 0x0039:  # '0'..'9'
        return 2
    if ch.isspace():
        return 3
    return 0


def general_category_code(ch: str) -> int:
    """Map Unicode General Category to a compact integer (0–13)."""
    cat = unicodedata.category(ch)
    _TABLE: dict[str, int] = {
        "Lu": 1,
        "Ll": 2,
        "Lo": 3,
        "Mn": 4,
        "Mc": 5,
        "Nd": 6,
        "Zs": 7,
        "Po": 8,
        "Pd": 9,
        "Ps": 10,
        "Pe": 11,
        "Sm": 12,
        "So": 13,
    }
    return _TABLE.get(cat, 0)


def arabic_layer_class(ch: str) -> int:
    """Classify a character within the Arabic linguistic layer.

    0 = other, 1 = Arabic letter, 2 = diacritic, 5 = whitespace,
    6 = punctuation, 7 = digit.
    """
    cp = ord(ch)
    if cp in _ARABIC_DIACRITICS:
        return 2
    if cp in _ARABIC_LETTERS:
        return 1
    if ch.isspace():
        return 5
    if unicodedata.category(ch).startswith("P"):
        return 6
    if unicodedata.category(ch) == "Nd":
        return 7
    return 0


def phonological_class(ch: str) -> int:
    """Return the phonological prior of a single character.

    0 = none, 1 = consonantal base, 2 = vocalic marker.
    """
    cp = ord(ch)
    if cp in _ARABIC_DIACRITICS:
        return 2
    if cp in _ARABIC_LETTERS:
        return 1
    return 0


def morphological_potential(ch: str) -> int:
    """Return the morphological prior of a single character.

    0 = none, 1 = root / lexical carrier candidate, 2 = pattern / vocalic slot.
    """
    cp = ord(ch)
    if cp in _ARABIC_LETTERS:
        return 1
    if cp in _ARABIC_DIACRITICS:
        return 2
    return 0


def relational_potential(ch: str) -> int:
    """Return the relational prior of a single character.

    0 = none, 1 = case / tense / phonological prior (diacritic),
    2 = nominal / verbal carrier prior (letter).
    """
    cp = ord(ch)
    if cp in _ARABIC_DIACRITICS:
        return 1
    if cp in _ARABIC_LETTERS:
        return 2
    return 0


def structural_flags(ch: str) -> int:
    """Return a bit-mask of structural flags for the character.

    Bit 0 – whitespace
    Bit 1 – Arabic diacritic
    Bit 2 – long-vowel letter (ا و ي)
    Bit 3 – tā marbūṭa (ة)
    Bit 4 – hamza (ء)
    """
    cp = ord(ch)
    f = 0
    if ch.isspace():
        f |= 1
    if cp in _ARABIC_DIACRITICS:
        f |= 2
    if cp in {0x0627, 0x0648, 0x064A}:  # ا و ي
        f |= 4
    if cp == 0x0629:  # ة
        f |= 8
    if cp == 0x0621:  # ء
        f |= 16
    return f


# ---------------------------------------------------------------------------
# Composite single-integer value
# ---------------------------------------------------------------------------


def unicode_value(ch: str) -> int:
    """Return the primary interpretive value ``V₀(u)`` for a single character.

    The result is a bit-packed integer that preserves the raw code point
    identity **and** encodes script, category, Arabic layer, phonological,
    morphological, relational, and structural information.  It can be
    unpacked losslessly with :func:`unpack_unicode_value`.

    Raises ``ValueError`` if *ch* is not exactly one character.
    """
    if len(ch) != 1:
        raise ValueError(f"unicode_value() requires a single character, got {ch!r}")

    c0 = ord(ch)
    c1 = script_class(ch)
    c2 = general_category_code(ch)
    c3 = arabic_layer_class(ch)
    c4 = phonological_class(ch)
    c5 = morphological_potential(ch)
    c6 = relational_potential(ch)
    c7 = structural_flags(ch)

    return (
        c0
        | (c1 << _SHIFT_SCRIPT)
        | (c2 << _SHIFT_GENCAT)
        | (c3 << _SHIFT_ARABIC)
        | (c4 << _SHIFT_PHONO)
        | (c5 << _SHIFT_MORPH)
        | (c6 << _SHIFT_RELAT)
        | (c7 << _SHIFT_FLAGS)
    )


# ---------------------------------------------------------------------------
# Unpacking
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class UnicodeValueFields:
    """Decoded fields of a ``V₀`` value."""

    codepoint: int
    script: int
    general_category: int
    arabic_layer: int
    phonological: int
    morphological: int
    relational: int
    flags: int


def unpack_unicode_value(v: int) -> UnicodeValueFields:
    """Losslessly unpack a ``V₀`` integer into its component fields."""
    return UnicodeValueFields(
        codepoint=v & _MASK_21,
        script=(v >> _SHIFT_SCRIPT) & _MASK_5,
        general_category=(v >> _SHIFT_GENCAT) & _MASK_5,
        arabic_layer=(v >> _SHIFT_ARABIC) & _MASK_6,
        phonological=(v >> _SHIFT_PHONO) & _MASK_5,
        morphological=(v >> _SHIFT_MORPH) & _MASK_6,
        relational=(v >> _SHIFT_RELAT) & _MASK_6,
        flags=(v >> _SHIFT_FLAGS) & _MASK_10,
    )


# ---------------------------------------------------------------------------
# Relation tags  (structural role inside a parent level)
# ---------------------------------------------------------------------------


class RelationTag(enum.IntEnum):
    """Structural role of an element within its parent composition level."""

    BASE = 1
    DIACRITIC = 2
    SYLLABLE = 3
    PATTERN = 4
    LEXEME = 5
    SENTENCE = 6
    TEXT = 7


# ---------------------------------------------------------------------------
# Fractal composition across levels
# ---------------------------------------------------------------------------

#: Mersenne prime 2**61 - 1, used as the default base for the
#: prime-power composition scheme.
DEFAULT_PRIME: int = 2305843009213693951


def compose(
    values: list[int],
    relation_tags: list[int],
    prime: int = DEFAULT_PRIME,
) -> int:
    """Combine ``(value, relation_tag)`` pairs into a single integer.

    .. math::

        F_{k+1} = \\sum_{i=1}^{m} (v_i + r_i) \\cdot p^{i-1}

    where *p* is *prime*.  This is order-sensitive and interpretable:
    each addend carries the structural role *r_i* of the element.

    Raises ``ValueError`` when the two lists differ in length.
    """
    if len(values) != len(relation_tags):
        raise ValueError(
            f"values and relation_tags must have the same length, "
            f"got {len(values)} and {len(relation_tags)}"
        )
    acc = 0
    for i, (v, r) in enumerate(zip(values, relation_tags)):
        acc += (v + r) * pow(prime, i)
    return acc
