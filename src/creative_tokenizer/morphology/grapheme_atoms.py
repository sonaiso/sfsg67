from __future__ import annotations

from ..normalization import _DIACRITICS
from .fractal_storage import cantor_pair, fractal_fold, phi

_TATWEEL = "\u0640"


def grapheme_clusters(text: str) -> list[tuple[str, tuple[str, ...]]]:
    """Split text into (base_char, diacritics) pairs.

    Each base character carries its immediately following diacritics.
    Orphaned leading diacritics and tatweel are silently skipped.
    """
    clusters: list[tuple[str, tuple[str, ...]]] = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in _DIACRITICS or char == _TATWEEL:
            i += 1
            continue
        marks: list[str] = []
        j = i + 1
        while j < len(text) and text[j] in _DIACRITICS:
            marks.append(text[j])
            j += 1
        clusters.append((char, tuple(marks)))
        i = j
    return clusters


def consonantal_skeleton(text: str) -> tuple[str, ...]:
    """Return base characters only, stripping all diacritics and tatweel."""
    return tuple(base for base, _ in grapheme_clusters(text))


def consonantal_skeleton_id(text: str) -> int:
    """C(w) = F(φ(c1), ..., φ(ck)) — identity of the consonantal skeleton."""
    skeleton = consonantal_skeleton(text)
    if not skeleton:
        return 0
    return fractal_fold([phi(c) for c in skeleton])


def grapheme_atom_id(base: str, marks: tuple[str, ...]) -> int:
    """G_i = π(φ(c_i), M(m_i)) where M is the fractal fold of mark codepoints."""
    mark_id = fractal_fold([phi(m) for m in marks]) if marks else 0
    return cantor_pair(phi(base), mark_id)


def grapheme_surface_id(text: str) -> int:
    """G(w) = F(G1, G2, ..., Gk) — full grapheme-cluster surface identity."""
    clusters = grapheme_clusters(text)
    if not clusters:
        return 0
    return fractal_fold([grapheme_atom_id(base, marks) for base, marks in clusters])
