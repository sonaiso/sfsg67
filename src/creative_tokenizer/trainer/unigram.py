"""Unigram language-model trainer and model container.

Implements a simplified version of the unigram LM algorithm (Kudo 2018):
1. Initialize vocabulary from the most frequent substrings of pretokenized words.
2. Iteratively prune the lowest-loss pieces until ``vocab_size`` is reached.

The ``UnigramModel`` container mirrors the ``BpeMerges`` pattern, including
versioned JSON serialization via ``to_dict`` / ``from_dict`` / ``save_json`` /
``load_json``.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ..pretokenizer import pretokenize

SCHEMA_VERSION = 1


@dataclass
class UnigramModel:
    """Trained unigram vocabulary with log-probabilities."""

    vocab: dict[str, float]

    @property
    def size(self) -> int:
        return len(self.vocab)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, object]:
        return {
            "format_version": SCHEMA_VERSION,
            "model_type": "unigram",
            "vocab": self.vocab,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> UnigramModel:
        version = data.get("format_version")
        if version != SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported format_version {version!r}; expected {SCHEMA_VERSION}"
            )
        model_type = data.get("model_type")
        if model_type != "unigram":
            raise ValueError(f"Expected model_type 'unigram', got {model_type!r}")
        raw_vocab = data.get("vocab")
        if not isinstance(raw_vocab, dict):
            raise ValueError("'vocab' must be a dict")
        vocab: dict[str, float] = {}
        for k, v in raw_vocab.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"Vocab values must be numeric, got {k!r}: {v!r}")
            vocab[k] = float(v)
        return cls(vocab=vocab)

    def save_json(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)

    @classmethod
    def load_json(cls, path: str | Path) -> UnigramModel:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        return cls.from_dict(data)


def _seed_vocab(
    word_freqs: dict[str, int], max_piece_len: int = 8
) -> Counter[str]:
    """Build initial candidate vocabulary from frequent substrings."""
    piece_counts: Counter[str] = Counter()
    for word, freq in word_freqs.items():
        for length in range(1, min(len(word), max_piece_len) + 1):
            for start in range(len(word) - length + 1):
                piece_counts[word[start : start + length]] += freq
    return piece_counts


def _viterbi_segment(word: str, vocab: dict[str, float]) -> list[str]:
    """Segment *word* into pieces using Viterbi best-path over *vocab*.

    Returns the segmentation with the highest sum of log-probabilities.
    """
    n = len(word)
    # best[i] = (best_score, best_length) for word[:i]
    best: list[tuple[float, int]] = [(-math.inf, 0)] * (n + 1)
    best[0] = (0.0, 0)

    for end in range(1, n + 1):
        for start in range(end):
            piece = word[start:end]
            if piece not in vocab:
                continue
            score = best[start][0] + vocab[piece]
            if score > best[end][0]:
                best[end] = (score, end - start)

    if best[n][0] == -math.inf:
        # Fallback: character-level split for unknown words
        return list(word)

    pieces: list[str] = []
    pos = n
    while pos > 0:
        length = best[pos][1]
        pieces.append(word[pos - length : pos])
        pos -= length
    pieces.reverse()
    return pieces


def _compute_loss(word_freqs: dict[str, int], vocab: dict[str, float]) -> float:
    """Total negative log-likelihood of the corpus under *vocab*."""
    total = 0.0
    for word, freq in word_freqs.items():
        pieces = _viterbi_segment(word, vocab)
        for p in pieces:
            total -= freq * vocab.get(p, -100.0)
    return total


class UnigramTrainer:
    """Train a unigram LM vocabulary from a text corpus.

    Args:
        vocab_size: target vocabulary size (must be ≥ 1).
        max_piece_len: maximum substring length for seed vocabulary.
        shrink_factor: fraction of pieces to remove each pruning round.
    """

    def __init__(
        self,
        vocab_size: int,
        *,
        max_piece_len: int = 8,
        shrink_factor: float = 0.25,
    ) -> None:
        if vocab_size < 1:
            raise ValueError(f"vocab_size must be at least 1, got {vocab_size}")
        self.vocab_size = vocab_size
        self.max_piece_len = max_piece_len
        self.shrink_factor = shrink_factor

    def train(self, corpus: Iterable[str]) -> UnigramModel:
        # 1. Collect word frequencies via pretokenizer
        word_counter: Counter[str] = Counter()
        for text in corpus:
            for pretoken in pretokenize(text):
                word_counter[pretoken.word] += 1

        if not word_counter:
            return UnigramModel(vocab={})

        word_freqs = dict(word_counter)

        # 2. Seed vocabulary with frequent substrings
        piece_counts = _seed_vocab(word_freqs, self.max_piece_len)

        # Keep all single characters as required base
        base_chars: set[str] = set()
        for word in word_freqs:
            base_chars.update(word)

        # Assign initial log-probabilities from counts
        total_count = sum(piece_counts.values())
        vocab: dict[str, float] = {
            piece: math.log(count / total_count)
            for piece, count in piece_counts.items()
        }

        # 3. Iteratively prune until target size
        while len(vocab) > self.vocab_size:
            # Compute per-piece loss contribution
            piece_loss: dict[str, float] = {p: 0.0 for p in vocab}
            for word, freq in word_freqs.items():
                pieces = _viterbi_segment(word, vocab)
                for p in pieces:
                    if p in piece_loss:
                        piece_loss[p] += freq * abs(vocab.get(p, -100.0))

            # Sort by loss contribution (ascending) — remove least-useful first
            candidates = sorted(
                ((p, loss) for p, loss in piece_loss.items() if p not in base_chars),
                key=lambda x: x[1],
            )

            n_remove = max(1, int(len(candidates) * self.shrink_factor))
            n_remove = min(n_remove, len(vocab) - self.vocab_size)

            if n_remove <= 0:
                break

            to_remove = {p for p, _ in candidates[:n_remove]}
            vocab = {p: s for p, s in vocab.items() if p not in to_remove}

            # Re-normalize log-probs
            if vocab:
                log_z = math.log(sum(math.exp(s) for s in vocab.values()))
                vocab = {p: s - log_z for p, s in vocab.items()}

        return UnigramModel(vocab=vocab)
