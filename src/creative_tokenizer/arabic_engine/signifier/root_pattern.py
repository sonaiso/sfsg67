"""Root and pattern extraction for Arabic words.

L: ℕ* → T   where T = (lemma_id, root_id, pattern_id, pos_id, feature_vector)

Implements a simple rule-based root extractor and pattern matcher using a
built-in trilateral root lexicon.  The lexicon is intentionally small and
explicit — morphology-heavy heuristics belong in optional extensions.
"""

from __future__ import annotations

from dataclasses import dataclass

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

__all__ = [
    "RootPatternResult",
    "extract_root_pattern",
]


# ── Built-in minimal root lexicon ─────────────────────────────────────

_ROOT_LEXICON: dict[str, tuple[str, str, str]] = {
    # root consonants → (root_str, default_pattern, default_pos)
    "كتب": ("كتب", "فَعَلَ", "verb"),
    "قرأ": ("قرأ", "فَعَلَ", "verb"),
    "علم": ("علم", "فَعِلَ", "verb"),
    "ذهب": ("ذهب", "فَعَلَ", "verb"),
    "جلس": ("جلس", "فَعَلَ", "verb"),
    "فتح": ("فتح", "فَعَلَ", "verb"),
    "خرج": ("خرج", "فَعَلَ", "verb"),
    "دخل": ("دخل", "فَعَلَ", "verb"),
    "سمع": ("سمع", "فَعِلَ", "verb"),
    "نصر": ("نصر", "فَعَلَ", "verb"),
    "رسل": ("رسل", "فِعَالَة", "noun"),
    "زيد": ("زيد", "فَعْل", "noun"),
    "عمر": ("عمر", "فُعَل", "noun"),
    "حسن": ("حسن", "فَعَلَ", "verb"),
    "صلح": ("صلح", "فَعُلَ", "verb"),
    "كبر": ("كبر", "فَعُلَ", "verb"),
    "حمد": ("حمد", "فَعِلَ", "verb"),
    "شكر": ("شكر", "فَعَلَ", "verb"),
}


# ── Diacritics and prefixes for stripping ─────────────────────────────

_DIACRITICS: frozenset[int] = frozenset({
    0x064B, 0x064C, 0x064D, 0x064E, 0x064F, 0x0650, 0x0651, 0x0652, 0x0670,
})

_DEFINITE_ARTICLE = "ال"

_CONSONANTS: frozenset[str] = frozenset(
    "ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي ء ة".split()
)


@dataclass(frozen=True, slots=True)
class RootPatternResult:
    """Root + pattern extraction result.

    Attributes
    ----------
    root:        root consonants (e.g. "كتب")
    pattern:     morphological pattern (e.g. "فَعَلَ")
    pos:         part-of-speech tag
    lemma:       reconstructed lemma
    root_id:     fractal identity of the root
    pattern_id:  fractal identity of the pattern
    """

    root: str
    pattern: str
    pos: str
    lemma: str
    root_id: int
    pattern_id: int


def _strip_diacritics(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) not in _DIACRITICS)


def _extract_consonants(text: str) -> str:
    stripped = _strip_diacritics(text)
    # Remove definite article
    if stripped.startswith(_DEFINITE_ARTICLE):
        stripped = stripped[len(_DEFINITE_ARTICLE):]
    # Filter to consonants only
    return "".join(ch for ch in stripped if ch in _CONSONANTS)


def extract_root_pattern(word: str) -> RootPatternResult:
    """Extract root and pattern from an Arabic word.

    Tries full consonant skeleton first, then 3-consonant sub-skeleton.
    Falls back to unknown root if no match is found.
    """
    skeleton = _extract_consonants(word)

    # Try full match
    if skeleton in _ROOT_LEXICON:
        root_str, pattern, pos = _ROOT_LEXICON[skeleton]
    elif len(skeleton) >= 3:
        # Try 3-consonant sub-skeleton
        tri = skeleton[:3]
        if tri in _ROOT_LEXICON:
            root_str, pattern, pos = _ROOT_LEXICON[tri]
        else:
            root_str, pattern, pos = skeleton[:3], "فَعَلَ", "unknown"
    else:
        root_str, pattern, pos = skeleton or "?", "?", "unknown"

    lemma = root_str

    root_id = fractal_fold([cantor_pair(i + 1, ord(c)) for i, c in enumerate(root_str)])
    pattern_id = fractal_fold([cantor_pair(i + 1, ord(c)) for i, c in enumerate(pattern)])

    return RootPatternResult(
        root=root_str,
        pattern=pattern,
        pos=pos,
        lemma=lemma,
        root_id=root_id,
        pattern_id=pattern_id,
    )
