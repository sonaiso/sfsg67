"""Phonological analysis of Arabic signifiers.

Builds the minimal signifier structure:
  grapheme cluster → consonant/vowel → syllable → phonological signature

Each level is a numeric tuple amenable to fractal identity computation.

  g = (base, m₁, m₂, …, mₖ)       — grapheme cluster
  s = (onset, nucleus, coda, weight) — syllable
"""

from __future__ import annotations

from dataclasses import dataclass

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

__all__ = [
    "GraphemeCluster",
    "PhonResult",
    "Syllable",
    "analyze_phonology",
]

# ── Arabic character sets ─────────────────────────────────────────────

_VOWEL_SHORT: frozenset[int] = frozenset({0x064E, 0x064F, 0x0650})
_VOWEL_LONG: frozenset[str] = frozenset({"ا", "و", "ي", "ى"})
_DIACRITICS: frozenset[int] = frozenset({
    0x064B, 0x064C, 0x064D, 0x064E, 0x064F, 0x0650, 0x0651, 0x0652, 0x0670,
})

_CONSONANTS: frozenset[str] = frozenset(
    "ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي ء ة".split()
)


# ── Data structures ───────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class GraphemeCluster:
    """A base character with its attached diacritics."""

    base: str
    marks: tuple[str, ...]
    cluster_id: int


@dataclass(frozen=True, slots=True)
class Syllable:
    """A phonological syllable: onset + nucleus + optional coda.

    weight: 1 = light (CV), 2 = heavy (CVC/CVV), 3 = superheavy (CVVC/CVCC)
    """

    onset: str
    nucleus: str
    coda: str
    weight: int
    syllable_id: int


@dataclass(frozen=True, slots=True)
class PhonResult:
    """Full phonological analysis of a word."""

    clusters: tuple[GraphemeCluster, ...]
    syllables: tuple[Syllable, ...]
    consonant_skeleton: tuple[str, ...]
    phonology_id: int


def _make_cluster(base: str, marks: tuple[str, ...]) -> GraphemeCluster:
    cid = fractal_fold([
        cantor_pair(1, ord(base)),
        *(cantor_pair(i + 2, ord(m)) for i, m in enumerate(marks)),
    ])
    return GraphemeCluster(base=base, marks=marks, cluster_id=cid)


def _make_syllable(onset: str, nucleus: str, coda: str) -> Syllable:
    if coda and nucleus and (nucleus in _VOWEL_LONG or ord(nucleus) in _VOWEL_SHORT):
        weight = 2
    elif nucleus in _VOWEL_LONG:
        weight = 2
    elif coda:
        weight = 2
    else:
        weight = 1
    sid = fractal_fold([
        cantor_pair(1, ord(onset) if onset else 0),
        cantor_pair(2, ord(nucleus) if nucleus else 0),
        cantor_pair(3, ord(coda) if coda else 0),
        cantor_pair(4, weight),
    ])
    return Syllable(onset=onset, nucleus=nucleus, coda=coda, weight=weight, syllable_id=sid)


def _segment_clusters(text: str) -> list[GraphemeCluster]:
    """Split text into grapheme clusters (base + following diacritics)."""
    clusters: list[GraphemeCluster] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == " ":
            i += 1
            continue
        marks: list[str] = []
        j = i + 1
        while j < len(text) and ord(text[j]) in _DIACRITICS:
            marks.append(text[j])
            j += 1
        clusters.append(_make_cluster(ch, tuple(marks)))
        i = j
    return clusters


def _extract_syllables(clusters: list[GraphemeCluster]) -> list[Syllable]:
    """Simple heuristic syllabification from grapheme clusters."""
    syllables: list[Syllable] = []
    i = 0
    while i < len(clusters):
        c = clusters[i]
        onset = c.base if c.base in _CONSONANTS else ""
        # Determine nucleus
        nucleus = ""
        for m in c.marks:
            if ord(m) in _VOWEL_SHORT:
                nucleus = m
                break
        # Check for long vowel (next cluster)
        if nucleus and i + 1 < len(clusters) and clusters[i + 1].base in _VOWEL_LONG:
            nucleus = clusters[i + 1].base
            i += 1
        # Determine coda
        coda = ""
        if i + 1 < len(clusters) and clusters[i + 1].base in _CONSONANTS:
            # Peek ahead: if the next consonant has no vowel mark, it's a coda
            next_c = clusters[i + 1]
            has_vowel = any(ord(m) in _VOWEL_SHORT for m in next_c.marks)
            if not has_vowel and (
                i + 2 >= len(clusters)
                or clusters[i + 2].base not in _VOWEL_LONG
            ):
                coda = next_c.base
                i += 1
        if onset or nucleus:
            syllables.append(_make_syllable(onset, nucleus, coda))
        i += 1
    return syllables if syllables else [_make_syllable("", "", "")]


def analyze_phonology(text: str) -> PhonResult:
    """Analyze the phonological structure of an Arabic word.

    Returns grapheme clusters, syllables, and consonant skeleton.
    """
    clusters = _segment_clusters(text)
    syllables = _extract_syllables(clusters)
    skeleton = tuple(c.base for c in clusters if c.base in _CONSONANTS)
    phon_id = fractal_fold([
        *(c.cluster_id for c in clusters),
        *(s.syllable_id for s in syllables),
    ])
    return PhonResult(
        clusters=tuple(clusters),
        syllables=tuple(syllables),
        consonant_skeleton=skeleton,
        phonology_id=phon_id,
    )
