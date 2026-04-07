"""Tests for augmentation.py — augmentation letter roles and identity."""

import pytest

from creative_tokenizer.morphology.augmentation import (
    AUGMENTATION_LETTERS,
    AugmentRole,
    augmentation_id,
    is_augmentation_letter,
    make_augmentation,
)


def test_ta_is_augmentation_letter() -> None:
    assert is_augmentation_letter(0x062A)  # ت


def test_alif_is_augmentation_letter() -> None:
    assert is_augmentation_letter(0x0627)  # ا


def test_ba_is_not_augmentation() -> None:
    assert not is_augmentation_letter(0x0628)  # ب


def test_augmentation_letters_count() -> None:
    """The mnemonic سألتمونيها has exactly 10 letters."""
    assert len(AUGMENTATION_LETTERS) == 10


def test_make_augmentation() -> None:
    aug = make_augmentation("ت", frozenset({AugmentRole.PATTERN}))
    assert aug.letter == "ت"
    assert AugmentRole.PATTERN in aug.roles
    assert aug.position == 0


def test_make_augmentation_with_position() -> None:
    aug = make_augmentation("ا", frozenset({AugmentRole.DERIVATIONAL}), position=3)
    assert aug.position == 3


def test_make_augmentation_invalid_letter() -> None:
    with pytest.raises(ValueError, match="single character"):
        make_augmentation("تا", frozenset({AugmentRole.PATTERN}))


def test_augmentation_id_deterministic() -> None:
    aug = make_augmentation("ن", frozenset({AugmentRole.INFLECTIONAL}))
    assert augmentation_id(aug) == augmentation_id(aug)


def test_augmentation_id_distinct_roles() -> None:
    a1 = make_augmentation("ت", frozenset({AugmentRole.PATTERN}))
    a2 = make_augmentation("ت", frozenset({AugmentRole.DERIVATIONAL}))
    assert augmentation_id(a1) != augmentation_id(a2)


def test_augmentation_id_distinct_letters() -> None:
    a1 = make_augmentation("ت", frozenset({AugmentRole.PATTERN}))
    a2 = make_augmentation("م", frozenset({AugmentRole.PATTERN}))
    assert augmentation_id(a1) != augmentation_id(a2)


def test_augmentation_id_distinct_positions() -> None:
    a1 = make_augmentation("ت", frozenset({AugmentRole.PATTERN}), position=0)
    a2 = make_augmentation("ت", frozenset({AugmentRole.PATTERN}), position=1)
    assert augmentation_id(a1) != augmentation_id(a2)
