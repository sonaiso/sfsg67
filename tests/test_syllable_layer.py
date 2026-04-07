"""Tests for syllable_layer.py — syllable shapes, building, and identity."""

import pytest

from creative_tokenizer.morphology.syllable_layer import (
    SyllableShape,
    build_syllable,
    detect_shape,
    syllable_id,
)

_FATHA = "\u064e"
_KASRA = "\u0650"
_DAMMA = "\u064f"
_SUKUN = "\u0652"


# ---------------------------------------------------------------------------
# Shape detection
# ---------------------------------------------------------------------------


def test_cv_shape() -> None:
    """كَ → CV."""
    clusters = (("ك", (_FATHA,)),)
    assert detect_shape(clusters) == SyllableShape.CV


def test_cvc_shape() -> None:
    """كَتْ → CVC  (ka + t with sukun)."""
    clusters = (("ك", (_FATHA,)), ("ت", (_SUKUN,)))
    assert detect_shape(clusters) == SyllableShape.CVC


def test_cvc_shape_no_sukun() -> None:
    """Two consonant clusters: first with short vowel, second bare → CVC."""
    clusters = (("ك", (_FATHA,)), ("ت", ()))
    assert detect_shape(clusters) == SyllableShape.CVC


def test_cvv_shape() -> None:
    """كَا → CVV  (ka + alif)."""
    clusters = (("ك", (_FATHA,)), ("ا", ()))
    assert detect_shape(clusters) == SyllableShape.CVV


def test_cvvc_shape() -> None:
    """كَاتْ → CVVC  (ka + alif + t)."""
    clusters = (("ك", (_FATHA,)), ("ا", ()), ("ت", ()))
    assert detect_shape(clusters) == SyllableShape.CVVC


def test_cvcc_shape() -> None:
    """كَتْبْ → CVCC  (ka + t + b)."""
    clusters = (("ك", (_FATHA,)), ("ت", ()), ("ب", ()))
    assert detect_shape(clusters) == SyllableShape.CVCC


def test_empty_returns_none() -> None:
    assert detect_shape(()) is None


def test_invalid_shape_returns_none() -> None:
    # Four consonant clusters → no canonical shape
    clusters = (("ك", (_FATHA,)), ("ت", ()), ("ب", ()), ("ر", ()))
    assert detect_shape(clusters) is None


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------


def test_build_syllable_cv() -> None:
    clusters = (("ك", (_FATHA,)),)
    syl = build_syllable(clusters)
    assert syl.shape == SyllableShape.CV
    assert syl.position == 0
    assert syl.clusters == clusters


def test_build_syllable_with_position() -> None:
    clusters = (("ت", (_DAMMA,)),)
    syl = build_syllable(clusters, position=2)
    assert syl.position == 2


def test_build_syllable_invalid_raises() -> None:
    with pytest.raises(ValueError, match="does not form a valid syllable"):
        build_syllable(())


# ---------------------------------------------------------------------------
# Fractal identity
# ---------------------------------------------------------------------------


def test_syllable_id_deterministic() -> None:
    clusters = (("ك", (_FATHA,)),)
    syl = build_syllable(clusters)
    assert syllable_id(syl) == syllable_id(syl)


def test_syllable_id_distinct_shapes() -> None:
    cv = build_syllable((("ك", (_FATHA,)),))
    cvc = build_syllable((("ك", (_FATHA,)), ("ت", ())))
    assert syllable_id(cv) != syllable_id(cvc)


def test_syllable_id_distinct_content() -> None:
    s1 = build_syllable((("ك", (_FATHA,)),))
    s2 = build_syllable((("ب", (_FATHA,)),))
    assert syllable_id(s1) != syllable_id(s2)


def test_syllable_id_distinct_diacritics() -> None:
    s1 = build_syllable((("ك", (_FATHA,)),))
    s2 = build_syllable((("ك", (_KASRA,)),))
    assert syllable_id(s1) != syllable_id(s2)
