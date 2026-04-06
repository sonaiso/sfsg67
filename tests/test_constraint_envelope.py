from creative_tokenizer.morphology.constraint_envelope import (
    ConstraintTag,
    constraint_envelope,
)


def test_empty_constraints_returns_zero() -> None:
    assert constraint_envelope({}) == 0


def test_diptote_constraint_nonzero() -> None:
    assert constraint_envelope({ConstraintTag.DIPTOTE: 1}) != 0


def test_different_constraint_sets_give_different_ids() -> None:
    a = constraint_envelope({ConstraintTag.DIPTOTE: 1})
    b = constraint_envelope({ConstraintTag.TANWEEN_BLOCKED: 1})
    assert a != b


def test_constraint_order_does_not_matter() -> None:
    a = constraint_envelope(
        {ConstraintTag.DIPTOTE: 1, ConstraintTag.TANWEEN_BLOCKED: 1}
    )
    b = constraint_envelope(
        {ConstraintTag.TANWEEN_BLOCKED: 1, ConstraintTag.DIPTOTE: 1}
    )
    assert a == b


def test_genitive_by_fatha_distinct_from_tanween_blocked() -> None:
    a = constraint_envelope({ConstraintTag.GENITIVE_BY_FATHA: 1})
    b = constraint_envelope({ConstraintTag.TANWEEN_BLOCKED: 1})
    assert a != b


def test_diptote_bundle_is_distinct() -> None:
    diptote = constraint_envelope(
        {
            ConstraintTag.DIPTOTE: 1,
            ConstraintTag.TANWEEN_BLOCKED: 1,
            ConstraintTag.GENITIVE_BY_FATHA: 1,
        }
    )
    partial = constraint_envelope(
        {ConstraintTag.DIPTOTE: 1, ConstraintTag.TANWEEN_BLOCKED: 1}
    )
    assert diptote != partial


def test_definite_vs_indefinite_is_distinct() -> None:
    def_ = constraint_envelope({ConstraintTag.DEFINITE: 1})
    indef = constraint_envelope({ConstraintTag.DEFINITE: 0})
    assert def_ != indef


def test_declinable_vs_indeclinable_is_distinct() -> None:
    dec = constraint_envelope({ConstraintTag.DECLINABLE: 1})
    ind = constraint_envelope({ConstraintTag.DECLINABLE: 0})
    assert dec != ind


def test_nun_state_distinctions() -> None:
    present = constraint_envelope({ConstraintTag.NUN_STATE: 1})
    deleted = constraint_envelope({ConstraintTag.NUN_STATE: 0})
    assert present != deleted


def test_constraint_is_deterministic() -> None:
    c = {ConstraintTag.DIPTOTE: 1, ConstraintTag.TANWEEN_BLOCKED: 1}
    assert constraint_envelope(c) == constraint_envelope(c)
