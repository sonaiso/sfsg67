"""Tests for the vertical slice pipeline — Sprint 5.

Tests verify:
  - Full pipeline on a known sentence produces a complete SliceResult.
  - All stages are populated (normalization, pretokens, word analyses, classification).
  - Epistemic engine does not reject a valid sentence.
  - Ambiguous / unknown input produces a "معلّق" (suspended) classification.
  - Interrogative sentence is classified as "إنشاء".
"""

from creative_tokenizer.knowledge import SignificationStatus, SliceResult, vertical_slice

# ── Complete known sentence ──────────────────────────────────────────


def test_vertical_slice_complete() -> None:
    result = vertical_slice("كَتَبَ الطالبُ الدرسَ")
    assert isinstance(result, SliceResult)
    assert result.raw_text == "كَتَبَ الطالبُ الدرسَ"


def test_vertical_slice_normalization() -> None:
    result = vertical_slice("كَتَبَ الطالبُ الدرسَ")
    # MORPHOLOGICAL normalisation strips diacritics
    assert result.normalized.text == "كتب الطالب الدرس"


def test_vertical_slice_pretokens() -> None:
    result = vertical_slice("كَتَبَ الطالبُ الدرسَ")
    words = [pt.word for pt in result.pretokens]
    assert "كتب" in words
    assert "الطالب" in words
    assert "الدرس" in words


def test_vertical_slice_word_analyses() -> None:
    result = vertical_slice("كَتَبَ الطالبُ الدرسَ")
    assert len(result.word_analyses) >= 3
    # At least the verb should have a root
    roots = [wa.root for wa in result.word_analyses if wa.root is not None]
    assert len(roots) >= 1


def test_vertical_slice_classification_khabar() -> None:
    result = vertical_slice("كَتَبَ الطالبُ الدرسَ")
    assert result.classification.sentence_type == "خبر"


def test_vertical_slice_strength_decided() -> None:
    result = vertical_slice("كتب الطالب الدرس")
    # All words have known roots → should be قطعي
    assert result.classification.strength == "قطعي"


def test_vertical_slice_epistemic_verdicts_present() -> None:
    result = vertical_slice("كتب الطالب الدرس")
    assert len(result.classification.epistemic_verdicts) > 0


def test_vertical_slice_decided_status() -> None:
    result = vertical_slice("كتب الطالب الدرس")
    assert result.classification.signification_status == SignificationStatus.DECIDED


# ── All stages linked ────────────────────────────────────────────────


def test_vertical_slice_all_stages_populated() -> None:
    result = vertical_slice("كتب الطالب")
    assert result.raw_text
    assert result.normalized.text
    assert len(result.pretokens) >= 2
    assert len(result.word_analyses) >= 2
    assert result.classification is not None


# ── Ambiguous / unknown input ────────────────────────────────────────


def test_vertical_slice_unknown_words_suspended() -> None:
    result = vertical_slice("زبرقلت مشنقعات")
    # Unknown words → ambiguity
    assert result.classification.strength == "معلّق"
    assert result.classification.signification_status == SignificationStatus.SUSPENDED


# ── Interrogative → إنشاء ────────────────────────────────────────────


def test_vertical_slice_question_insha() -> None:
    result = vertical_slice("هل كتب الطالب")
    assert result.classification.sentence_type == "إنشاء"


# ── Vocative → إنشاء ────────────────────────────────────────────────


def test_vertical_slice_vocative_insha() -> None:
    result = vertical_slice("يا طالب")
    assert result.classification.sentence_type == "إنشاء"


# ── Simple declarative ───────────────────────────────────────────────


def test_vertical_slice_simple_declarative() -> None:
    result = vertical_slice("ذهب الطالب")
    assert result.classification.sentence_type == "خبر"
    assert result.confidence >= 0.0


# ── Empty input ──────────────────────────────────────────────────────


def test_vertical_slice_empty() -> None:
    result = vertical_slice("")
    assert result.pretokens == ()
    assert result.word_analyses == ()


# ── Confidence is weakest link ───────────────────────────────────────


def test_vertical_slice_confidence() -> None:
    result = vertical_slice("كتب الطالب الدرس")
    # Confidence should be minimum across word analyses
    if result.word_analyses:
        expected = min(wa.confidence for wa in result.word_analyses)
        assert result.confidence == expected
