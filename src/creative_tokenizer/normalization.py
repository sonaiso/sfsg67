from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "NormalizationProfile",
    "NormalizedText",
    "normalize_text",
]

# ── Normalization profiles ───────────────────────────────────────────


class NormalizationProfile(Enum):
    """Normalization strictness level.

    CONSERVATIVE — remove tatweel only; preserve diacritics and hamza forms.
    STANDARD     — remove diacritics + tatweel, unify hamza/ya/waw/ta-marbuta.
                   (this is the original default behaviour)
    MORPHOLOGICAL — like STANDARD but maps ة→ت (not ه) for morphological analysis.
    """

    CONSERVATIVE = "conservative"
    STANDARD = "standard"
    MORPHOLOGICAL = "morphological"


_DIACRITICS = {
    "\u0610",
    "\u0611",
    "\u0612",
    "\u0613",
    "\u0614",
    "\u0615",
    "\u0616",
    "\u0617",
    "\u0618",
    "\u0619",
    "\u061A",
    "\u064B",
    "\u064C",
    "\u064D",
    "\u064E",
    "\u064F",
    "\u0650",
    "\u0651",
    "\u0652",
    "\u0653",
    "\u0654",
    "\u0655",
    "\u0656",
    "\u0657",
    "\u0658",
    "\u0659",
    "\u065A",
    "\u065B",
    "\u065C",
    "\u065D",
    "\u065E",
    "\u065F",
    "\u0670",
    "\u06D6",
    "\u06D7",
    "\u06D8",
    "\u06D9",
    "\u06DA",
    "\u06DB",
    "\u06DC",
    "\u06DF",
    "\u06E0",
    "\u06E1",
    "\u06E2",
    "\u06E3",
    "\u06E4",
    "\u06E7",
    "\u06E8",
    "\u06EA",
    "\u06EB",
    "\u06EC",
    "\u06ED",
}

_CHAR_REPLACEMENTS_STANDARD: dict[str, str] = {
    "أ": "ا",
    "إ": "ا",
    "آ": "ا",
    "ٱ": "ا",
    "ى": "ي",
    "ؤ": "و",
    "ئ": "ي",
    "ة": "ه",
    "ﻻ": "لا",
    "ﻷ": "لا",
    "ﻹ": "لا",
    "ﻵ": "لا",
}

# Backward-compatible alias used by existing callers that reference the old name.
_CHAR_REPLACEMENTS = _CHAR_REPLACEMENTS_STANDARD

_CHAR_REPLACEMENTS_MORPHOLOGICAL: dict[str, str] = {
    **_CHAR_REPLACEMENTS_STANDARD,
    "ة": "ت",  # ta-marbuta → ta (not ha) for morphological analysis
}


@dataclass(frozen=True, slots=True)
class NormalizedText:
    text: str
    mapping: tuple[int, ...]


def normalize_text(
    text: str,
    profile: NormalizationProfile = NormalizationProfile.STANDARD,
) -> NormalizedText:
    """Normalize *text* according to *profile*, preserving a char-index mapping.

    The mapping tuple has the same length as the normalised text and maps each
    normalised character back to its position in the original *text*.
    """
    normalized_chars: list[str] = []
    mapping: list[int] = []

    if profile is NormalizationProfile.CONSERVATIVE:
        # Only strip tatweel; keep diacritics and hamza forms.
        for original_index, char in enumerate(text):
            if char == "ـ":
                continue
            normalized_chars.append(char)
            mapping.append(original_index)
        return NormalizedText(text="".join(normalized_chars), mapping=tuple(mapping))

    replacements = (
        _CHAR_REPLACEMENTS_MORPHOLOGICAL
        if profile is NormalizationProfile.MORPHOLOGICAL
        else _CHAR_REPLACEMENTS_STANDARD
    )

    for original_index, char in enumerate(text):
        if char == "ـ" or char in _DIACRITICS:
            continue

        replacement = replacements.get(char, char)
        for normalized_char in replacement:
            normalized_chars.append(normalized_char)
            mapping.append(original_index)

    return NormalizedText(text="".join(normalized_chars), mapping=tuple(mapping))
