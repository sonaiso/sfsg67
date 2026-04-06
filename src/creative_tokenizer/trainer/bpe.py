from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ..pretokenizer import pretokenize

SCHEMA_VERSION = 1


@dataclass
class BpeMerges:
    merges: list[tuple[str, str]]
    vocab: dict[str, int]

    @property
    def size(self) -> int:
        return len(self.vocab)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, object]:
        return {
            "format_version": SCHEMA_VERSION,
            "model_type": "bpe",
            "merges": [[a, b] for a, b in self.merges],
            "vocab": self.vocab,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> BpeMerges:
        version = data.get("format_version")
        if version != SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported format_version {version!r}; expected {SCHEMA_VERSION}"
            )
        model_type = data.get("model_type")
        if model_type != "bpe":
            raise ValueError(f"Expected model_type 'bpe', got {model_type!r}")

        raw_merges = data.get("merges")
        if not isinstance(raw_merges, list):
            raise ValueError("'merges' must be a list")
        raw_vocab = data.get("vocab")
        if not isinstance(raw_vocab, dict):
            raise ValueError("'vocab' must be a dict")

        merges: list[tuple[str, str]] = []
        for item in raw_merges:
            if not isinstance(item, list) or len(item) != 2:
                raise ValueError(f"Each merge must be a 2-element list, got {item!r}")
            a, b = item
            if not isinstance(a, str) or not isinstance(b, str):
                raise ValueError(f"Merge elements must be strings, got {item!r}")
            merges.append((a, b))

        vocab: dict[str, int] = {}
        for k, v in raw_vocab.items():
            if not isinstance(v, int):
                raise ValueError(f"Vocab values must be int, got {k!r}: {v!r}")
            vocab[k] = v

        return cls(merges=merges, vocab=vocab)

    def save_json(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)

    @classmethod
    def load_json(cls, path: str | Path) -> BpeMerges:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        return cls.from_dict(data)


def _get_pair_counts(
    word_freqs: dict[tuple[str, ...], int],
) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for word, freq in word_freqs.items():
        for i in range(len(word) - 1):
            counts[(word[i], word[i + 1])] += freq
    return counts


def _merge_pair(
    word_freqs: dict[tuple[str, ...], int],
    pair: tuple[str, str],
) -> dict[tuple[str, ...], int]:
    a, b = pair
    merged = a + b
    new_word_freqs: dict[tuple[str, ...], int] = {}
    for word, freq in word_freqs.items():
        new_word: list[str] = []
        i = 0
        while i < len(word):
            if i < len(word) - 1 and word[i] == a and word[i + 1] == b:
                new_word.append(merged)
                i += 2
            else:
                new_word.append(word[i])
                i += 1
        new_word_freqs[tuple(new_word)] = freq
    return new_word_freqs


class BpeTrainer:
    def __init__(self, vocab_size: int) -> None:
        if vocab_size < 1:
            raise ValueError(f"vocab_size must be at least 1, got {vocab_size}")
        self.vocab_size = vocab_size

    def train(self, corpus: Iterable[str]) -> BpeMerges:
        word_counter: Counter[str] = Counter()
        for text in corpus:
            for pretoken in pretokenize(text):
                word_counter[pretoken.word] += 1

        word_freqs: dict[tuple[str, ...], int] = {
            tuple(word): freq for word, freq in word_counter.items()
        }

        base_chars: set[str] = set()
        for word in word_freqs:
            base_chars.update(word)

        vocab: dict[str, int] = {ch: i for i, ch in enumerate(sorted(base_chars))}
        merges: list[tuple[str, str]] = []

        while len(vocab) < self.vocab_size:
            pair_counts = _get_pair_counts(word_freqs)
            if not pair_counts:
                break
            best_pair: tuple[str, str] = max(
                pair_counts, key=lambda p: (pair_counts[p], p)
            )
            if pair_counts[best_pair] < 2:
                break
            merges.append(best_pair)
            new_token = best_pair[0] + best_pair[1]
            if new_token not in vocab:
                vocab[new_token] = len(vocab)
            word_freqs = _merge_pair(word_freqs, best_pair)

        return BpeMerges(merges=merges, vocab=vocab)
