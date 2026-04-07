"""Shared frozen dataclasses for the Arabic Engine pipeline.

Token   — lexical closure output (lemma, root, pattern, POS, features)
Concept — ontological node (entity / event / attribute / relation / norm)
DalalLink — validated semantic linkage between a Token and a Concept

All dataclasses are frozen and slotted for immutability and memory efficiency.
Identity fields use the fractal Cantor pairing from the morphology subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

from .enums import DalalType, SemanticType

__all__ = ["Concept", "DalalLink", "Token"]


# ── Token (lexical closure output) ────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Token:
    """Lexical closure of a single Arabic word.

    Attributes
    ----------
    surface:    original surface form (with diacritics)
    normalized: normalized form
    lemma:      base lemma string
    root:       trilateral/quadrilateral root string
    pattern:    morphological pattern (وزن)
    pos:        part-of-speech tag
    features:   tuple of morphological features (e.g. tense, person, number …)
    span:       (start, end) character offsets in the original input
    token_id:   stable fractal identity
    """

    surface: str
    normalized: str
    lemma: str
    root: str
    pattern: str
    pos: str
    features: tuple[str, ...]
    span: tuple[int, int]
    token_id: int


def make_token(
    surface: str,
    normalized: str,
    lemma: str,
    root: str,
    pattern: str,
    pos: str,
    features: tuple[str, ...] = (),
    span: tuple[int, int] = (0, 0),
) -> Token:
    """Build a Token with a deterministic fractal identity."""
    token_id = fractal_fold([
        cantor_pair(1, sum(ord(c) for c in lemma)),
        cantor_pair(2, sum(ord(c) for c in root)),
        cantor_pair(3, sum(ord(c) for c in pattern)),
        cantor_pair(4, sum(ord(c) for c in pos)),
        cantor_pair(5, span[0]),
        cantor_pair(6, span[1]),
    ])
    return Token(
        surface=surface,
        normalized=normalized,
        lemma=lemma,
        root=root,
        pattern=pattern,
        pos=pos,
        features=features,
        span=span,
        token_id=token_id,
    )


# ── Concept (ontological node) ────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Concept:
    """An ontological concept derived from lexical closure.

    Attributes
    ----------
    label_ar:      Arabic label
    label_en:      English label
    semantic_type: SemanticType enum
    properties:    tuple of (key, value) property pairs
    concept_id:    stable fractal identity
    """

    label_ar: str
    label_en: str
    semantic_type: SemanticType
    properties: tuple[tuple[str, str], ...]
    concept_id: int


def make_concept(
    label_ar: str,
    label_en: str,
    semantic_type: SemanticType,
    properties: tuple[tuple[str, str], ...] = (),
) -> Concept:
    """Build a Concept with a deterministic fractal identity."""
    concept_id = fractal_fold([
        cantor_pair(1, sum(ord(c) for c in label_ar)),
        cantor_pair(2, int(semantic_type)),
        cantor_pair(3, len(properties)),
    ])
    return Concept(
        label_ar=label_ar,
        label_en=label_en,
        semantic_type=semantic_type,
        properties=properties,
        concept_id=concept_id,
    )


# ── DalalLink (validated semantic linkage) ────────────────────────────


@dataclass(frozen=True, slots=True)
class DalalLink:
    """A validated semantic linkage between a Token and a Concept.

    Attributes
    ----------
    token_id:   identity of the source Token
    concept_id: identity of the target Concept
    dalal_type: kind of dalāla (mutabaqa, tadammun, …)
    accepted:   whether the link passed validation
    confidence: confidence score in [0.0, 1.0]
    link_id:    stable fractal identity
    """

    token_id: int
    concept_id: int
    dalal_type: DalalType
    accepted: bool
    confidence: float
    link_id: int


def make_dalal_link(
    token_id: int,
    concept_id: int,
    dalal_type: DalalType,
    accepted: bool = True,
    confidence: float = 1.0,
) -> DalalLink:
    """Build a DalalLink with a deterministic fractal identity."""
    link_id = fractal_fold([
        cantor_pair(1, token_id),
        cantor_pair(2, concept_id),
        cantor_pair(3, int(dalal_type)),
        cantor_pair(4, int(accepted)),
        cantor_pair(5, int(confidence * 1000)),
    ])
    return DalalLink(
        token_id=token_id,
        concept_id=concept_id,
        dalal_type=dalal_type,
        accepted=accepted,
        confidence=confidence,
        link_id=link_id,
    )
