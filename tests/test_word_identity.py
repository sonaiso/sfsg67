from creative_tokenizer.morphology.constraint_envelope import ConstraintTag, constraint_envelope
from creative_tokenizer.morphology.lexical_containers import (
    Independence,
    IndependenceGrade,
    LexicalType,
    jamid_carrier,
    operator_carrier,
    root_carrier,
)
from creative_tokenizer.morphology.morph_family import FamilyTag, morph_family_id
from creative_tokenizer.morphology.relation_frame import RoleTag
from creative_tokenizer.morphology.relational_container import (
    PronounTag,
    RelationalType,
    relational_container,
)
from creative_tokenizer.morphology.semantic_envelope import FeatureTag
from creative_tokenizer.morphology.word_identity import WordIdentity, compute_word_identity


def test_compute_word_identity_is_deterministic() -> None:
    carrier = jamid_carrier("شمس")
    a = compute_word_identity("شمس", LexicalType.JAMID, Independence.INDEPENDENT, carrier)
    b = compute_word_identity("شمس", LexicalType.JAMID, Independence.INDEPENDENT, carrier)
    assert a.identity == b.identity


def test_distinct_words_have_distinct_identities() -> None:
    a = compute_word_identity(
        "شمس", LexicalType.JAMID, Independence.INDEPENDENT, jamid_carrier("شمس")
    )
    b = compute_word_identity(
        "قمر", LexicalType.JAMID, Independence.INDEPENDENT, jamid_carrier("قمر")
    )
    assert a.identity != b.identity


def test_lexical_type_affects_identity() -> None:
    a = compute_word_identity(
        "كتب", LexicalType.JAMID, Independence.INDEPENDENT, jamid_carrier("كتب")
    )
    b = compute_word_identity(
        "كتب", LexicalType.ROOT, Independence.INDEPENDENT, root_carrier("كتب")
    )
    assert a.identity != b.identity


def test_independence_flag_affects_identity() -> None:
    carrier = jamid_carrier("شمس")
    a = compute_word_identity("شمس", LexicalType.JAMID, Independence.INDEPENDENT, carrier)
    b = compute_word_identity("شمس", LexicalType.JAMID, Independence.DEPENDENT, carrier)
    assert a.identity != b.identity


def test_features_change_identity() -> None:
    carrier = root_carrier("كتب")
    a = compute_word_identity("كتب", LexicalType.ROOT, Independence.INDEPENDENT, carrier)
    b = compute_word_identity(
        "كتب",
        LexicalType.ROOT,
        Independence.INDEPENDENT,
        carrier,
        features={FeatureTag.TRANSITIVITY: 1},
    )
    assert a.identity != b.identity


def test_roles_change_identity() -> None:
    carrier = root_carrier("ذهب")
    a = compute_word_identity(
        "ذهب",
        LexicalType.ROOT,
        Independence.INDEPENDENT,
        carrier,
        roles={RoleTag.EVENT: 1, RoleTag.AGENT: 1, RoleTag.PATIENT: 0},
    )
    b = compute_word_identity(
        "ذهب",
        LexicalType.ROOT,
        Independence.INDEPENDENT,
        carrier,
        roles={RoleTag.EVENT: 1, RoleTag.AGENT: 1, RoleTag.PATIENT: 1},
    )
    assert a.identity != b.identity


def test_operator_distinct_from_jamid_same_surface() -> None:
    a = compute_word_identity(
        "من", LexicalType.OPERATOR, Independence.DEPENDENT, operator_carrier("من")
    )
    b = compute_word_identity(
        "من", LexicalType.JAMID, Independence.INDEPENDENT, jamid_carrier("من")
    )
    assert a.identity != b.identity


def test_word_identity_is_frozen_and_hashable() -> None:
    carrier = jamid_carrier("نهر")
    wi = compute_word_identity("نهر", LexicalType.JAMID, Independence.INDEPENDENT, carrier)
    assert isinstance(wi, WordIdentity)
    _ = hash(wi)


def test_word_identity_stores_all_components() -> None:
    carrier = root_carrier("كتب")
    features = {FeatureTag.TRANSITIVITY: 1}
    roles = {RoleTag.AGENT: 1, RoleTag.PATIENT: 1}
    wi = compute_word_identity(
        "كتب",
        LexicalType.ROOT,
        Independence.INDEPENDENT,
        carrier,
        features=features,
        roles=roles,
    )
    assert wi.word == "كتب"
    assert wi.lexical_type == LexicalType.ROOT
    assert wi.independence == Independence.INDEPENDENT
    assert wi.carrier_id == carrier
    assert wi.envelope_id != 0
    assert wi.frame_id != 0


def test_semantic_envelope_stable_regardless_of_insertion_order() -> None:
    carrier = root_carrier("كتب")
    features_a = {FeatureTag.TRANSITIVITY: 1, FeatureTag.PASSIVE: 0}
    features_b = {FeatureTag.PASSIVE: 0, FeatureTag.TRANSITIVITY: 1}
    a = compute_word_identity(
        "كتب", LexicalType.ROOT, Independence.INDEPENDENT, carrier, features=features_a
    )
    b = compute_word_identity(
        "كتب", LexicalType.ROOT, Independence.INDEPENDENT, carrier, features=features_b
    )
    assert a.identity == b.identity


# ------------------------------------------------------------------
# New Phase 5 tests: Λ, Ξ, Ω layers and IndependenceGrade
# ------------------------------------------------------------------


def test_family_param_affects_identity() -> None:
    carrier = jamid_carrier("كتاب")
    a = compute_word_identity(
        "كتاب", LexicalType.JAMID, Independence.INDEPENDENT, carrier,
        family=0,
    )
    b = compute_word_identity(
        "كتاب", LexicalType.JAMID, Independence.INDEPENDENT, carrier,
        family=morph_family_id(FamilyTag.DUAL),
    )
    assert a.identity != b.identity


def test_constraints_param_affects_identity() -> None:
    carrier = jamid_carrier("مساجد")
    no_constraint = compute_word_identity(
        "مساجد", LexicalType.JAMID, Independence.INDEPENDENT, carrier,
    )
    diptote = compute_word_identity(
        "مساجد", LexicalType.JAMID, Independence.INDEPENDENT, carrier,
        constraints=constraint_envelope(
            {ConstraintTag.DIPTOTE: 1, ConstraintTag.TANWEEN_BLOCKED: 1}
        ),
    )
    assert no_constraint.identity != diptote.identity


def test_relational_param_affects_identity() -> None:
    carrier = operator_carrier("هو")
    no_rel = compute_word_identity(
        "هو", LexicalType.OPERATOR, Independence.INDEPENDENT, carrier,
    )
    with_rel = compute_word_identity(
        "هو", LexicalType.OPERATOR, Independence.INDEPENDENT, carrier,
        relational=relational_container(
            RelationalType.PRONOUN,
            {int(PronounTag.PERSON): 3, int(PronounTag.GENDER): 1},
        ),
    )
    assert no_rel.identity != with_rel.identity


def test_family_id_stored_in_word_identity() -> None:
    carrier = jamid_carrier("أعلام")
    fid = morph_family_id(FamilyTag.BROKEN_PL)
    wi = compute_word_identity(
        "أعلام", LexicalType.JAMID, Independence.INDEPENDENT, carrier,
        family=fid,
    )
    assert wi.family_id == fid


def test_constraint_id_stored_in_word_identity() -> None:
    carrier = jamid_carrier("مساجد")
    cid = constraint_envelope({ConstraintTag.DIPTOTE: 1, ConstraintTag.TANWEEN_BLOCKED: 1})
    wi = compute_word_identity(
        "مساجد", LexicalType.JAMID, Independence.INDEPENDENT, carrier,
        constraints=cid,
    )
    assert wi.constraint_id == cid


def test_relational_id_stored_in_word_identity() -> None:
    carrier = operator_carrier("أنتم")
    rid = relational_container(
        RelationalType.PRONOUN,
        {int(PronounTag.PERSON): 2, int(PronounTag.NUMBER): 3},
    )
    wi = compute_word_identity(
        "أنتم", LexicalType.OPERATOR, Independence.INDEPENDENT, carrier,
        relational=rid,
    )
    assert wi.relational_id == rid


def test_independence_grade_autonomous_vs_bound_distinct() -> None:
    carrier = jamid_carrier("كتاب")
    bound = compute_word_identity(
        "كتاب", LexicalType.JAMID, IndependenceGrade.BOUND, carrier,
    )
    autonomous = compute_word_identity(
        "كتاب", LexicalType.JAMID, IndependenceGrade.AUTONOMOUS, carrier,
    )
    assert bound.identity != autonomous.identity


def test_independence_grade_four_levels_all_distinct() -> None:
    carrier = jamid_carrier("نهر")
    ids = {
        compute_word_identity(
            "نهر", LexicalType.JAMID, grade, carrier
        ).identity
        for grade in IndependenceGrade
    }
    assert len(ids) == len(IndependenceGrade)


def test_independence_grade_stored_in_word_identity() -> None:
    carrier = jamid_carrier("علم")
    wi = compute_word_identity(
        "علم", LexicalType.JAMID, IndependenceGrade.DERIVED, carrier,
    )
    assert wi.independence == IndependenceGrade.DERIVED


def test_default_new_params_zero_in_word_identity() -> None:
    carrier = jamid_carrier("شمس")
    wi = compute_word_identity("شمس", LexicalType.JAMID, Independence.INDEPENDENT, carrier)
    assert wi.family_id == 0
    assert wi.constraint_id == 0
    assert wi.relational_id == 0
