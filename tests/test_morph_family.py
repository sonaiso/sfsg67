from creative_tokenizer.morphology.morph_family import (
    FamilyTag,
    FiveNounTag,
    FiveVerbTag,
    morph_family_id,
)


def test_morph_family_id_is_deterministic() -> None:
    assert morph_family_id(FamilyTag.SIMPLE_NOUN) == morph_family_id(FamilyTag.SIMPLE_NOUN)


def test_each_family_tag_gives_distinct_id() -> None:
    ids = {morph_family_id(tag) for tag in FamilyTag}
    assert len(ids) == len(FamilyTag)


def test_properties_change_identity() -> None:
    base = morph_family_id(FamilyTag.FIVE_VERBS)
    with_props = morph_family_id(
        FamilyTag.FIVE_VERBS,
        {int(FiveVerbTag.PERSON): 3, int(FiveVerbTag.NUMBER): 3},
    )
    assert base != with_props


def test_property_order_does_not_matter() -> None:
    a = morph_family_id(
        FamilyTag.FIVE_VERBS,
        {int(FiveVerbTag.PERSON): 3, int(FiveVerbTag.GENDER): 1},
    )
    b = morph_family_id(
        FamilyTag.FIVE_VERBS,
        {int(FiveVerbTag.GENDER): 1, int(FiveVerbTag.PERSON): 3},
    )
    assert a == b


def test_five_verbs_distinct_from_five_nouns_same_props() -> None:
    props = {1: 2, 2: 3}
    assert morph_family_id(FamilyTag.FIVE_VERBS, props) != morph_family_id(
        FamilyTag.FIVE_NOUNS, props
    )


def test_dual_distinct_from_sound_masc_pl() -> None:
    assert morph_family_id(FamilyTag.DUAL) != morph_family_id(FamilyTag.SOUND_MASC_PL)


def test_diptote_family_distinct_from_indeclinable() -> None:
    assert morph_family_id(FamilyTag.DIPTOTE) != morph_family_id(FamilyTag.INDECLINABLE)


def test_five_noun_case_carriers_give_distinct_ids() -> None:
    waw = morph_family_id(
        FamilyTag.FIVE_NOUNS,
        {int(FiveNounTag.LEXEME_CLASS): 1, int(FiveNounTag.CASE_CARRIER): 1},
    )
    alif = morph_family_id(
        FamilyTag.FIVE_NOUNS,
        {int(FiveNounTag.LEXEME_CLASS): 1, int(FiveNounTag.CASE_CARRIER): 2},
    )
    ya = morph_family_id(
        FamilyTag.FIVE_NOUNS,
        {int(FiveNounTag.LEXEME_CLASS): 1, int(FiveNounTag.CASE_CARRIER): 3},
    )
    assert len({waw, alif, ya}) == 3


def test_five_verb_nun_states_give_distinct_ids() -> None:
    present = morph_family_id(
        FamilyTag.FIVE_VERBS, {int(FiveVerbTag.NUN_STATE): 1}
    )
    deleted = morph_family_id(
        FamilyTag.FIVE_VERBS, {int(FiveVerbTag.NUN_STATE): 0}
    )
    assert present != deleted
