"""Corpus-driven evaluation: ground-truth segmentation fixtures.

Each fixture in ``tests/fixtures/corpus_cases.json`` carries an Arabic text
together with expected tokenizer output for both clitic modes.  The span
contract (``token.text == text[token.start:token.end]``) is verified for every
token in every case.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from creative_tokenizer import CreativeTokenizer

_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_CORPUS_FILE = _FIXTURES_DIR / "corpus_cases.json"


def _load_cases() -> list[dict[str, object]]:
    return json.loads(_CORPUS_FILE.read_text(encoding="utf-8"))  # type: ignore[return-value]


_CASES = _load_cases()


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])  # type: ignore[index]
def test_no_clitics_normalized_tokens(case: dict[str, object]) -> None:
    text = str(case["text"])
    expected = case["expected_no_clitics"]  # type: ignore[index]
    tokenizer = CreativeTokenizer(segment_clitics=False)
    tokens = tokenizer.tokenize(text)
    assert [t.normalized for t in tokens] == expected["normalized"]  # type: ignore[index]


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])  # type: ignore[index]
def test_with_clitics_normalized_tokens(case: dict[str, object]) -> None:
    text = str(case["text"])
    expected = case["expected_with_clitics"]  # type: ignore[index]
    tokenizer = CreativeTokenizer(segment_clitics=True)
    tokens = tokenizer.tokenize(text)
    assert [t.normalized for t in tokens] == expected["normalized"]  # type: ignore[index]


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])  # type: ignore[index]
def test_span_contract_no_clitics(case: dict[str, object]) -> None:
    text = str(case["text"])
    tokenizer = CreativeTokenizer(segment_clitics=False)
    tokens = tokenizer.tokenize(text)
    for token in tokens:
        assert token.text == text[token.start : token.end], (
            f"span mismatch for {token!r}"
        )


@pytest.mark.parametrize("case", _CASES, ids=[c["id"] for c in _CASES])  # type: ignore[index]
def test_span_contract_with_clitics(case: dict[str, object]) -> None:
    text = str(case["text"])
    tokenizer = CreativeTokenizer(segment_clitics=True)
    tokens = tokenizer.tokenize(text)
    for token in tokens:
        assert token.text == text[token.start : token.end], (
            f"span mismatch for {token!r}"
        )
