"""Epistemic engine — executable rules derived from the ten epistemic principles.

Transforms the descriptive principles in
:mod:`~creative_tokenizer.morphology.epistemic_principles` into a rule engine
that can:

* **validate** — check whether the context at a given ontology node
  satisfies all governing principles.
* **can_transition** — decide whether a forward step in the ontology chain
  is epistemically permitted.

Every verdict includes an Arabic ``reason`` so that the system's decisions
are human-auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..morphology.epistemic_principles import PrincipleIndex
from ..morphology.upper_ontology import NodeIndex

__all__ = [
    "EpistemicEngine",
    "EpistemicVerdict",
    "SignificationStatus",
]


# ═══════════════════════════════════════════════════════════════════════
# §1  Verdict and status types
# ═══════════════════════════════════════════════════════════════════════


class SignificationStatus(Enum):
    """Outcome status for signification-level checks."""

    DECIDED = "decided"          # قطعي — single clear meaning
    SUSPENDED = "suspended"      # معلّق — ambiguity unresolved


@dataclass(frozen=True, slots=True)
class EpistemicVerdict:
    """Result of evaluating one epistemic rule."""

    principle_index: PrincipleIndex
    satisfied: bool
    reason: str  # Arabic reason string
    input_snapshot: dict[str, object]


# ═══════════════════════════════════════════════════════════════════════
# §2  Rule definitions  (principle → callable check)
# ═══════════════════════════════════════════════════════════════════════


def _check_reality(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 1: لا معرفة بلا واقع أو بديل حسي."""
    has = bool(ctx.get("has_reality", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.REALITY,
        satisfied=has,
        reason="الواقع موجود أو بديله متحقق" if has else "لا واقع ولا بديل حسي",
        input_snapshot=dict(ctx),
    )


def _check_sense(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 2: الحس شرط النقل لا شرط التفكير."""
    has = bool(ctx.get("has_sense", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.SENSE,
        satisfied=has,
        reason="الحس متحقق — شرط النقل مستوفى" if has else "لا حس — النقل غير ممكن",
        input_snapshot=dict(ctx),
    )


def _check_prior_knowledge(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 3: الحس وحده لا يكفي — لا بد من معلومات سابقة."""
    has = bool(ctx.get("has_prior_knowledge", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.PRIOR_KNOWLEDGE,
        satisfied=has,
        reason="المعلومات السابقة متاحة" if has else "لا معلومات سابقة — التفسير متعذر",
        input_snapshot=dict(ctx),
    )


def _check_binding(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 4: العقل يربط المُدرَك بالمعلومات السابقة."""
    has = bool(ctx.get("has_binding", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.BINDING,
        satisfied=has,
        reason="الربط العقلي متحقق" if has else "لا ربط عقلي — لا حكم",
        input_snapshot=dict(ctx),
    )


def _check_input_purity(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 5: الرأي السابق لا يدخل طبقة التحقق."""
    has_opinion = bool(ctx.get("has_prior_opinion", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.INPUT_PURITY,
        satisfied=not has_opinion,
        reason=(
            "المدخلات نقية — لا رأي مسبق"
            if not has_opinion
            else "رأي مسبق دخل التحقق — النتيجة مشكوك فيها"
        ),
        input_snapshot=dict(ctx),
    )


def _check_judgement_gradation(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 6: الحكم على الوجود أقوى من الحكم على الحقيقة/الصفة."""
    jt = ctx.get("judgement_type", "")
    rank = {"existence": 3, "essence": 2, "attribute": 1}.get(str(jt), 0)
    return EpistemicVerdict(
        principle_index=PrincipleIndex.JUDGEMENT_GRADATION,
        satisfied=rank > 0,
        reason=f"نوع الحكم: {jt} — المرتبة: {rank}" if rank else "نوع الحكم غير محدد",
        input_snapshot=dict(ctx),
    )


def _check_convention(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 7: لا دال معتبر بلا وضع أو قرينة."""
    has = bool(ctx.get("has_convention", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.CONVENTION,
        satisfied=has,
        reason="الوضع أو القرينة متحققة" if has else "لا وضع ولا قرينة — الدال غير معتبر",
        input_snapshot=dict(ctx),
    )


def _check_understanding_safety(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 8: تعدد احتمال الدلالة → معلّق لا مقطوع."""
    count = int(ctx.get("ambiguity_count", 0))  # type: ignore[call-overload]
    if count <= 1:
        satisfied = True
        reason = "الدلالة واحدة — قطعي"
    else:
        satisfied = False
        reason = f"تعدد الدلالة ({count} احتمالات) — الحالة معلّقة لا مقطوعة"
    return EpistemicVerdict(
        principle_index=PrincipleIndex.UNDERSTANDING_SAFETY,
        satisfied=satisfied,
        reason=reason,
        input_snapshot=dict(ctx),
    )


def _check_standard(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 9: لا تقويم بلا معيار حق/باطل."""
    has = bool(ctx.get("has_standard", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.STANDARD,
        satisfied=has,
        reason="المعيار متحقق" if has else "لا معيار — التقويم غير ممكن",
        input_snapshot=dict(ctx),
    )


def _check_practical_guidance(ctx: dict[str, object]) -> EpistemicVerdict:
    """Rule 10: المعرفة السليمة تؤدي إلى هداية ثم عمل ثم ثمرة."""
    has = bool(ctx.get("has_fruit", False))
    return EpistemicVerdict(
        principle_index=PrincipleIndex.PRACTICAL_GUIDANCE,
        satisfied=has,
        reason="الإثمار متحقق — المعرفة مكتملة" if has else "لا إثمار — المعرفة ناقصة",
        input_snapshot=dict(ctx),
    )


# Principle → checker mapping
_RULES: dict[PrincipleIndex, object] = {
    PrincipleIndex.REALITY: _check_reality,
    PrincipleIndex.SENSE: _check_sense,
    PrincipleIndex.PRIOR_KNOWLEDGE: _check_prior_knowledge,
    PrincipleIndex.BINDING: _check_binding,
    PrincipleIndex.INPUT_PURITY: _check_input_purity,
    PrincipleIndex.JUDGEMENT_GRADATION: _check_judgement_gradation,
    PrincipleIndex.CONVENTION: _check_convention,
    PrincipleIndex.UNDERSTANDING_SAFETY: _check_understanding_safety,
    PrincipleIndex.STANDARD: _check_standard,
    PrincipleIndex.PRACTICAL_GUIDANCE: _check_practical_guidance,
}

# Node → governing principles mapping
_NODE_PRINCIPLES: dict[NodeIndex, tuple[PrincipleIndex, ...]] = {
    NodeIndex.REALITY: (PrincipleIndex.REALITY,),
    NodeIndex.SENSE: (PrincipleIndex.SENSE,),
    NodeIndex.PRIOR_KNOWLEDGE: (PrincipleIndex.PRIOR_KNOWLEDGE, PrincipleIndex.INPUT_PURITY),
    NodeIndex.BINDING: (PrincipleIndex.BINDING, PrincipleIndex.INPUT_PURITY),
    NodeIndex.JUDGEMENT: (PrincipleIndex.JUDGEMENT_GRADATION,),
    NodeIndex.SIGNIFIER: (PrincipleIndex.CONVENTION,),
    NodeIndex.COMPOSITION: (PrincipleIndex.CONVENTION,),
    NodeIndex.SIGNIFICATION: (
        PrincipleIndex.CONVENTION,
        PrincipleIndex.UNDERSTANDING_SAFETY,
    ),
    NodeIndex.TRUTH_VALUE: (PrincipleIndex.STANDARD,),
    NodeIndex.GUIDANCE: (PrincipleIndex.STANDARD, PrincipleIndex.PRACTICAL_GUIDANCE),
    NodeIndex.ACTION: (PrincipleIndex.PRACTICAL_GUIDANCE,),
    NodeIndex.OUTCOME: (PrincipleIndex.PRACTICAL_GUIDANCE,),
}

# Transition-specific checks: (source, target) → required principles
_TRANSITION_CHECKS: dict[tuple[NodeIndex, NodeIndex], tuple[PrincipleIndex, ...]] = {
    (NodeIndex.REALITY, NodeIndex.SENSE): (PrincipleIndex.REALITY,),
    (NodeIndex.SENSE, NodeIndex.PRIOR_KNOWLEDGE): (PrincipleIndex.SENSE,),
    (NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING): (
        PrincipleIndex.PRIOR_KNOWLEDGE,
        PrincipleIndex.INPUT_PURITY,
    ),
    (NodeIndex.BINDING, NodeIndex.JUDGEMENT): (PrincipleIndex.BINDING,),
    (NodeIndex.JUDGEMENT, NodeIndex.SIGNIFIER): (PrincipleIndex.JUDGEMENT_GRADATION,),
    (NodeIndex.SIGNIFIER, NodeIndex.COMPOSITION): (PrincipleIndex.CONVENTION,),
    (NodeIndex.COMPOSITION, NodeIndex.SIGNIFICATION): (
        PrincipleIndex.CONVENTION,
        PrincipleIndex.UNDERSTANDING_SAFETY,
    ),
    (NodeIndex.SIGNIFICATION, NodeIndex.TRUTH_VALUE): (PrincipleIndex.STANDARD,),
    (NodeIndex.TRUTH_VALUE, NodeIndex.GUIDANCE): (PrincipleIndex.STANDARD,),
    (NodeIndex.GUIDANCE, NodeIndex.ACTION): (PrincipleIndex.PRACTICAL_GUIDANCE,),
    (NodeIndex.ACTION, NodeIndex.OUTCOME): (PrincipleIndex.PRACTICAL_GUIDANCE,),
}


# ═══════════════════════════════════════════════════════════════════════
# §3  Engine
# ═══════════════════════════════════════════════════════════════════════


class EpistemicEngine:
    """Executable epistemic rule engine.

    Evaluates the ten epistemic principles against a context dict and
    produces auditable :class:`EpistemicVerdict` objects.
    """

    def validate(
        self,
        node_index: NodeIndex,
        context: dict[str, object],
    ) -> list[EpistemicVerdict]:
        """Check all principles governing *node_index* against *context*."""
        principles = _NODE_PRINCIPLES.get(node_index, ())
        verdicts: list[EpistemicVerdict] = []
        for pi in principles:
            checker = _RULES.get(pi)
            if checker is not None:
                verdicts.append(checker(context))  # type: ignore[operator]
        return verdicts

    def can_transition(
        self,
        source: NodeIndex,
        target: NodeIndex,
        context: dict[str, object],
    ) -> tuple[bool, list[EpistemicVerdict]]:
        """Determine whether the transition from *source* → *target* is allowed.

        Returns ``(allowed, verdicts)`` where ``allowed`` is ``True`` only
        if every relevant principle is satisfied.
        """
        principles = _TRANSITION_CHECKS.get((source, target), ())
        verdicts: list[EpistemicVerdict] = []
        for pi in principles:
            checker = _RULES.get(pi)
            if checker is not None:
                verdicts.append(checker(context))  # type: ignore[operator]
        allowed = all(v.satisfied for v in verdicts) if verdicts else True
        return allowed, verdicts

    def signification_status(self, context: dict[str, object]) -> SignificationStatus:
        """Return whether signification is DECIDED or SUSPENDED."""
        count = int(context.get("ambiguity_count", 0))  # type: ignore[call-overload]
        return SignificationStatus.DECIDED if count <= 1 else SignificationStatus.SUSPENDED
