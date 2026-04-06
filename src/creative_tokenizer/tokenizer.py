from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .pretokenizer import pretokenize

_ARABIC_LETTER_PATTERN = re.compile(r"[\u0621-\u064A]")
_PREFIXES = ("و", "ف", "ب", "ك", "ل", "س")
_SUFFIXES = ("كما", "كم", "كن", "هما", "هم", "هن", "نا", "ها", "ه", "ك", "ي")


@dataclass(frozen=True, slots=True)
class Token:
    text: str
    normalized: str
    start: int
    end: int

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)


class CreativeTokenizer:
    def __init__(self, *, segment_clitics: bool = False) -> None:
        self.segment_clitics = segment_clitics

    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []

        for pretoken in pretokenize(text):
            if self.segment_clitics and _ARABIC_LETTER_PATTERN.search(pretoken.word):
                tokens.extend(self._segment_token(text, pretoken.word, pretoken.mapping))
                continue

            tokens.append(self._build_token(text, pretoken.word, pretoken.mapping))

        return tokens

    def _segment_token(
        self,
        text: str,
        normalized_token: str,
        token_mapping: tuple[int, ...],
    ) -> list[Token]:
        if not token_mapping:
            return []

        pieces: list[tuple[str, tuple[int, ...]]] = []
        start_index = 0

        while start_index < len(normalized_token) - 2:
            candidate = normalized_token[start_index]
            remaining = normalized_token[start_index + 1 :]
            if candidate not in _PREFIXES or len(remaining) < 2:
                break
            pieces.append((candidate, token_mapping[start_index : start_index + 1]))
            start_index += 1

        core_text = normalized_token[start_index:]
        core_mapping = token_mapping[start_index:]

        suffix_piece: tuple[str, tuple[int, ...]] | None = None
        for suffix in _SUFFIXES:
            if not core_text.endswith(suffix):
                continue
            stem_length = len(core_text) - len(suffix)
            if stem_length < 2:
                continue
            suffix_piece = (suffix, core_mapping[stem_length:])
            core_text = core_text[:stem_length]
            core_mapping = core_mapping[:stem_length]
            break

        if core_text:
            pieces.append((core_text, core_mapping))

        if suffix_piece is not None:
            pieces.append(suffix_piece)

        return [
            self._build_token(text, piece_text, piece_mapping)
            for piece_text, piece_mapping in pieces
        ]

    def _build_token(
        self,
        text: str,
        normalized_text: str,
        token_mapping: tuple[int, ...],
    ) -> Token:
        start = token_mapping[0]
        end = token_mapping[-1] + 1
        return Token(text=text[start:end], normalized=normalized_text, start=start, end=end)
