from __future__ import annotations

from dataclasses import dataclass

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

_CHAR_REPLACEMENTS = {
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


@dataclass(frozen=True, slots=True)
class NormalizedText:
    text: str
    mapping: tuple[int, ...]


def normalize_text(text: str) -> NormalizedText:
    normalized_chars: list[str] = []
    mapping: list[int] = []

    for original_index, char in enumerate(text):
        if char == "ـ" or char in _DIACRITICS:
            continue

        replacement = _CHAR_REPLACEMENTS.get(char, char)
        for normalized_char in replacement:
            normalized_chars.append(normalized_char)
            mapping.append(original_index)

    return NormalizedText(text="".join(normalized_chars), mapping=tuple(mapping))
