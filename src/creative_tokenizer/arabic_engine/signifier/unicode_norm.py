"""Unicode normalization for Arabic text (التطبيع).

N: ℕ* → ℕ*

Removes tatweel (kashida), normalizes whitespace, and optionally strips or
preserves diacritics.  Every character maps to the normalized output with a
position mapping so that token spans remain valid against the original input.

Policy modes:
  PRESERVE_DIACRITICS — keep all tashkeel marks
  STRIP_DIACRITICS   — remove fatha, damma, kasra, shadda, sukun, tanween
  NORMALIZE_ALIF     — unify alif variants (أ إ آ → ا)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

__all__ = ["NormMode", "NormResult", "normalize_arabic"]

# ── Diacritic code points (tashkeel) ─────────────────────────────────

_DIACRITICS: frozenset[int] = frozenset({
    0x064B,  # FATHATAN
    0x064C,  # DAMMATAN
    0x064D,  # KASRATAN
    0x064E,  # FATHA
    0x064F,  # DAMMA
    0x0650,  # KASRA
    0x0651,  # SHADDA
    0x0652,  # SUKUN
    0x0670,  # SUPERSCRIPT ALEF
})

# ── Alif variant → plain alif ────────────────────────────────────────

_ALIF_MAP: dict[str, str] = {
    "\u0622": "\u0627",  # ALEF WITH MADDA ABOVE → ALEF
    "\u0623": "\u0627",  # ALEF WITH HAMZA ABOVE → ALEF
    "\u0625": "\u0627",  # ALEF WITH HAMZA BELOW → ALEF
    "\u0671": "\u0627",  # ALEF WASLA → ALEF
}

_TATWEEL = "\u0640"  # ARABIC TATWEEL (kashida)


class NormMode(IntEnum):
    """Normalization policy."""

    PRESERVE_DIACRITICS = 1
    STRIP_DIACRITICS = 2


@dataclass(frozen=True, slots=True)
class NormResult:
    """Result of Arabic normalization.

    Attributes
    ----------
    text:      normalized string
    mapping:   tuple mapping each output index to its original index
    original:  the original input string
    """

    text: str
    mapping: tuple[int, ...]
    original: str


def normalize_arabic(
    text: str,
    *,
    mode: NormMode = NormMode.STRIP_DIACRITICS,
    normalize_alif: bool = True,
) -> NormResult:
    """Normalize Arabic text deterministically.

    Parameters
    ----------
    text:           raw Arabic input
    mode:           diacritic handling policy
    normalize_alif: whether to unify alif variants

    Returns
    -------
    NormResult with normalized text and position mapping.
    """
    out_chars: list[str] = []
    mapping: list[int] = []

    for i, ch in enumerate(text):
        # Remove tatweel
        if ch == _TATWEEL:
            continue

        # Optionally strip diacritics
        if mode == NormMode.STRIP_DIACRITICS and ord(ch) in _DIACRITICS:
            continue

        # Normalize whitespace runs
        if ch in (" ", "\t", "\n", "\r"):
            if out_chars and out_chars[-1] != " ":
                out_chars.append(" ")
                mapping.append(i)
            continue

        # Normalize alif variants
        if normalize_alif and ch in _ALIF_MAP:
            out_chars.append(_ALIF_MAP[ch])
            mapping.append(i)
            continue

        out_chars.append(ch)
        mapping.append(i)

    # Strip trailing space
    if out_chars and out_chars[-1] == " ":
        out_chars.pop()
        mapping.pop()

    return NormResult(
        text="".join(out_chars),
        mapping=tuple(mapping),
        original=text,
    )
