"""Tests for the linguistic analysis pipeline — Sprint 2.

Tests verify:
  - analyze_word with known-root verbs (كتب، ذهب، طلب، درس)
  - analyze_word with definite-article prefix stripping (الكتاب)
  - analyze_word with unknown words (returns None for root/pattern/event)
  - LayerResult trace provenance (source_layer, source_identity)
  - LayerResult confidence validation
  - closure: all trace entries have valid layer indices
  - particles / frozen words
"""

import pytest

from creative_tokenizer.linguistics import (
    LayerResult,
    analyze_word,
)
from creative_tokenizer.morphology.event_layer import EventType, Transitivity
from creative_tokenizer.morphology.formal_chain import LayerIndex
from creative_tokenizer.morphology.root_pattern import RootKind

# ── Known trilateral verbs ───────────────────────────────────────────


def test_analyze_kataba_root() -> None:
    result = analyze_word("كتب")
    assert result.root is not None
    assert result.root.consonants == ("ك", "ت", "ب")
    assert result.root.kind == RootKind.TRILATERAL


def test_analyze_kataba_pattern() -> None:
    result = analyze_word("كتب")
    assert result.pattern is not None
    assert result.pattern.template == "فَعَلَ"


def test_analyze_kataba_event() -> None:
    result = analyze_word("كتب")
    assert result.event is not None
    assert result.event.event_type == EventType.ACTION
    assert result.event.transitivity == Transitivity.TRANSITIVE


def test_analyze_dhahaba() -> None:
    result = analyze_word("ذهب")
    assert result.root is not None
    assert result.root.consonants == ("ذ", "ه", "ب")
    assert result.event is not None
    assert result.event.transitivity == Transitivity.INTRANSITIVE


def test_analyze_talaba() -> None:
    result = analyze_word("طلب")
    assert result.root is not None
    assert result.root.consonants == ("ط", "ل", "ب")


def test_analyze_darasa() -> None:
    result = analyze_word("درس")
    assert result.root is not None
    assert result.root.consonants == ("د", "ر", "س")


# ── Definite article prefix stripping ────────────────────────────────


def test_analyze_alkitab() -> None:
    result = analyze_word("الكتاب")
    assert result.root is not None, "Should strip ال and find root for كتاب"
    assert result.root.consonants == ("ك", "ت", "ب")


def test_analyze_altalib() -> None:
    result = analyze_word("الطالب")
    assert result.root is not None
    assert result.root.consonants == ("ط", "ل", "ب")


def test_analyze_aldars() -> None:
    result = analyze_word("الدرس")
    assert result.root is not None
    assert result.root.consonants == ("د", "ر", "س")


# ── Unknown words ────────────────────────────────────────────────────


def test_analyze_unknown_word() -> None:
    result = analyze_word("زبرقلت")  # nonsense word
    assert result.root is None
    assert result.pattern is None
    assert result.event is None
    assert result.confidence == 0.0


def test_analyze_particle() -> None:
    result = analyze_word("في")
    assert result.root is None
    assert result.identity is not None  # still gets a WordIdentity


# ── Trace provenance ─────────────────────────────────────────────────


def test_trace_has_all_layers() -> None:
    result = analyze_word("كتب")
    layers_in_trace = {lr.layer for lr in result.trace}
    assert LayerIndex.UNICODE in layers_in_trace
    assert LayerIndex.GRAPHEME in layers_in_trace
    assert LayerIndex.ROOT_PATTERN in layers_in_trace
    assert LayerIndex.LEXICAL in layers_in_trace
    assert LayerIndex.CLOSED_WORD in layers_in_trace


def test_trace_source_chain() -> None:
    result = analyze_word("كتب")
    # GRAPHEME sources from UNICODE
    grapheme_lr = next(lr for lr in result.trace if lr.layer == LayerIndex.GRAPHEME)
    assert grapheme_lr.source_layer == LayerIndex.UNICODE

    # ROOT_PATTERN sources from GRAPHEME
    root_lr = next(lr for lr in result.trace if lr.layer == LayerIndex.ROOT_PATTERN)
    assert root_lr.source_layer == LayerIndex.GRAPHEME

    # LEXICAL sources from ROOT_PATTERN
    lex_lr = next(lr for lr in result.trace if lr.layer == LayerIndex.LEXICAL)
    assert lex_lr.source_layer == LayerIndex.ROOT_PATTERN


def test_trace_confidence_range() -> None:
    result = analyze_word("كتب")
    for lr in result.trace:
        assert 0.0 <= lr.confidence <= 1.0


# ── LayerResult validation ───────────────────────────────────────────


def test_layer_result_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        LayerResult(
            layer=LayerIndex.UNICODE,
            value="x",
            identity=0,
            source_layer=LayerIndex.UNICODE,
            source_identity=0,
            confidence=1.5,
        )


# ── Graphemes are populated ──────────────────────────────────────────


def test_graphemes_populated() -> None:
    result = analyze_word("كتب")
    assert len(result.graphemes) >= 3
    bases = [g[0] for g in result.graphemes]
    assert "ك" in bases
    assert "ت" in bases
    assert "ب" in bases


# ── Word identity is always present ──────────────────────────────────


def test_identity_always_present() -> None:
    for word in ["كتب", "الكتاب", "زبرقلت", "في", "من"]:
        result = analyze_word(word)
        assert result.identity is not None
        assert isinstance(result.identity.identity, int)


# ── Deterministic ────────────────────────────────────────────────────


def test_deterministic() -> None:
    r1 = analyze_word("كتب")
    r2 = analyze_word("كتب")
    assert r1.identity.identity == r2.identity.identity
    assert r1.confidence == r2.confidence


# ── With diacritics ──────────────────────────────────────────────────


def test_analyze_with_diacritics() -> None:
    result = analyze_word("كَتَبَ")
    assert result.root is not None
    assert result.root.consonants == ("ك", "ت", "ب")


# ── Custom extractor ─────────────────────────────────────────────────


def test_custom_extractor() -> None:
    """analyze_word accepts an external RootExtractor."""
    from creative_tokenizer.morphology.root_pattern import make_root

    class FakeExtractor:
        def extract(self, skeleton: str) -> tuple | None:
            if skeleton == "xyz":
                return (make_root(("x", "y", "z"), RootKind.FROZEN), 0.5)
            return None

    result = analyze_word("xyz", extractor=FakeExtractor())  # type: ignore[arg-type]
    assert result.root is not None
    assert result.root.consonants == ("x", "y", "z")
    assert result.confidence == 0.0  # weakest link (some layers have 0.0)
