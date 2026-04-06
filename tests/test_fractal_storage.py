import pytest

from creative_tokenizer.morphology.fractal_storage import (
    cantor_pair,
    fractal_fold,
    invert_cantor_pair,
    phi,
)


def test_phi_returns_unicode_codepoint() -> None:
    assert phi("ا") == 0x0627
    assert phi("A") == 65
    assert phi("\n") == 10


def test_phi_rejects_empty_string() -> None:
    with pytest.raises(ValueError):
        phi("")


def test_phi_rejects_multi_char_string() -> None:
    with pytest.raises(ValueError):
        phi("ab")


def test_cantor_pair_zero_zero() -> None:
    assert cantor_pair(0, 0) == 0


def test_cantor_pair_known_values() -> None:
    assert cantor_pair(1, 0) == 1
    assert cantor_pair(0, 1) == 2
    assert cantor_pair(2, 0) == 3
    assert cantor_pair(1, 1) == 4
    assert cantor_pair(0, 2) == 5


def test_cantor_pair_rejects_negative() -> None:
    with pytest.raises(ValueError):
        cantor_pair(-1, 0)
    with pytest.raises(ValueError):
        cantor_pair(0, -1)


def test_cantor_pair_is_injective_on_small_grid() -> None:
    seen: set[int] = set()
    for x in range(30):
        for y in range(30):
            z = cantor_pair(x, y)
            assert z not in seen, f"collision at ({x}, {y})"
            seen.add(z)


def test_invert_cantor_pair_is_inverse() -> None:
    for x in range(20):
        for y in range(20):
            assert invert_cantor_pair(cantor_pair(x, y)) == (x, y)


def test_invert_cantor_pair_rejects_negative() -> None:
    with pytest.raises(ValueError):
        invert_cantor_pair(-1)


def test_fractal_fold_empty_returns_zero() -> None:
    assert fractal_fold([]) == 0


def test_fractal_fold_single_element_is_identity() -> None:
    assert fractal_fold([42]) == 42
    assert fractal_fold([0]) == 0


def test_fractal_fold_two_elements_matches_cantor_pair() -> None:
    assert fractal_fold([3, 7]) == cantor_pair(3, 7)


def test_fractal_fold_is_order_sensitive() -> None:
    assert fractal_fold([1, 2, 3]) != fractal_fold([3, 2, 1])


def test_fractal_fold_distinct_inputs_give_distinct_outputs() -> None:
    outputs = {fractal_fold(list(v)) for v in [(1, 2), (2, 1), (1, 1), (2, 2)]}
    assert len(outputs) == 4
