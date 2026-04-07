from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .pretokenizer import pretokenize

__all__ = ["CliticRules", "CreativeTokenizer", "Token"]

_ARABIC_LETTER_PATTERN = re.compile(r"[\u0621-\u064A]")
_PREFIXES = ("و", "ف", "ب", "ك", "ل", "س")
_SUFFIXES = ("كما", "كم", "كن", "هما", "هم", "هن", "نا", "ها", "ه", "ك", "ي")


# ── Clitic rule configuration ────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class CliticRules:
    """Configurable clitic-segmentation rules.

    ``prefixes`` and ``suffixes`` are ordered longest-first so that
    greedy matching peels the longest affix first.

    ``min_stem_length`` (default 2) prevents over-segmentation.

    ``bidirectional`` (default True) allows both a prefix *and* a suffix
    to be stripped from the same word.
    """

    prefixes: tuple[str, ...]
    suffixes: tuple[str, ...]
    min_stem_length: int = 2
    bidirectional: bool = True

    # -- Serialization -------------------------------------------------

    def to_dict(self) -> dict[str, object]:
        return {
            "prefixes": list(self.prefixes),
            "suffixes": list(self.suffixes),
            "min_stem_length": self.min_stem_length,
            "bidirectional": self.bidirectional,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> CliticRules:
        raw_pre = data.get("prefixes")
        if not isinstance(raw_pre, list):
            raise ValueError("'prefixes' must be a list of strings")
        raw_suf = data.get("suffixes")
        if not isinstance(raw_suf, list):
            raise ValueError("'suffixes' must be a list of strings")
        min_stem = data.get("min_stem_length", 2)
        if not isinstance(min_stem, int) or min_stem < 1:
            raise ValueError("'min_stem_length' must be a positive integer")
        bidir = data.get("bidirectional", True)
        if not isinstance(bidir, bool):
            raise ValueError("'bidirectional' must be a boolean")
        return cls(
            prefixes=tuple(str(p) for p in raw_pre),
            suffixes=tuple(str(s) for s in raw_suf),
            min_stem_length=min_stem,
            bidirectional=bidir,
        )

    @classmethod
    def from_json(cls, path: str | Path) -> CliticRules:
        """Load clitic rules from a JSON file."""
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        return cls.from_dict(data)

    def save_json(self, path: str | Path) -> None:
        """Save clitic rules to a JSON file."""
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)


#: Pre-built default rules matching current hard-coded behaviour.
DEFAULT_CLITIC_RULES = CliticRules(
    prefixes=_PREFIXES,
    suffixes=_SUFFIXES,
    min_stem_length=2,
    bidirectional=True,
)
# Alias for convenience on the class itself
CliticRules.DEFAULT = DEFAULT_CLITIC_RULES  # type: ignore[attr-defined]


@dataclass(frozen=True, slots=True)
class Token:
    """A single token with its normalised form and span into the source text.

    The core invariant is ``source[start:end] == text``.
    """

    text: str
    normalized: str
    start: int
    end: int

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)


class CreativeTokenizer:
    def __init__(
        self,
        *,
        segment_clitics: bool = False,
        clitic_rules: CliticRules | None = None,
    ) -> None:
        self.segment_clitics = segment_clitics
        self._rules: CliticRules = clitic_rules or CliticRules.DEFAULT  # type: ignore[attr-defined]

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

        rules = self._rules
        pieces: list[tuple[str, tuple[int, ...]]] = []
        start_index = 0

        while start_index < len(normalized_token) - rules.min_stem_length:
            candidate = normalized_token[start_index]
            remaining = normalized_token[start_index + 1 :]
            if candidate not in rules.prefixes or len(remaining) < rules.min_stem_length:
                break
            pieces.append((candidate, token_mapping[start_index : start_index + 1]))
            start_index += 1

        core_text = normalized_token[start_index:]
        core_mapping = token_mapping[start_index:]

        suffix_piece: tuple[str, tuple[int, ...]] | None = None
        if rules.bidirectional or not pieces:
            for suffix in rules.suffixes:
                if not core_text.endswith(suffix):
                    continue
                stem_length = len(core_text) - len(suffix)
                if stem_length < rules.min_stem_length:
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
