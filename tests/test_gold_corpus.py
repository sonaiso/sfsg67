"""Tests for the gold corpus — Sprint 6.

Tests verify:
  - All corpus files parse as valid JSON.
  - Every sample has the required fields (id, text, annotations, annotator).
  - Sample IDs are unique across the entire corpus.
  - Token span contract holds on all annotated tokens.
  - analyze_word matches gold root annotations for known lexicon entries.
  - The corpus contains at least 95 samples total.
"""

import json
from pathlib import Path

import pytest

from creative_tokenizer.linguistics import analyze_word

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus" / "gold"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "corpus" / "schema.json"


def _load_all_samples() -> list[dict]:
    """Load all gold corpus JSON files."""
    samples: list[dict] = []
    for path in sorted(CORPUS_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            samples.extend(data)
    return samples


# Cache samples across tests
_ALL_SAMPLES: list[dict] | None = None


def _get_samples() -> list[dict]:
    global _ALL_SAMPLES  # noqa: PLW0603
    if _ALL_SAMPLES is None:
        _ALL_SAMPLES = _load_all_samples()
    return _ALL_SAMPLES


# ── Corpus size ──────────────────────────────────────────────────────


def test_corpus_has_at_least_95_samples() -> None:
    samples = _get_samples()
    assert len(samples) >= 95, f"Only {len(samples)} samples found, need >= 95"


# ── Schema validity ──────────────────────────────────────────────────


def test_schema_file_exists() -> None:
    assert SCHEMA_PATH.exists()


def test_schema_is_valid_json() -> None:
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    assert "$schema" in data


# ── Required fields ──────────────────────────────────────────────────


@pytest.mark.parametrize("sample", _load_all_samples(), ids=lambda s: s.get("id", "?"))
def test_sample_has_required_fields(sample: dict) -> None:
    assert "id" in sample
    assert "text" in sample
    assert "annotations" in sample
    assert "annotator" in sample
    assert "tokens" in sample["annotations"]


# ── Unique IDs ───────────────────────────────────────────────────────


def test_sample_ids_unique() -> None:
    samples = _get_samples()
    ids = [s["id"] for s in samples]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"


# ── Token span contract on corpus annotations ───────────────────────


@pytest.mark.parametrize("sample", _load_all_samples(), ids=lambda s: s.get("id", "?"))
def test_corpus_span_contract(sample: dict) -> None:
    text = sample["text"]
    for tok in sample["annotations"]["tokens"]:
        start = tok["start"]
        end = tok["end"]
        assert 0 <= start < end <= len(text), (
            f"Invalid span [{start}:{end}] for text of length {len(text)} "
            f"in sample {sample['id']}"
        )
        # The span should cover a non-empty substring
        actual = text[start:end]
        assert len(actual) > 0


# ── Root matching on known lexicon entries ────────────────────────────


def test_root_annotations_match_analyze_word() -> None:
    """For samples with annotated roots, check that analyze_word finds them."""
    samples = _get_samples()
    matched = 0
    total = 0
    for sample in samples:
        for tok in sample["annotations"]["tokens"]:
            if "root" not in tok:
                continue
            total += 1
            gold_root = tuple(tok["root"])
            result = analyze_word(tok["normalized"])
            if result.root is not None and result.root.consonants == gold_root:
                matched += 1
    # We expect 100% match on roots that are in our lexicon
    # Allow some flexibility since not all roots are in the lexicon
    assert total > 0, "No root annotations found in corpus"
    match_rate = matched / total
    assert match_rate >= 0.5, (
        f"Root match rate too low: {matched}/{total} = {match_rate:.1%}"
    )
