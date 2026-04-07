"""Formal layer chain — §16–17 of the hierarchical specification.

The complete formal chain from the atom to the sentence:

    𝒰 → (𝒞, 𝒱, 𝒟) → 𝒢_gr → 𝒮_yl → (ℛ, 𝒲) → (ℰ, 𝒩, ℱ, ℒ, 𝒵) → 𝒳 → 𝒮

This module defines:

* ``LayerIndex`` — enum of all formal layers in order.
* ``FormalLayer`` — dataclass wrapping each layer's metadata.
* ``FORMAL_CHAIN`` — the ordered sequence of all layers.
* ``generative_compose`` / ``analytic_compose`` — §17 compositional /
  decompositional function chains.

The layer chain is *query-only*; it does not perform computation.  It
provides the structural backbone that higher-level routines can walk.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

# ---------------------------------------------------------------------------
# §16  Layer index
# ---------------------------------------------------------------------------


class LayerIndex(IntEnum):
    """Ordered index of every formal layer — §16.

    The integer values encode the level's position in the chain.
    """

    UNICODE = 0  # 𝒰  — raw Unicode symbols
    PHONOLOGICAL = 1  # (𝒞, 𝒱, 𝒟) — consonants, vowels, diacritics
    GRAPHEME = 2  # 𝒢_gr — grapheme clusters
    SYLLABLE = 3  # 𝒮_yl — syllables
    ROOT_PATTERN = 4  # (ℛ, 𝒲) — roots and patterns
    LEXICAL = 5  # (ℰ, 𝒩, ℱ, ℒ, 𝒵) — events, nouns, verbs, particles, augmentation
    CLOSED_WORD = 6  # 𝒳  — closed lexical items
    SENTENCE = 7  # 𝒮  — sentences


@dataclass(frozen=True, slots=True)
class FormalLayer:
    """Metadata for a single layer in the formal chain."""

    index: LayerIndex
    symbol: str  # mathematical symbol (e.g. "𝒰", "𝒢_gr")
    label_ar: str  # Arabic label
    label_en: str  # English label
    modules: tuple[str, ...]  # implementing Python modules
    layer_id: int  # stable fractal identity


def _layer_id(idx: LayerIndex, modules: tuple[str, ...]) -> int:
    mod_fold = (
        fractal_fold([cantor_pair(i + 1, hash(m) % (2**31)) for i, m in enumerate(modules)])
        if modules
        else 0
    )
    return cantor_pair(int(idx), mod_fold)


# ---------------------------------------------------------------------------
# §16  Formal chain
# ---------------------------------------------------------------------------


def _make(
    idx: LayerIndex,
    symbol: str,
    label_ar: str,
    label_en: str,
    modules: tuple[str, ...],
) -> FormalLayer:
    return FormalLayer(
        index=idx,
        symbol=symbol,
        label_ar=label_ar,
        label_en=label_en,
        modules=modules,
        layer_id=_layer_id(idx, modules),
    )


FORMAL_CHAIN: tuple[FormalLayer, ...] = (
    _make(
        LayerIndex.UNICODE,
        "𝒰",
        "الرموز الخام",
        "Raw Unicode symbols",
        ("unicode_value", "unicode_identity"),
    ),
    _make(
        LayerIndex.PHONOLOGICAL,
        "(𝒞, 𝒱, 𝒟)",
        "الصوامت والصوائت والعلامات",
        "Consonants, vowels, diacritics",
        ("phonological_sets",),
    ),
    _make(
        LayerIndex.GRAPHEME,
        "𝒢_gr",
        "العناقيد الكتابية",
        "Grapheme clusters",
        ("grapheme_atoms",),
    ),
    _make(
        LayerIndex.SYLLABLE,
        "𝒮_yl",
        "المقاطع",
        "Syllables",
        ("syllable_layer",),
    ),
    _make(
        LayerIndex.ROOT_PATTERN,
        "(ℛ, 𝒲)",
        "الجذور والأوزان",
        "Roots and patterns",
        ("root_pattern",),
    ),
    _make(
        LayerIndex.LEXICAL,
        "(ℰ, 𝒩, ℱ, ℒ, 𝒵)",
        "الحدث والاسم والفعل والأداة والزيادة",
        "Events, nouns, verbs, particles, augmentation",
        ("event_layer", "particle_sets", "augmentation"),
    ),
    _make(
        LayerIndex.CLOSED_WORD,
        "𝒳",
        "اللفظ المفرد المغلق",
        "Closed lexical item",
        ("word_identity", "pre_compositional"),
    ),
    _make(
        LayerIndex.SENTENCE,
        "𝒮",
        "الجملة",
        "Sentence",
        ("sentence_node",),
    ),
)


def formal_layer(idx: LayerIndex) -> FormalLayer:
    """Return the FormalLayer for a given index."""
    return FORMAL_CHAIN[int(idx)]


def all_formal_layers() -> tuple[FormalLayer, ...]:
    """Return the complete ordered chain."""
    return FORMAL_CHAIN


# ---------------------------------------------------------------------------
# §17  Generative and analytic function chains
# ---------------------------------------------------------------------------


class ChainDirection(IntEnum):
    """Direction of traversal through the formal chain."""

    GENERATIVE = 1  # 𝒢 — bottom-up (Unicode → Sentence)
    ANALYTIC = 2  # 𝒜 — top-down (Sentence → Unicode)


@dataclass(frozen=True, slots=True)
class ChainStep:
    """A single step in a generative or analytic chain.

    ``source`` and ``target`` are LayerIndex values.
    ``function_name`` is the canonical name of the transition function.
    """

    source: LayerIndex
    target: LayerIndex
    function_name: str


#: Generative chain 𝒢 = 𝒢_sent ∘ 𝒢_lex ∘ 𝒢_pattern ∘ 𝒢_syl ∘ 𝒢_gr ∘ 𝒢_u
GENERATIVE_CHAIN: tuple[ChainStep, ...] = (
    ChainStep(LayerIndex.UNICODE, LayerIndex.PHONOLOGICAL, "𝒢_u"),
    ChainStep(LayerIndex.PHONOLOGICAL, LayerIndex.GRAPHEME, "𝒢_gr"),
    ChainStep(LayerIndex.GRAPHEME, LayerIndex.SYLLABLE, "𝒢_syl"),
    ChainStep(LayerIndex.SYLLABLE, LayerIndex.ROOT_PATTERN, "𝒢_pattern"),
    ChainStep(LayerIndex.ROOT_PATTERN, LayerIndex.LEXICAL, "𝒢_lex"),
    ChainStep(LayerIndex.LEXICAL, LayerIndex.CLOSED_WORD, "𝒢_close"),
    ChainStep(LayerIndex.CLOSED_WORD, LayerIndex.SENTENCE, "𝒢_sent"),
)

#: Analytic chain 𝒜 = 𝒜_u ∘ 𝒜_gr ∘ 𝒜_syl ∘ 𝒜_pattern ∘ 𝒜_lex ∘ 𝒜_sent
ANALYTIC_CHAIN: tuple[ChainStep, ...] = (
    ChainStep(LayerIndex.SENTENCE, LayerIndex.CLOSED_WORD, "𝒜_sent"),
    ChainStep(LayerIndex.CLOSED_WORD, LayerIndex.LEXICAL, "𝒜_lex"),
    ChainStep(LayerIndex.LEXICAL, LayerIndex.ROOT_PATTERN, "𝒜_pattern"),
    ChainStep(LayerIndex.ROOT_PATTERN, LayerIndex.SYLLABLE, "𝒜_syl"),
    ChainStep(LayerIndex.SYLLABLE, LayerIndex.GRAPHEME, "𝒜_gr"),
    ChainStep(LayerIndex.GRAPHEME, LayerIndex.PHONOLOGICAL, "𝒜_phono"),
    ChainStep(LayerIndex.PHONOLOGICAL, LayerIndex.UNICODE, "𝒜_u"),
)


def generative_chain() -> tuple[ChainStep, ...]:
    """Return the generative (bottom-up) function chain — §17."""
    return GENERATIVE_CHAIN


def analytic_chain() -> tuple[ChainStep, ...]:
    """Return the analytic (top-down) function chain — §17."""
    return ANALYTIC_CHAIN


def chain_id(direction: ChainDirection) -> int:
    """Stable identity of the entire chain in a given direction."""
    steps = GENERATIVE_CHAIN if direction == ChainDirection.GENERATIVE else ANALYTIC_CHAIN
    return cantor_pair(
        int(direction),
        fractal_fold([cantor_pair(int(s.source), int(s.target)) for s in steps]),
    )
