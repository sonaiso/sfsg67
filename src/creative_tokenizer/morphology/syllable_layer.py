"""Syllable layer — §4 of the formal hierarchical specification.

Arabic syllables follow a small set of canonical shapes:

=====  =========================================
Shape  Structure
=====  =========================================
CV     consonant + short vowel
CVC    consonant + short vowel + consonant
CVV    consonant + long vowel
CVVC   consonant + long vowel + consonant
CVCC   consonant + short vowel + two consonants
=====  =========================================

The module provides:

* ``SyllableShape`` enum — the five canonical shapes.
* ``Syllable`` dataclass — shape + grapheme-cluster content + position.
* ``build_syllable`` — validates and wraps clusters into a ``Syllable``.
* ``syllable_id`` — fractal identity of a syllable.

**Phonotactic constraints** (§4 specification):

1. No onset cluster (Arabic syllables always start with exactly one consonant).
2. No adjacent guttural consonants within a single syllable.
3. Coda clusters (CVCC) only appear word-finally.

The builder does *not* perform full word-level syllabification; that requires
higher-layer context.  It validates a *candidate* cluster sequence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold, phi
from .phonological_sets import (
    CONSONANT_ROOT,
    VOWEL_LONG,
    VOWEL_SHORT,
    PlaceOfArticulation,
    place_of_articulation,
)


class SyllableShape(IntEnum):
    """Canonical Arabic syllable shapes — §4."""

    CV = 1
    CVC = 2
    CVV = 3
    CVVC = 4
    CVCC = 5


@dataclass(frozen=True, slots=True)
class Syllable:
    """A single syllable with its shape, clusters, and word position.

    ``clusters`` stores the raw grapheme clusters (base, marks) that were
    consumed to form this syllable.  ``position`` is a zero-based index
    within the word.
    """

    shape: SyllableShape
    clusters: tuple[tuple[str, tuple[str, ...]], ...]
    position: int


# ---------------------------------------------------------------------------
# Phonotactic helpers
# ---------------------------------------------------------------------------

_GUTTURAL_PLACES: frozenset[PlaceOfArticulation] = frozenset(
    {
        PlaceOfArticulation.PHARYNGEAL,
        PlaceOfArticulation.GLOTTAL,
    }
)


def _is_consonant(cp: int) -> bool:
    """Return True if the code-point is an Arabic consonant."""
    return cp in CONSONANT_ROOT or cp in frozenset({0x0627, 0x0629, 0x0649})


def _is_short_vowel(cp: int) -> bool:
    return cp in VOWEL_SHORT


def _is_long_vowel(cp: int) -> bool:
    return cp in VOWEL_LONG


def _adjacent_guttural(c1: int, c2: int) -> bool:
    """Return True if two consonants are both guttural — forbidden adjacency."""
    p1 = place_of_articulation(c1)
    p2 = place_of_articulation(c2)
    return (p1 in _GUTTURAL_PLACES) and (p2 in _GUTTURAL_PLACES)


# ---------------------------------------------------------------------------
# Shape detection from cluster sequence
# ---------------------------------------------------------------------------


def detect_shape(
    clusters: tuple[tuple[str, tuple[str, ...]], ...],
) -> SyllableShape | None:
    """Detect the syllable shape from a sequence of grapheme clusters.

    Returns ``None`` if the sequence does not match any canonical shape.
    Each cluster is ``(base_char, diacritics)``.
    """
    if not clusters:
        return None

    bases = [ord(c[0]) for c in clusters]
    # Collect first diacritic of each cluster (if any)
    first_marks = [ord(c[1][0]) if c[1] else None for c in clusters]

    if len(clusters) == 1:
        # CV: one consonant + short vowel (as diacritic)
        if (
            _is_consonant(bases[0])
            and first_marks[0] is not None
            and _is_short_vowel(first_marks[0])
        ):
            return SyllableShape.CV
        return None

    if len(clusters) == 2:
        # CVV: C+short_vowel + long_vowel_letter  (check before CVC)
        if (
            _is_consonant(bases[0])
            and first_marks[0] is not None
            and _is_short_vowel(first_marks[0])
            and _is_long_vowel(bases[1])
        ):
            return SyllableShape.CVV
        # CVC: C+short_vowel C(+sukun or no vowel)
        if (
            _is_consonant(bases[0])
            and first_marks[0] is not None
            and _is_short_vowel(first_marks[0])
            and _is_consonant(bases[1])
        ):
            return SyllableShape.CVC
        return None

    if len(clusters) == 3:
        # CVVC: C+short_vowel + long_vowel + C
        if (
            _is_consonant(bases[0])
            and first_marks[0] is not None
            and _is_short_vowel(first_marks[0])
            and _is_long_vowel(bases[1])
            and _is_consonant(bases[2])
        ):
            return SyllableShape.CVVC
        # CVCC: C+short_vowel + C + C  (word-final only)
        if (
            _is_consonant(bases[0])
            and first_marks[0] is not None
            and _is_short_vowel(first_marks[0])
            and _is_consonant(bases[1])
            and _is_consonant(bases[2])
        ):
            return SyllableShape.CVCC
        return None

    return None


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_syllable(
    clusters: tuple[tuple[str, tuple[str, ...]], ...],
    position: int = 0,
) -> Syllable:
    """Build a ``Syllable`` from grapheme clusters.

    Raises ``ValueError`` if the cluster sequence does not match any
    canonical Arabic syllable shape.
    """
    shape = detect_shape(clusters)
    if shape is None:
        bases = "".join(c[0] for c in clusters)
        raise ValueError(f"Cluster sequence does not form a valid syllable: {bases!r}")
    return Syllable(shape=shape, clusters=clusters, position=position)


# ---------------------------------------------------------------------------
# Fractal identity
# ---------------------------------------------------------------------------


def syllable_id(syl: Syllable) -> int:
    """Compute the fractal identity of a syllable.

    σ_id = π(shape, F(cluster_atoms))

    where each cluster atom is π(φ(base), F(φ(m) for m in marks)).
    """
    atoms: list[int] = []
    for base, marks in syl.clusters:
        mark_fold = fractal_fold([phi(m) for m in marks]) if marks else 0
        atoms.append(cantor_pair(phi(base), mark_fold))
    return cantor_pair(int(syl.shape), fractal_fold(atoms))
