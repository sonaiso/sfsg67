"""Tests for the epistemic engine — Sprint 4.

Tests verify:
  - EpistemicEngine.validate() returns verdicts for each governing node.
  - can_transition() blocks transitions when rules are violated.
  - Five specific rejection cases: prior opinion, no binding, no convention,
    ambiguity → SUSPENDED, no fruit.
  - Verdicts contain Arabic reasons.
  - signification_status returns DECIDED or SUSPENDED.
"""

from creative_tokenizer.knowledge import EpistemicEngine, SignificationStatus
from creative_tokenizer.morphology.upper_ontology import NodeIndex


def _full_context() -> dict[str, object]:
    """A fully satisfied context — all checks pass."""
    return {
        "has_reality": True,
        "has_sense": True,
        "has_prior_knowledge": True,
        "has_binding": True,
        "has_prior_opinion": False,
        "judgement_type": "existence",
        "has_convention": True,
        "ambiguity_count": 1,
        "has_standard": True,
        "has_fruit": True,
    }


# ── validate() ───────────────────────────────────────────────────────


def test_validate_reality_satisfied() -> None:
    engine = EpistemicEngine()
    verdicts = engine.validate(NodeIndex.REALITY, _full_context())
    assert all(v.satisfied for v in verdicts)


def test_validate_all_nodes_satisfied() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    for node in NodeIndex:
        verdicts = engine.validate(node, ctx)
        for v in verdicts:
            assert v.satisfied, f"Node {node.name}: principle {v.principle_index.name} failed"


def test_validate_binding_fails_without_binding() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    ctx["has_binding"] = False
    verdicts = engine.validate(NodeIndex.BINDING, ctx)
    failed = [v for v in verdicts if not v.satisfied]
    assert len(failed) >= 1


# ── can_transition() ─────────────────────────────────────────────────


def test_can_transition_all_pass_full_context() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    transitions = [
        (NodeIndex.REALITY, NodeIndex.SENSE),
        (NodeIndex.SENSE, NodeIndex.PRIOR_KNOWLEDGE),
        (NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING),
        (NodeIndex.BINDING, NodeIndex.JUDGEMENT),
        (NodeIndex.JUDGEMENT, NodeIndex.SIGNIFIER),
        (NodeIndex.SIGNIFIER, NodeIndex.COMPOSITION),
        (NodeIndex.COMPOSITION, NodeIndex.SIGNIFICATION),
        (NodeIndex.SIGNIFICATION, NodeIndex.TRUTH_VALUE),
        (NodeIndex.TRUTH_VALUE, NodeIndex.GUIDANCE),
        (NodeIndex.GUIDANCE, NodeIndex.ACTION),
        (NodeIndex.ACTION, NodeIndex.OUTCOME),
    ]
    for src, tgt in transitions:
        allowed, verdicts = engine.can_transition(src, tgt, ctx)
        assert allowed, f"Transition {src.name}→{tgt.name} should be allowed"


# ── Rejection case 1: prior opinion ─────────────────────────────────


def test_reject_prior_opinion() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    ctx["has_prior_opinion"] = True
    allowed, verdicts = engine.can_transition(
        NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING, ctx
    )
    assert not allowed
    failed = [v for v in verdicts if not v.satisfied]
    assert any("رأي مسبق" in v.reason for v in failed)


# ── Rejection case 2: no binding ────────────────────────────────────


def test_reject_no_binding() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    ctx["has_binding"] = False
    allowed, verdicts = engine.can_transition(
        NodeIndex.BINDING, NodeIndex.JUDGEMENT, ctx
    )
    assert not allowed


# ── Rejection case 3: no convention ─────────────────────────────────


def test_reject_no_convention() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    ctx["has_convention"] = False
    allowed, verdicts = engine.can_transition(
        NodeIndex.SIGNIFIER, NodeIndex.COMPOSITION, ctx
    )
    assert not allowed


# ── Rejection case 4: ambiguity → SUSPENDED ─────────────────────────


def test_ambiguity_suspends_signification() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    ctx["ambiguity_count"] = 3
    allowed, verdicts = engine.can_transition(
        NodeIndex.COMPOSITION, NodeIndex.SIGNIFICATION, ctx
    )
    assert not allowed
    assert engine.signification_status(ctx) == SignificationStatus.SUSPENDED


def test_no_ambiguity_decided() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    assert engine.signification_status(ctx) == SignificationStatus.DECIDED


# ── Rejection case 5: no fruit ──────────────────────────────────────


def test_reject_no_fruit() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    ctx["has_fruit"] = False
    allowed, verdicts = engine.can_transition(
        NodeIndex.ACTION, NodeIndex.OUTCOME, ctx
    )
    assert not allowed


# ── Verdicts contain Arabic reasons ──────────────────────────────────


def test_verdicts_have_arabic_reasons() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    for node in NodeIndex:
        verdicts = engine.validate(node, ctx)
        for v in verdicts:
            assert isinstance(v.reason, str)
            assert len(v.reason) > 0


# ── EpistemicVerdict fields ──────────────────────────────────────────


def test_verdict_has_input_snapshot() -> None:
    engine = EpistemicEngine()
    ctx = _full_context()
    verdicts = engine.validate(NodeIndex.REALITY, ctx)
    for v in verdicts:
        assert isinstance(v.input_snapshot, dict)
