from __future__ import annotations

import re
from dataclasses import dataclass

from .normalization import normalize_text

_WORD_PATTERN = re.compile(
    r"[\u0621-\u063A\u0641-\u064A\u0660-\u0669A-Za-z0-9]+|[^\s]",
    re.UNICODE,
)


@dataclass(frozen=True, slots=True)
class PreToken:
    word: str
    mapping: tuple[int, ...]


def pretokenize(text: str) -> list[PreToken]:
    normalized = normalize_text(text)
    result: list[PreToken] = []
    for match in _WORD_PATTERN.finditer(normalized.text):
        result.append(
            PreToken(
                word=match.group(0),
                mapping=normalized.mapping[match.start() : match.end()],
            )
        )
    return result
