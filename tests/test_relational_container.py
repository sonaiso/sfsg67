from creative_tokenizer.morphology.relational_container import (
    CopularTag,
    DemonstrativeTag,
    PronounTag,
    RelationalType,
    RelativeTag,
    relational_container,
)


def _pronoun(**kwargs: int) -> int:
    return relational_container(RelationalType.PRONOUN, {int(k): v for k, v in kwargs.items()})


def _demo(**kwargs: int) -> int:
    return relational_container(
        RelationalType.DEMONSTRATIVE, {int(k): v for k, v in kwargs.items()}
    )


def _rel(**kwargs: int) -> int:
    return relational_container(
        RelationalType.RELATIVE, {int(k): v for k, v in kwargs.items()}
    )


def _cop(**kwargs: int) -> int:
    return relational_container(
        RelationalType.COPULAR, {int(k): v for k, v in kwargs.items()}
    )


# ------------------------------------------------------------------
# Type discrimination
# ------------------------------------------------------------------


def test_pronoun_distinct_from_demonstrative() -> None:
    p = relational_container(RelationalType.PRONOUN, {})
    d = relational_container(RelationalType.DEMONSTRATIVE, {})
    assert p != d


def test_demonstrative_distinct_from_relative() -> None:
    d = relational_container(RelationalType.DEMONSTRATIVE, {})
    r = relational_container(RelationalType.RELATIVE, {})
    assert d != r


def test_relative_distinct_from_copular() -> None:
    r = relational_container(RelationalType.RELATIVE, {})
    c = relational_container(RelationalType.COPULAR, {})
    assert r != c


def test_all_four_types_are_distinct() -> None:
    ids = {relational_container(t, {}) for t in RelationalType}
    assert len(ids) == len(RelationalType)


def test_same_property_bundle_different_type_gives_different_id() -> None:
    props = {1: 1, 2: 1}
    ids = {relational_container(t, props) for t in RelationalType}
    assert len(ids) == len(RelationalType)


# ------------------------------------------------------------------
# Pronoun
# ------------------------------------------------------------------


def test_pronoun_person_variants_are_distinct() -> None:
    ids = {
        _pronoun(**{str(PronounTag.PERSON): p}) for p in (1, 2, 3)
    }
    assert len(ids) == 3


def test_pronoun_gender_affects_id() -> None:
    m = relational_container(
        RelationalType.PRONOUN,
        {int(PronounTag.PERSON): 3, int(PronounTag.GENDER): 1},
    )
    f = relational_container(
        RelationalType.PRONOUN,
        {int(PronounTag.PERSON): 3, int(PronounTag.GENDER): 2},
    )
    assert m != f


def test_pronoun_attachment_modes_are_distinct() -> None:
    free = relational_container(
        RelationalType.PRONOUN, {int(PronounTag.ATTACHMENT): 0}
    )
    bound = relational_container(
        RelationalType.PRONOUN, {int(PronounTag.ATTACHMENT): 1}
    )
    implicit = relational_container(
        RelationalType.PRONOUN, {int(PronounTag.ATTACHMENT): 2}
    )
    assert len({free, bound, implicit}) == 3


def test_pronoun_closure_requirement_encoded() -> None:
    with_closure = relational_container(
        RelationalType.PRONOUN, {int(PronounTag.CLOSURE): 1}
    )
    without = relational_container(
        RelationalType.PRONOUN, {int(PronounTag.CLOSURE): 0}
    )
    assert with_closure != without


# ------------------------------------------------------------------
# Demonstrative
# ------------------------------------------------------------------


def test_demonstrative_proximal_vs_distal() -> None:
    prox = relational_container(
        RelationalType.DEMONSTRATIVE, {int(DemonstrativeTag.DISTANCE): 0}
    )
    dist = relational_container(
        RelationalType.DEMONSTRATIVE, {int(DemonstrativeTag.DISTANCE): 2}
    )
    assert prox != dist


def test_demonstrative_target_kinds_are_distinct() -> None:
    ids = {
        relational_container(
            RelationalType.DEMONSTRATIVE, {int(DemonstrativeTag.TARGET_KIND): k}
        )
        for k in range(1, 6)
    }
    assert len(ids) == 5


def test_demonstrative_closure_encoded() -> None:
    c = relational_container(
        RelationalType.DEMONSTRATIVE, {int(DemonstrativeTag.CLOSURE): 1}
    )
    assert c != relational_container(RelationalType.DEMONSTRATIVE, {})


# ------------------------------------------------------------------
# Relative
# ------------------------------------------------------------------


def test_relative_requires_sila_encoded() -> None:
    with_sila = relational_container(
        RelationalType.RELATIVE, {int(RelativeTag.REQUIRES_SILA): 1}
    )
    without = relational_container(
        RelationalType.RELATIVE, {int(RelativeTag.REQUIRES_SILA): 0}
    )
    assert with_sila != without


def test_relative_requires_aid_encoded() -> None:
    with_aid = relational_container(
        RelationalType.RELATIVE, {int(RelativeTag.REQUIRES_AID): 1}
    )
    without = relational_container(
        RelationalType.RELATIVE, {int(RelativeTag.REQUIRES_AID): 0}
    )
    assert with_aid != without


def test_relative_specific_vs_generic() -> None:
    specific = relational_container(
        RelationalType.RELATIVE, {int(RelativeTag.SUBTYPE): 1}
    )
    generic = relational_container(
        RelationalType.RELATIVE, {int(RelativeTag.SUBTYPE): 2}
    )
    assert specific != generic


# ------------------------------------------------------------------
# Copular
# ------------------------------------------------------------------


def test_copular_subject_predicate_slots_encoded() -> None:
    with_both = relational_container(
        RelationalType.COPULAR,
        {int(CopularTag.SUBJECT_SLOT): 1, int(CopularTag.PREDICATE_SLOT): 1},
    )
    missing_pred = relational_container(
        RelationalType.COPULAR,
        {int(CopularTag.SUBJECT_SLOT): 1, int(CopularTag.PREDICATE_SLOT): 0},
    )
    assert with_both != missing_pred


def test_copular_effects_are_distinct() -> None:
    effects = {
        relational_container(
            RelationalType.COPULAR, {int(CopularTag.EFFECT): e}
        )
        for e in range(1, 6)
    }
    assert len(effects) == 5


def test_copular_subtypes_are_distinct() -> None:
    ids = {
        relational_container(RelationalType.COPULAR, {int(CopularTag.SUBTYPE): s})
        for s in range(1, 7)
    }
    assert len(ids) == 6


def test_copular_predicative_transform_vs_eventive() -> None:
    eventive = relational_container(
        RelationalType.COPULAR, {int(CopularTag.MODE): 1}
    )
    transform = relational_container(
        RelationalType.COPULAR, {int(CopularTag.MODE): 2}
    )
    assert eventive != transform


# ------------------------------------------------------------------
# Stability
# ------------------------------------------------------------------


def test_relational_container_is_deterministic() -> None:
    props = {int(PronounTag.PERSON): 1, int(PronounTag.NUMBER): 1}
    a = relational_container(RelationalType.PRONOUN, props)
    b = relational_container(RelationalType.PRONOUN, props)
    assert a == b


def test_property_order_does_not_matter() -> None:
    a = relational_container(
        RelationalType.PRONOUN,
        {int(PronounTag.PERSON): 1, int(PronounTag.GENDER): 1},
    )
    b = relational_container(
        RelationalType.PRONOUN,
        {int(PronounTag.GENDER): 1, int(PronounTag.PERSON): 1},
    )
    assert a == b
