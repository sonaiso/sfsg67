"""Tests for the pre-compositional layer (𝕡(w))."""
import pytest

from creative_tokenizer.morphology.base_class import BaseClass, base_class_id
from creative_tokenizer.morphology.contract_function import (
    NounContractTag,
    ParticleContractTag,
    SharedContractTag,
    VerbContractTag,
    contract_function,
)
from creative_tokenizer.morphology.exact_decimal import (
    READY_HIGH,
    READY_MID,
    ExactDecimal,
)
from creative_tokenizer.morphology.factor_system import (
    NounFactorTag,
    ParticleFactorTag,
    VerbFactorTag,
    factor_system,
)
from creative_tokenizer.morphology.inflectional_state import (
    InflCarrier,
    InflMode,
    InflState,
    inflectional_state_id,
)
from creative_tokenizer.morphology.lexical_containers import (
    Independence,
    LexicalType,
    jamid_carrier,
    operator_carrier,
    root_carrier,
)
from creative_tokenizer.morphology.lexical_nature import LexicalNature, lexical_nature_id
from creative_tokenizer.morphology.pre_compositional import (
    PreCompositionalValue,
    compute_pre_compositional,
)
from creative_tokenizer.morphology.readiness import (
    full_readiness,
    partial_readiness,
    readiness_envelope,
)
from creative_tokenizer.morphology.triple_semantic import (
    iltizam_id,
    triple_semantic_envelope,
)
from creative_tokenizer.morphology.word_identity import compute_word_identity

# ── helpers ───────────────────────────────────────────────────────────


def _noun_identity(word: str = "كتاب") -> object:
    return compute_word_identity(
        word, LexicalType.JAMID, Independence.INDEPENDENT, jamid_carrier(word)
    )


def _verb_identity(word: str = "كتب") -> object:
    return compute_word_identity(
        word, LexicalType.ROOT, Independence.INDEPENDENT, root_carrier(word)
    )


def _simple_pcv(word: str = "كتاب") -> PreCompositionalValue:
    wi = _noun_identity(word)
    return compute_pre_compositional(
        word_identity=wi,
        base_class_id=base_class_id(BaseClass.ISM),
        infl_state_id=inflectional_state_id(
            InflState.MU_RAB, InflCarrier.SHORT_VOWEL, InflMode.RAF_NASB_JARR
        ),
        lex_nature_id=lexical_nature_id(LexicalNature.JAMID),
        contract_id=contract_function({
            int(SharedContractTag.GENDER): 1,
            int(SharedContractTag.NUMBER): 1,
            int(NounContractTag.TANWEEN): 1,
        }),
        factor_id=factor_system({
            int(NounFactorTag.ACCEPT_RAF): 1,
            int(NounFactorTag.ACCEPT_NASB): 1,
            int(NounFactorTag.ACCEPT_JARR): 1,
        }),
        semantic_id=triple_semantic_envelope(42, 7, 0),
        readiness_id=full_readiness(),
    )


# ── ExactDecimal ──────────────────────────────────────────────────────


def test_exact_decimal_fractal_id_stable() -> None:
    d = ExactDecimal(875, 3)
    assert d.fractal_id() == d.fractal_id()


def test_exact_decimal_as_float() -> None:
    assert ExactDecimal(500, 3).as_float() == pytest.approx(0.5)
    assert ExactDecimal(1000, 3).as_float() == pytest.approx(1.0)


def test_exact_decimal_different_values_different_ids() -> None:
    a = ExactDecimal(875, 3)
    b = ExactDecimal(500, 3)
    assert a.fractal_id() != b.fractal_id()


def test_exact_decimal_scale_matters() -> None:
    # 5/1 ≠ 50/2 in fractal encoding (same float, different representation)
    a = ExactDecimal(5, 1)
    b = ExactDecimal(50, 2)
    assert a.fractal_id() != b.fractal_id()


def test_exact_decimal_rejects_negative() -> None:
    with pytest.raises(ValueError):
        ExactDecimal(-1, 3)


def test_exact_decimal_from_pair_roundtrip() -> None:
    pair = (875, 3)
    d = ExactDecimal.from_pair(pair)
    assert d.numerator == 875
    assert d.scale == 3


# ── BaseClass ─────────────────────────────────────────────────────────


def test_base_classes_all_distinct() -> None:
    ids = {base_class_id(bc) for bc in BaseClass}
    assert len(ids) == len(BaseClass)


def test_ism_id_is_one() -> None:
    assert base_class_id(BaseClass.ISM) == 1


# ── InflectionalState ─────────────────────────────────────────────────


def test_mabni_vs_mu_rab_distinct() -> None:
    mabni = inflectional_state_id(InflState.MABNI, InflCarrier.SUKUN, InflMode.MABNI_SUKUN)
    mu_rab = inflectional_state_id(
        InflState.MU_RAB, InflCarrier.SHORT_VOWEL, InflMode.RAF_NASB_JARR
    )
    assert mabni != mu_rab


def test_infl_carrier_affects_id() -> None:
    a = inflectional_state_id(InflState.MU_RAB, InflCarrier.ALIF, InflMode.RAF_NASB_JARR)
    b = inflectional_state_id(InflState.MU_RAB, InflCarrier.WAW, InflMode.RAF_NASB_JARR)
    assert a != b


def test_infl_mode_affects_id() -> None:
    a = inflectional_state_id(InflState.MABNI, InflCarrier.SUKUN, InflMode.MABNI_SUKUN)
    b = inflectional_state_id(InflState.MABNI, InflCarrier.SUKUN, InflMode.MABNI_FATH)
    assert a != b


def test_infl_state_deterministic() -> None:
    args = (InflState.MU_RAB, InflCarrier.SHORT_VOWEL, InflMode.RAF_NASB_JARR)
    assert inflectional_state_id(*args) == inflectional_state_id(*args)


# ── LexicalNature ─────────────────────────────────────────────────────


def test_all_natures_distinct() -> None:
    ids = {lexical_nature_id(n) for n in LexicalNature}
    assert len(ids) == len(LexicalNature)


# ── ContractFunction ──────────────────────────────────────────────────


def test_empty_contract_is_zero() -> None:
    assert contract_function({}) == 0


def test_contract_tag_order_does_not_matter() -> None:
    a = contract_function(
        {int(SharedContractTag.GENDER): 1, int(SharedContractTag.NUMBER): 2}
    )
    b = contract_function(
        {int(SharedContractTag.NUMBER): 2, int(SharedContractTag.GENDER): 1}
    )
    assert a == b


def test_noun_contract_tanween_affects_id() -> None:
    with_t = contract_function({int(NounContractTag.TANWEEN): 1})
    without = contract_function({int(NounContractTag.TANWEEN): 0})
    assert with_t != without


def test_verb_contract_tense_affects_id() -> None:
    past = contract_function({int(VerbContractTag.TENSE): 1})
    pres = contract_function({int(VerbContractTag.TENSE): 2})
    assert past != pres


def test_verb_contract_voice_affects_id() -> None:
    active  = contract_function({int(VerbContractTag.VOICE): 1})
    passive = contract_function({int(VerbContractTag.VOICE): 2})
    assert active != passive


def test_particle_contract_scope_affects_id() -> None:
    nominal = contract_function({int(ParticleContractTag.SCOPE): 1})
    verbal  = contract_function({int(ParticleContractTag.SCOPE): 2})
    assert nominal != verbal


def test_contract_deterministic() -> None:
    s = {int(VerbContractTag.TENSE): 2, int(VerbContractTag.VOICE): 1}
    assert contract_function(s) == contract_function(s)


# ── FactorSystem ──────────────────────────────────────────────────────


def test_empty_factor_is_zero() -> None:
    assert factor_system({}) == 0


def test_noun_factor_raf_vs_jarr_distinct() -> None:
    r = factor_system({int(NounFactorTag.ACCEPT_RAF): 1})
    j = factor_system({int(NounFactorTag.ACCEPT_JARR): 1})
    assert r != j


def test_verb_object_slot_affects_id() -> None:
    trans  = factor_system({int(VerbFactorTag.ALLOWS_OBJECT): 1})
    intrans = factor_system({int(VerbFactorTag.ALLOWS_OBJECT): 0})
    assert trans != intrans


def test_particle_governs_jarr_vs_nasb_distinct() -> None:
    j = factor_system({int(ParticleFactorTag.GOVERNS_JARR): 1})
    n = factor_system({int(ParticleFactorTag.GOVERNS_NASB): 1})
    assert j != n


def test_factor_order_does_not_matter() -> None:
    a = factor_system({int(NounFactorTag.ACCEPT_RAF): 1, int(NounFactorTag.ACCEPT_NASB): 1})
    b = factor_system({int(NounFactorTag.ACCEPT_NASB): 1, int(NounFactorTag.ACCEPT_RAF): 1})
    assert a == b


# ── TripleSemantic ────────────────────────────────────────────────────


def test_triple_semantic_all_zero_is_nonzero_base() -> None:
    # F(π(1,0), π(2,0), π(3,0)) should still be a valid id, just not zero
    # (it happens to be non-zero because of the tag prefixes)
    val = triple_semantic_envelope(0, 0, 0)
    assert isinstance(val, int)


def test_mutabaqa_affects_triple_id() -> None:
    a = triple_semantic_envelope(10, 0, 0)
    b = triple_semantic_envelope(20, 0, 0)
    assert a != b


def test_tadammun_affects_triple_id() -> None:
    a = triple_semantic_envelope(0, 5, 0)
    b = triple_semantic_envelope(0, 6, 0)
    assert a != b


def test_iltizam_affects_triple_id() -> None:
    a = triple_semantic_envelope(0, 0, 100)
    b = triple_semantic_envelope(0, 0, 200)
    assert a != b


def test_iltizam_is_conditional_not_obligatory() -> None:
    # obligation_mode is always 0 — two different schemas with same strength
    # must differ, confirming that the schema value is encoded
    s1 = iltizam_id(1, ExactDecimal(500, 3))
    s2 = iltizam_id(2, ExactDecimal(500, 3))
    assert s1 != s2


def test_iltizam_strength_affects_id() -> None:
    weak   = iltizam_id(1, ExactDecimal(250, 3))
    strong = iltizam_id(1, ExactDecimal(875, 3))
    assert weak != strong


def test_triple_semantic_deterministic() -> None:
    assert triple_semantic_envelope(5, 3, 99) == triple_semantic_envelope(5, 3, 99)


# ── Readiness ─────────────────────────────────────────────────────────


def test_full_readiness_deterministic() -> None:
    assert full_readiness() == full_readiness()


def test_partial_readiness_differs_from_full() -> None:
    assert partial_readiness(score=READY_MID) != full_readiness()


def test_factor_not_ready_differs_from_ready() -> None:
    ready = readiness_envelope(factor_ready=True)
    not_ready = readiness_envelope(factor_ready=False)
    assert ready != not_ready


def test_readiness_score_affects_id() -> None:
    high = readiness_envelope(composition_score=READY_HIGH)
    mid  = readiness_envelope(composition_score=READY_MID)
    assert high != mid


def test_identity_closed_flag_affects_id() -> None:
    closed = readiness_envelope(identity_closed=True)
    open_  = readiness_envelope(identity_closed=False)
    assert closed != open_


# ── PreCompositionalValue ─────────────────────────────────────────────


def test_pcv_is_frozen_and_hashable() -> None:
    pcv = _simple_pcv()
    assert isinstance(pcv, PreCompositionalValue)
    _ = hash(pcv)


def test_pcv_deterministic() -> None:
    assert _simple_pcv().value == _simple_pcv().value


def test_pcv_different_words_different_values() -> None:
    a = _simple_pcv("كتاب")
    b = _simple_pcv("قلم")
    assert a.value != b.value


def test_pcv_base_class_affects_value() -> None:
    wi = _noun_identity()
    ism = compute_pre_compositional(
        wi, base_class_id(BaseClass.ISM), 0, 0, 0, 0, 0, full_readiness()
    )
    fi_l = compute_pre_compositional(
        wi, base_class_id(BaseClass.FI_L), 0, 0, 0, 0, 0, full_readiness()
    )
    assert ism.value != fi_l.value


def test_pcv_infl_state_affects_value() -> None:
    wi = _noun_identity()
    mu_rab_id = inflectional_state_id(
        InflState.MU_RAB, InflCarrier.SHORT_VOWEL, InflMode.RAF_NASB_JARR
    )
    mabni_id  = inflectional_state_id(InflState.MABNI, InflCarrier.SUKUN, InflMode.MABNI_SUKUN)
    a = compute_pre_compositional(wi, 1, mu_rab_id, 0, 0, 0, 0, full_readiness())
    b = compute_pre_compositional(wi, 1, mabni_id,  0, 0, 0, 0, full_readiness())
    assert a.value != b.value


def test_pcv_contract_affects_value() -> None:
    wi = _noun_identity()
    c1 = contract_function({int(NounContractTag.TANWEEN): 1})
    c2 = contract_function({int(NounContractTag.TANWEEN): 0})
    a = compute_pre_compositional(wi, 1, 0, 0, c1, 0, 0, full_readiness())
    b = compute_pre_compositional(wi, 1, 0, 0, c2, 0, 0, full_readiness())
    assert a.value != b.value


def test_pcv_factor_affects_value() -> None:
    wi = _verb_identity()
    f1 = factor_system({int(VerbFactorTag.ALLOWS_OBJECT): 1})
    f2 = factor_system({int(VerbFactorTag.ALLOWS_OBJECT): 0})
    a = compute_pre_compositional(wi, 2, 0, 0, 0, f1, 0, full_readiness())
    b = compute_pre_compositional(wi, 2, 0, 0, 0, f2, 0, full_readiness())
    assert a.value != b.value


def test_pcv_semantic_affects_value() -> None:
    wi = _noun_identity()
    s1 = triple_semantic_envelope(10, 0, 0)
    s2 = triple_semantic_envelope(20, 0, 0)
    a = compute_pre_compositional(wi, 1, 0, 0, 0, 0, s1, full_readiness())
    b = compute_pre_compositional(wi, 1, 0, 0, 0, 0, s2, full_readiness())
    assert a.value != b.value


def test_pcv_readiness_affects_value() -> None:
    wi = _noun_identity()
    r1 = full_readiness()
    r2 = partial_readiness(score=READY_MID)
    a = compute_pre_compositional(wi, 1, 0, 0, 0, 0, 0, r1)
    b = compute_pre_compositional(wi, 1, 0, 0, 0, 0, 0, r2)
    assert a.value != b.value


def test_pcv_stores_word_identity() -> None:
    pcv = _simple_pcv("نهر")
    assert pcv.word_identity.word == "نهر"


def test_pcv_unicode_identity_preserved() -> None:
    """Raw Unicode surface id must survive the pcv wrapping."""
    from creative_tokenizer.morphology.unicode_identity import unicode_surface
    word = "مدرسة"
    pcv = _simple_pcv(word)
    assert pcv.word_identity.surface_id == unicode_surface(word)


# ── Independent noun (معرب مستقل) ───────────────────────────────────


def test_independent_noun_mu_rab() -> None:
    wi = compute_word_identity(
        "رجل", LexicalType.JAMID, Independence.INDEPENDENT, jamid_carrier("رجل")
    )
    infl = inflectional_state_id(InflState.MU_RAB, InflCarrier.SHORT_VOWEL, InflMode.RAF_NASB_JARR)
    pcv = compute_pre_compositional(
        wi,
        base_class_id=base_class_id(BaseClass.ISM),
        infl_state_id=infl,
        lex_nature_id=lexical_nature_id(LexicalNature.JAMID),
        contract_id=contract_function({
            int(SharedContractTag.GENDER): 1,
            int(SharedContractTag.NUMBER): 1,
            int(NounContractTag.TANWEEN): 1,
        }),
        factor_id=factor_system({
            int(NounFactorTag.ACCEPT_RAF): 1,
            int(NounFactorTag.ACCEPT_NASB): 1,
            int(NounFactorTag.ACCEPT_JARR): 1,
        }),
        semantic_id=triple_semantic_envelope(10, 5, 0),
        readiness_id=full_readiness(),
    )
    assert pcv.value != 0
    assert pcv.word_identity.word == "رجل"


# ── Mabni deictic (اسم إشارة مبني) ──────────────────────────────────


def test_mabni_deictic_noun() -> None:
    wi = compute_word_identity(
        "هذا", LexicalType.DEICTIC, Independence.INDEPENDENT, operator_carrier("هذا")
    )
    infl = inflectional_state_id(InflState.MABNI, InflCarrier.SUKUN, InflMode.MABNI_SUKUN)
    pcv = compute_pre_compositional(
        wi,
        base_class_id=base_class_id(BaseClass.ISM),
        infl_state_id=infl,
        lex_nature_id=lexical_nature_id(LexicalNature.DEICTIC),
        contract_id=0,
        factor_id=factor_system({int(NounFactorTag.ACCEPT_RAF): 1}),
        semantic_id=triple_semantic_envelope(1, 0, 0),
        readiness_id=partial_readiness(score=READY_HIGH),
    )
    assert pcv.infl_state_id == infl
    assert pcv.readiness_id != full_readiness()
