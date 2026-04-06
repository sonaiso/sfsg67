"""Tests for the compositional layer (ℛ, ℑ, Σ, MinClose)."""
from creative_tokenizer.morphology.compositional_context import make_context
from creative_tokenizer.morphology.exact_decimal import READY_FULL, READY_MID
from creative_tokenizer.morphology.irab_node import (
    IrabCarrier,
    IrabCase,
    IrabOrigin,
    IrabVisibility,
    make_irab_node,
)
from creative_tokenizer.morphology.lexical_containers import (
    Independence,
    LexicalType,
    jamid_carrier,
    operator_carrier,
    root_carrier,
)
from creative_tokenizer.morphology.minimal_closure import derive_nodes, minimal_closure
from creative_tokenizer.morphology.relation_nodes import (
    DerivedType,
    ReferenceMode,
    RelationType,
    make_derived_node,
    make_reference_node,
    make_relation_node,
)
from creative_tokenizer.morphology.sentence_node import make_sentence_node
from creative_tokenizer.morphology.word_identity import compute_word_identity

# ── Helpers ───────────────────────────────────────────────────────────


def _pcv_int(word: str, lt: LexicalType = LexicalType.JAMID) -> int:
    """Return a pre-compositional stand-in (word_identity.identity) for testing."""
    if lt == LexicalType.ROOT:
        c = root_carrier(word)
    elif lt in (LexicalType.OPERATOR, LexicalType.DEICTIC):
        c = operator_carrier(word)
    else:
        c = jamid_carrier(word)
    return compute_word_identity(word, lt, Independence.INDEPENDENT, c).identity


# ── CompositionalContext ──────────────────────────────────────────────


def test_context_no_neighbours() -> None:
    ctx = make_context(42)
    assert ctx.node_id == 42
    assert ctx.left_id == 0
    assert ctx.right_id == 0


def test_context_deterministic() -> None:
    ctx1 = make_context(10, left_id=5, right_id=7)
    ctx2 = make_context(10, left_id=5, right_id=7)
    assert ctx1.context_id == ctx2.context_id


def test_context_different_neighbours_different_id() -> None:
    a = make_context(10, left_id=5, right_id=7)
    b = make_context(10, left_id=5, right_id=8)
    assert a.context_id != b.context_id


def test_context_position_matters() -> None:
    # left=A right=0  vs  left=0 right=A  should differ
    a = make_context(10, left_id=99, right_id=0)
    b = make_context(10, left_id=0, right_id=99)
    assert a.context_id != b.context_id


# ── RelationNode ──────────────────────────────────────────────────────


def test_relation_node_deterministic() -> None:
    v = _pcv_int("ذهب", LexicalType.ROOT)
    n = _pcv_int("محمد")
    r1 = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    r2 = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    assert r1.identity == r2.identity


def test_relation_type_affects_identity() -> None:
    v = _pcv_int("ذهب", LexicalType.ROOT)
    n = _pcv_int("محمد")
    isnad  = make_relation_node(RelationType.ISNAD,  0, 1, v, n)
    taqyid = make_relation_node(RelationType.TAQYID, 0, 1, v, n)
    assert isnad.identity != taqyid.identity


def test_relation_node_order_matters() -> None:
    a = _pcv_int("كتب", LexicalType.ROOT)
    b = _pcv_int("طالب")
    ab = make_relation_node(RelationType.ISNAD, 0, 1, a, b)
    ba = make_relation_node(RelationType.ISNAD, 0, 1, b, a)
    assert ab.identity != ba.identity


def test_economy_affects_relation_identity() -> None:
    a = _pcv_int("كتب", LexicalType.ROOT)
    b = _pcv_int("زيد")
    r1 = make_relation_node(RelationType.ISNAD, 0, 1, a, b, economy=READY_FULL)
    r2 = make_relation_node(RelationType.ISNAD, 0, 1, a, b, economy=READY_MID)
    assert r1.identity != r2.identity


def test_context_affects_relation_identity() -> None:
    a = _pcv_int("رجع", LexicalType.ROOT)
    b = _pcv_int("سعيد")
    r1 = make_relation_node(RelationType.ISNAD, 0, 1, a, b, left_ctx=100)
    r2 = make_relation_node(RelationType.ISNAD, 0, 1, a, b, left_ctx=200)
    assert r1.identity != r2.identity


# ── DerivedNode ───────────────────────────────────────────────────────


def test_fai_liyya_derived_node_deterministic() -> None:
    v = _pcv_int("ذهب", LexicalType.ROOT)
    n = _pcv_int("عمر")
    rel = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    d1 = make_derived_node(DerivedType.FAI_LIYYA, v, n, rel.identity)
    d2 = make_derived_node(DerivedType.FAI_LIYYA, v, n, rel.identity)
    assert d1.identity == d2.identity


def test_fai_liyya_vs_maf_uliyya_distinct() -> None:
    v = _pcv_int("ضرب", LexicalType.ROOT)
    n = _pcv_int("زيد")
    rel = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    fa  = make_derived_node(DerivedType.FAI_LIYYA,  v, n, rel.identity)
    maf = make_derived_node(DerivedType.MAF_ULIYYA, v, n, rel.identity)
    assert fa.identity != maf.identity


def test_sababiyya_vs_musabbabiyya_distinct() -> None:
    c = _pcv_int("أسقط", LexicalType.ROOT)
    e = _pcv_int("المطر")
    rel = make_relation_node(RelationType.ISNAD, 0, 1, c, e)
    sab  = make_derived_node(DerivedType.SABABIYYA,     c, e, rel.identity)
    mus  = make_derived_node(DerivedType.MUSABBABIYYA,  c, e, rel.identity)
    assert sab.identity != mus.identity


# ── ReferenceNode ─────────────────────────────────────────────────────


def test_explicit_vs_implicit_reference_distinct() -> None:
    src = _pcv_int("هو", LexicalType.DEICTIC)
    tgt = _pcv_int("محمد")
    exp = make_reference_node(ReferenceMode.EXPLICIT, src, tgt)
    imp = make_reference_node(ReferenceMode.IMPLICIT, src, tgt)
    assert exp.identity != imp.identity


def test_reference_mode_relative_distinct() -> None:
    src = _pcv_int("الذي", LexicalType.DEICTIC)
    tgt = _pcv_int("رجل")
    rel = make_reference_node(ReferenceMode.RELATIVE, src, tgt)
    exp = make_reference_node(ReferenceMode.EXPLICIT, src, tgt)
    assert rel.identity != exp.identity


def test_reference_sentence_mode() -> None:
    s1 = _pcv_int("جاء", LexicalType.ROOT)
    s2 = _pcv_int("فضحك", LexicalType.ROOT)
    ref = make_reference_node(ReferenceMode.SENTENCE, s1, s2)
    assert ref.identity != 0


def test_reference_distance_affects_identity() -> None:
    src = _pcv_int("هم", LexicalType.DEICTIC)
    tgt = _pcv_int("الطلاب")
    near = make_reference_node(ReferenceMode.EXPLICIT, src, tgt, distance=READY_FULL)
    far  = make_reference_node(ReferenceMode.EXPLICIT, src, tgt, distance=READY_MID)
    assert near.identity != far.identity


def test_reference_node_deterministic() -> None:
    src = _pcv_int("هو", LexicalType.DEICTIC)
    tgt = _pcv_int("أحمد")
    r1 = make_reference_node(ReferenceMode.EXPLICIT, src, tgt)
    r2 = make_reference_node(ReferenceMode.EXPLICIT, src, tgt)
    assert r1.identity == r2.identity


# ── IrabNode ──────────────────────────────────────────────────────────


def test_irab_case_affects_identity() -> None:
    node_id = _pcv_int("طالب")
    rel_id  = 999
    raf  = make_irab_node(
        1, node_id, IrabCase.RAF,  IrabCarrier.DAMMA,
        IrabVisibility.OVERT, IrabOrigin.ORIGINAL, rel_id,
    )
    nasb = make_irab_node(
        1, node_id, IrabCase.NASB, IrabCarrier.FATHA,
        IrabVisibility.OVERT, IrabOrigin.ORIGINAL, rel_id,
    )
    jarr = make_irab_node(
        1, node_id, IrabCase.JARR, IrabCarrier.KASRA,
        IrabVisibility.OVERT, IrabOrigin.ORIGINAL, rel_id,
    )
    assert len({raf.identity, nasb.identity, jarr.identity}) == 3


def test_irab_visibility_overt_vs_estimated_distinct() -> None:
    node_id = _pcv_int("مستشفى")
    overt = make_irab_node(
        0, node_id, IrabCase.RAF, IrabCarrier.ESTIMATED,
        IrabVisibility.OVERT, IrabOrigin.ORIGINAL, 0
    )
    est   = make_irab_node(
        0, node_id, IrabCase.RAF, IrabCarrier.ESTIMATED,
        IrabVisibility.ESTIMATED, IrabOrigin.ORIGINAL, 0
    )
    assert overt.identity != est.identity


def test_irab_origin_original_vs_secondary_distinct() -> None:
    node_id = _pcv_int("مساجد")
    orig = make_irab_node(
        0, node_id, IrabCase.JARR, IrabCarrier.FATHA,
        IrabVisibility.OVERT, IrabOrigin.ORIGINAL, 0
    )
    sec  = make_irab_node(
        0, node_id, IrabCase.JARR, IrabCarrier.FATHA,
        IrabVisibility.OVERT, IrabOrigin.SECONDARY, 0
    )
    assert orig.identity != sec.identity


def test_irab_jazm_with_nun_deletion() -> None:
    # Afaal khamsa: jazm by nun deletion
    node_id = _pcv_int("يذهبون", LexicalType.ROOT)
    irab = make_irab_node(
        0, node_id, IrabCase.JAZM, IrabCarrier.NUN_DELETION,
        IrabVisibility.DELETED, IrabOrigin.SECONDARY, 0
    )
    assert irab.case == IrabCase.JAZM
    assert irab.carrier == IrabCarrier.NUN_DELETION


def test_irab_deterministic() -> None:
    node_id = _pcv_int("البيت")
    args = (
        0, node_id, IrabCase.RAF, IrabCarrier.DAMMA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, 0
    )
    assert make_irab_node(*args).identity == make_irab_node(*args).identity


# ── MinimalClosure ────────────────────────────────────────────────────


def test_minimal_closure_selects_nearest() -> None:
    v  = _pcv_int("ذهب", LexicalType.ROOT)
    n1 = _pcv_int("محمد")
    n2 = _pcv_int("زيد")
    # Both candidates fill slot 0 (left_index=0), but n1 is nearer (right=1 vs right=3)
    r_near = make_relation_node(RelationType.ISNAD, 0, 1, v, n1)
    r_far  = make_relation_node(RelationType.ISNAD, 0, 3, v, n2)
    selected, cost = minimal_closure([r_far, r_near], obligatory_left_indices={0})
    assert len(selected) == 1
    assert selected[0].right_index == 1  # nearer was chosen


def test_minimal_closure_fills_obligatory_slot() -> None:
    v = _pcv_int("قرأ", LexicalType.ROOT)
    n = _pcv_int("الطالب")
    r = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    selected, _ = minimal_closure([r], obligatory_left_indices={0})
    assert len(selected) == 1


def test_minimal_closure_unfilled_slot_increases_cost() -> None:
    v = _pcv_int("جلس", LexicalType.ROOT)
    n = _pcv_int("علي")
    # One candidate for slot 0, nothing for slot 1
    r = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    _, cost_with_unfilled = minimal_closure([r], obligatory_left_indices={0, 1})
    _, cost_filled        = minimal_closure([r], obligatory_left_indices={0})
    assert cost_with_unfilled > cost_filled


def test_minimal_closure_no_candidates_no_cost_if_no_slots() -> None:
    selected, cost = minimal_closure([], obligatory_left_indices=None)
    assert selected == []
    assert cost == 0


def test_derive_nodes_from_isnad_gives_fai_liyya() -> None:
    v = _pcv_int("علّم", LexicalType.ROOT)
    n = _pcv_int("المعلم")
    rel = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    derived = derive_nodes([rel])
    assert len(derived) == 1
    assert derived[0].derived_type == DerivedType.FAI_LIYYA


def test_derive_nodes_taqyid_gives_no_derived() -> None:
    a = _pcv_int("رجل")
    b = _pcv_int("كريم")
    rel = make_relation_node(RelationType.TAQYID, 0, 1, a, b)
    derived = derive_nodes([rel])
    assert derived == []


# ── SentenceNode ──────────────────────────────────────────────────────


def test_sentence_node_deterministic() -> None:
    v = _pcv_int("جاء", LexicalType.ROOT)
    n = _pcv_int("الرجل")
    rel  = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    irab = make_irab_node(
        1, n, IrabCase.RAF, IrabCarrier.DAMMA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, rel.identity
    )
    s1   = make_sentence_node(v, [rel], [irab])
    s2   = make_sentence_node(v, [rel], [irab])
    assert s1.identity == s2.identity


def test_sentence_node_irab_affects_identity() -> None:
    v  = _pcv_int("جلس", LexicalType.ROOT)
    n  = _pcv_int("أحمد")
    rel = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    raf  = make_irab_node(
        1, n, IrabCase.RAF,  IrabCarrier.DAMMA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, rel.identity
    )
    nasb = make_irab_node(
        1, n, IrabCase.NASB, IrabCarrier.FATHA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, rel.identity
    )
    s1 = make_sentence_node(v, [rel], [raf])
    s2 = make_sentence_node(v, [rel], [nasb])
    assert s1.identity != s2.identity


def test_sentence_node_with_reference() -> None:
    v   = _pcv_int("رجع", LexicalType.ROOT)
    pro = _pcv_int("هو", LexicalType.DEICTIC)
    ref = make_reference_node(ReferenceMode.IMPLICIT, pro, v)
    rel = make_relation_node(RelationType.ISNAD, 0, 1, v, pro)
    irab = make_irab_node(
        1, pro, IrabCase.RAF, IrabCarrier.ESTIMATED,
        IrabVisibility.ESTIMATED, IrabOrigin.ORIGINAL, rel.identity
    )
    s = make_sentence_node(v, [rel], [irab], references=[ref])
    assert s.identity != 0


def test_sentence_stores_derived_nodes() -> None:
    v = _pcv_int("ضرب", LexicalType.ROOT)
    n = _pcv_int("زيد")
    rel = make_relation_node(RelationType.ISNAD, 0, 1, v, n)
    drv = make_derived_node(DerivedType.FAI_LIYYA, v, n, rel.identity)
    irab = make_irab_node(
        1, n, IrabCase.RAF, IrabCarrier.DAMMA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, rel.identity
    )
    s = make_sentence_node(v, [rel], [irab], derived=[drv])
    assert len(s.derived) == 1
    assert s.derived[0].derived_type == DerivedType.FAI_LIYYA


# ── Arabic end-to-end scenarios ───────────────────────────────────────


def test_nasikh_ism_khabar_construction() -> None:
    """كان + اسم كان + خبر كان: two ISNAD-like slots."""
    kana = _pcv_int("كان", LexicalType.COPULAR)
    ism  = _pcv_int("الطالب")
    khbr = _pcv_int("مجتهدًا")
    r_ism  = make_relation_node(RelationType.ISNAD, 0, 1, kana, ism,  economy=READY_FULL)
    r_khbr = make_relation_node(RelationType.ISNAD, 0, 2, kana, khbr, economy=READY_FULL)
    selected, _ = minimal_closure([r_ism, r_khbr], obligatory_left_indices={0})
    # Both are obligatory for the same head (kana), but economy picks nearest
    assert len(selected) >= 1


def test_idafa_taqyid_construction() -> None:
    """كتاب + الطالب — idafa (تقييد إضافي)."""
    head = _pcv_int("كتاب")
    dep  = _pcv_int("الطالب")
    rel  = make_relation_node(RelationType.TAQYID, 0, 1, head, dep)
    assert rel.rel_type == RelationType.TAQYID


def test_full_verb_sentence_fai_liyya_and_irab() -> None:
    """ذهب محمد — generate fai'liyya + raf irab."""
    v  = _pcv_int("ذهب", LexicalType.ROOT)
    n  = _pcv_int("محمد")
    rel = make_relation_node(RelationType.ISNAD, 0, 1, v, n, economy=READY_FULL)
    irab = make_irab_node(
        1, n, IrabCase.RAF, IrabCarrier.DAMMA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, rel.identity
    )
    derived = derive_nodes([rel])
    s = make_sentence_node(v, [rel], [irab], derived=derived)
    assert s.head_id == v
    assert s.irab_nodes[0].case == IrabCase.RAF
    assert s.derived[0].derived_type == DerivedType.FAI_LIYYA


def test_transitive_verb_maf_uliyya() -> None:
    """ضرب زيدٌ عمرًا — explicit maf'uliyya node."""
    v    = _pcv_int("ضرب", LexicalType.ROOT)
    fa   = _pcv_int("زيد")
    maf  = _pcv_int("عمرو")
    rel_fa  = make_relation_node(RelationType.ISNAD, 0, 1, v, fa)
    rel_maf = make_relation_node(RelationType.ISNAD, 0, 2, v, maf)
    drv_fa  = make_derived_node(DerivedType.FAI_LIYYA,  v, fa,  rel_fa.identity)
    drv_maf = make_derived_node(DerivedType.MAF_ULIYYA, v, maf, rel_maf.identity)
    irab_fa  = make_irab_node(
        1, fa,  IrabCase.RAF,  IrabCarrier.DAMMA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, rel_fa.identity
    )
    irab_maf = make_irab_node(
        2, maf, IrabCase.NASB, IrabCarrier.FATHA, IrabVisibility.OVERT,
        IrabOrigin.ORIGINAL, rel_maf.identity
    )
    s = make_sentence_node(v, [rel_fa, rel_maf], [irab_fa, irab_maf], derived=[drv_fa, drv_maf])
    assert len(s.derived) == 2


def test_economy_prevents_relation_explosion() -> None:
    """With 5 nodes, only relevant relations pass minimal_closure."""
    ids = [_pcv_int(w) for w in ["يحب", "محمد", "المعلم", "الكتاب", "القديم"]]
    candidates: list = []
    # Generate all possible ISNAD candidates
    for i in range(len(ids)):
        for j in range(len(ids)):
            if i != j:
                candidates.append(
                    make_relation_node(RelationType.ISNAD, i, j, ids[i], ids[j])
                )
    # Only slot 0 (head verb) is obligatory
    selected, _ = minimal_closure(candidates, obligatory_left_indices={0})
    # Greedy: exactly 1 relation closes slot 0
    assert len(selected) == 1
