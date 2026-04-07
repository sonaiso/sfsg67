"""Tests for normalization profiles — Sprint 1.2.

Verifies the mapping contract for all three profiles:
  CONSERVATIVE  — only tatweel removed; diacritics + hamza forms preserved.
  STANDARD      — diacritics stripped, hamza/ya/waw/ة→ه unified.
  MORPHOLOGICAL — like STANDARD but ة→ت instead of ة→ه.
"""

from creative_tokenizer.normalization import (
    NormalizationProfile,
    NormalizedText,
    normalize_text,
)


def _assert_mapping(text: str, result: NormalizedText) -> None:
    """Each normalised char must map to a valid index in the original."""
    assert len(result.mapping) == len(result.text)
    for i, idx in enumerate(result.mapping):
        assert 0 <= idx < len(text), (
            f"mapping[{i}]={idx} out of range for original len {len(text)}"
        )


# ── CONSERVATIVE profile ─────────────────────────────────────────────


def test_conservative_keeps_diacritics() -> None:
    text = "كِتَابٌ"
    result = normalize_text(text, NormalizationProfile.CONSERVATIVE)
    assert result.text == "كِتَابٌ"
    _assert_mapping(text, result)


def test_conservative_removes_tatweel() -> None:
    text = "كـــتاب"
    result = normalize_text(text, NormalizationProfile.CONSERVATIVE)
    assert "ـ" not in result.text
    assert result.text == "كتاب"
    _assert_mapping(text, result)


def test_conservative_keeps_hamza_forms() -> None:
    text = "أحمد إبراهيم آسف"
    result = normalize_text(text, NormalizationProfile.CONSERVATIVE)
    assert "أ" in result.text
    assert "إ" in result.text
    assert "آ" in result.text
    _assert_mapping(text, result)


# ── STANDARD profile (default) ───────────────────────────────────────


def test_standard_strips_diacritics() -> None:
    text = "كِتَابٌ"
    result = normalize_text(text, NormalizationProfile.STANDARD)
    assert result.text == "كتاب"
    _assert_mapping(text, result)


def test_standard_unifies_hamza() -> None:
    text = "أحمد إبراهيم آسف"
    result = normalize_text(text, NormalizationProfile.STANDARD)
    # All hamza-bearing alefs → bare alef
    assert "أ" not in result.text
    assert "إ" not in result.text
    assert "آ" not in result.text
    _assert_mapping(text, result)


def test_standard_ta_marbuta_to_ha() -> None:
    text = "مدرسة"
    result = normalize_text(text, NormalizationProfile.STANDARD)
    assert result.text == "مدرسه"
    _assert_mapping(text, result)


def test_standard_is_default() -> None:
    text = "كِتَابٌ"
    default_result = normalize_text(text)
    explicit_result = normalize_text(text, NormalizationProfile.STANDARD)
    assert default_result == explicit_result


# ── MORPHOLOGICAL profile ────────────────────────────────────────────


def test_morphological_ta_marbuta_to_ta() -> None:
    text = "مدرسة"
    result = normalize_text(text, NormalizationProfile.MORPHOLOGICAL)
    assert result.text == "مدرست"
    _assert_mapping(text, result)


def test_morphological_strips_diacritics() -> None:
    text = "كِتَابٌ"
    result = normalize_text(text, NormalizationProfile.MORPHOLOGICAL)
    assert result.text == "كتاب"
    _assert_mapping(text, result)


def test_morphological_unifies_hamza() -> None:
    text = "أحمد"
    result = normalize_text(text, NormalizationProfile.MORPHOLOGICAL)
    assert result.text == "احمد"
    _assert_mapping(text, result)
