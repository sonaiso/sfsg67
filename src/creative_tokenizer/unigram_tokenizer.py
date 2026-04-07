"""Unigram tokenizer: encode, decode and tokenize with span preservation.

Uses a trained ``UnigramModel`` (from ``trainer.unigram``) to segment text into
subword tokens via Viterbi search.  Reuses the shared ``pretokenizer.py`` layer
and upholds the span contract (``token.text == source[start:end]``).
"""

from __future__ import annotations

import math

from .pretokenizer import pretokenize
from .tokenizer import Token
from .trainer.unigram import UnigramModel


def _viterbi_segment(word: str, vocab: dict[str, float]) -> list[str]:
    """Segment *word* into pieces using Viterbi best-path over *vocab*."""
    n = len(word)
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
        return list(word)

    pieces: list[str] = []
    pos = n
    while pos > 0:
        length = best[pos][1]
        pieces.append(word[pos - length : pos])
        pos -= length
    pieces.reverse()
    return pieces


class UnigramTokenizer:
    """Tokenizer backend using a unigram language model."""

    def __init__(self, model: UnigramModel) -> None:
        self._model = model
        # Build token→id mapping (sorted for deterministic IDs)
        self._token_to_id: dict[str, int] = {
            tok: i for i, tok in enumerate(sorted(model.vocab))
        }
        self._id_to_token: dict[int, str] = {
            i: tok for tok, i in self._token_to_id.items()
        }

    def encode(self, text: str) -> list[int]:
        ids: list[int] = []
        for pretoken in pretokenize(text):
            pieces = _viterbi_segment(pretoken.word, self._model.vocab)
            for piece in pieces:
                token_id = self._token_to_id.get(piece)
                if token_id is not None:
                    ids.append(token_id)
        return ids

    def decode(self, ids: list[int]) -> str:
        return "".join(self._id_to_token.get(i, "") for i in ids)

    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        for pretoken in pretokenize(text):
            pieces = _viterbi_segment(pretoken.word, self._model.vocab)
            char_offset = 0
            for piece in pieces:
                piece_len = len(piece)
                piece_mapping = pretoken.mapping[char_offset : char_offset + piece_len]
                char_offset += piece_len
                if not piece_mapping:
                    continue
                start = piece_mapping[0]
                end = piece_mapping[-1] + 1
                tokens.append(
                    Token(
                        text=text[start:end],
                        normalized=piece,
                        start=start,
                        end=end,
                    )
                )
        return tokens
