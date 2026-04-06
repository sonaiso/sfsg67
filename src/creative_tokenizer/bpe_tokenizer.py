from __future__ import annotations

from .pretokenizer import pretokenize
from .tokenizer import Token
from .trainer.bpe import BpeMerges


def _apply_merges(word: str, merges: list[tuple[str, str]]) -> list[str]:
    pieces = list(word)
    for a, b in merges:
        new_pieces: list[str] = []
        i = 0
        while i < len(pieces):
            if i < len(pieces) - 1 and pieces[i] == a and pieces[i + 1] == b:
                new_pieces.append(a + b)
                i += 2
            else:
                new_pieces.append(pieces[i])
                i += 1
        pieces = new_pieces
    return pieces


class BpeTokenizer:
    def __init__(self, merges: BpeMerges) -> None:
        self._merges = merges

    def encode(self, text: str) -> list[int]:
        ids: list[int] = []
        for pretoken in pretokenize(text):
            pieces = _apply_merges(pretoken.word, self._merges.merges)
            for piece in pieces:
                token_id = self._merges.vocab.get(piece)
                if token_id is not None:
                    ids.append(token_id)
        return ids

    def decode(self, ids: list[int]) -> str:
        id_to_token = {v: k for k, v in self._merges.vocab.items()}
        return "".join(id_to_token.get(i, "") for i in ids)

    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        for pretoken in pretokenize(text):
            pieces = _apply_merges(pretoken.word, self._merges.merges)
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
