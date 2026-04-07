"""Tests for configurable CliticRules — Sprint 1.3.

Verifies:
  - DEFAULT rules reproduce existing hard-coded behaviour.
  - JSON round-trip (save → load).
  - Custom rules change segmentation behaviour.
  - min_stem_length and bidirectional flags work.
  - Schema validation on from_dict.
"""

import pathlib

import pytest

from creative_tokenizer import CliticRules, CreativeTokenizer

# ── DEFAULT rules match existing behaviour ───────────────────────────


def test_default_rules_match_existing_behaviour() -> None:
    text = "وبالكتاب ذهبنا"
    default = CreativeTokenizer(segment_clitics=True)
    explicit = CreativeTokenizer(
        segment_clitics=True, clitic_rules=CliticRules.DEFAULT
    )
    assert [t.to_dict() for t in default.tokenize(text)] == [
        t.to_dict() for t in explicit.tokenize(text)
    ]


# ── JSON round-trip ──────────────────────────────────────────────────


def test_clitic_rules_json_roundtrip(tmp_path: pathlib.Path) -> None:
    rules = CliticRules(
        prefixes=("و", "ف"),
        suffixes=("ها", "ه"),
        min_stem_length=3,
        bidirectional=False,
    )
    path = tmp_path / "rules.json"
    rules.save_json(path)
    loaded = CliticRules.from_json(path)
    assert loaded == rules


def test_clitic_rules_to_dict_from_dict() -> None:
    rules = CliticRules.DEFAULT
    d = rules.to_dict()
    restored = CliticRules.from_dict(d)
    assert restored == rules


# ── Custom rules change behaviour ────────────────────────────────────


def test_custom_prefix_only_rules() -> None:
    # Only strip "و" prefix, no suffixes at all
    rules = CliticRules(prefixes=("و",), suffixes=(), min_stem_length=2)
    tok = CreativeTokenizer(segment_clitics=True, clitic_rules=rules)
    tokens = tok.tokenize("وكتب")
    normalized = [t.normalized for t in tokens]
    assert normalized == ["و", "كتب"]


def test_min_stem_length_prevents_oversegmentation() -> None:
    rules = CliticRules(prefixes=("و", "ف", "ب"), suffixes=(), min_stem_length=4)
    tok = CreativeTokenizer(segment_clitics=True, clitic_rules=rules)
    # "وكتب" stem after stripping "و" is "كتب" (3 chars < min 4), so no split
    tokens = tok.tokenize("وكتب")
    assert [t.normalized for t in tokens] == ["وكتب"]


def test_bidirectional_false_prevents_both_prefix_and_suffix() -> None:
    rules = CliticRules(
        prefixes=("و",),
        suffixes=("ها",),
        min_stem_length=2,
        bidirectional=False,
    )
    tok = CreativeTokenizer(segment_clitics=True, clitic_rules=rules)
    tokens = tok.tokenize("وكتابها")
    normalized = [t.normalized for t in tokens]
    # With bidirectional=False: prefix found → suffix not attempted
    assert normalized == ["و", "كتابها"]


# ── Schema validation on from_dict ───────────────────────────────────


def test_from_dict_rejects_missing_prefixes() -> None:
    with pytest.raises(ValueError, match="prefixes"):
        CliticRules.from_dict({"suffixes": []})


def test_from_dict_rejects_non_list_suffixes() -> None:
    with pytest.raises(ValueError, match="suffixes"):
        CliticRules.from_dict({"prefixes": [], "suffixes": "bad"})


def test_from_dict_rejects_bad_min_stem() -> None:
    with pytest.raises(ValueError, match="min_stem_length"):
        CliticRules.from_dict({"prefixes": [], "suffixes": [], "min_stem_length": 0})
