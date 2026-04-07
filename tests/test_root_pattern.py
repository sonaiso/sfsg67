"""Tests for root_pattern.py — root and pattern formal structures."""

import pytest

from creative_tokenizer.morphology.root_pattern import (
    MAZEED_PATTERNS,
    MUJARRAD_PATTERNS,
    NounPatternKind,
    PatternDomain,
    RootKind,
    VerbPatternKind,
    make_noun_pattern,
    make_root,
    make_verb_pattern,
    pattern_id,
    root_id,
)

# ---------------------------------------------------------------------------
# §5  Root tests
# ---------------------------------------------------------------------------


def test_trilateral_root() -> None:
    r = make_root(("ك", "ت", "ب"))
    assert r.kind == RootKind.TRILATERAL
    assert r.consonants == ("ك", "ت", "ب")


def test_quadrilateral_root() -> None:
    r = make_root(("ز", "ل", "ز", "ل"))
    assert r.kind == RootKind.QUADRILATERAL


def test_frozen_root() -> None:
    r = make_root(("ل", "ك"), kind=RootKind.FROZEN)
    assert r.kind == RootKind.FROZEN


def test_inferred_kind_two_consonants() -> None:
    """Two consonants without explicit kind → FROZEN."""
    r = make_root(("م", "ن"))
    assert r.kind == RootKind.FROZEN


def test_trilateral_wrong_count_raises() -> None:
    with pytest.raises(ValueError, match="Trilateral root must have exactly 3"):
        make_root(("ك", "ت"), kind=RootKind.TRILATERAL)


def test_quadrilateral_wrong_count_raises() -> None:
    with pytest.raises(ValueError, match="Quadrilateral root must have exactly 4"):
        make_root(("ك", "ت", "ب"), kind=RootKind.QUADRILATERAL)


def test_root_id_deterministic() -> None:
    r = make_root(("ك", "ت", "ب"))
    assert root_id(r) == root_id(r)


def test_root_id_distinct() -> None:
    r1 = make_root(("ك", "ت", "ب"))
    r2 = make_root(("ذ", "ه", "ب"))
    assert root_id(r1) != root_id(r2)


def test_root_id_order_sensitive() -> None:
    """Root (ك, ت, ب) ≠ (ب, ت, ك)."""
    r1 = make_root(("ك", "ت", "ب"))
    r2 = make_root(("ب", "ت", "ك"))
    assert root_id(r1) != root_id(r2)


def test_root_id_empty_consonants() -> None:
    r = make_root((), kind=RootKind.FROZEN)
    assert root_id(r) == 0


# ---------------------------------------------------------------------------
# §6  Pattern tests
# ---------------------------------------------------------------------------


def test_verb_pattern() -> None:
    pat = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    assert pat.domain == PatternDomain.VERB
    assert pat.sub_kind == int(VerbPatternKind.MUJARRAD)


def test_noun_pattern() -> None:
    pat = make_noun_pattern("مَفْعُول", NounPatternKind.ISM_MAFOUL)
    assert pat.domain == PatternDomain.NOUN
    assert pat.sub_kind == int(NounPatternKind.ISM_MAFOUL)


def test_pattern_id_deterministic() -> None:
    pat = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    assert pattern_id(pat) == pattern_id(pat)


def test_pattern_id_distinct_templates() -> None:
    p1 = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    p2 = make_verb_pattern("فَعِلَ", VerbPatternKind.MUJARRAD)
    assert pattern_id(p1) != pattern_id(p2)


def test_pattern_id_distinct_domains() -> None:
    p1 = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    p2 = make_noun_pattern("فَعَلَ", NounPatternKind.JAMID)
    assert pattern_id(p1) != pattern_id(p2)


def test_mujarrad_patterns_has_three() -> None:
    assert len(MUJARRAD_PATTERNS) == 3


def test_mazeed_patterns_non_empty() -> None:
    assert len(MAZEED_PATTERNS) > 0
