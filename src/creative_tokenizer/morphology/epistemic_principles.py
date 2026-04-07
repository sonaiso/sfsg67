"""Epistemic principles — ten foundational rules governing the upper ontology.

These principles are derived from the epistemological framework that underpins
the twelve-node upper ontology.  They formalise the conditions under which
knowledge formation, signification, and practical guidance are valid.

Each principle receives a stable fractal identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold
from .upper_ontology import NodeIndex

# ═══════════════════════════════════════════════════════════════════════
# §1  Principle index
# ═══════════════════════════════════════════════════════════════════════


class PrincipleIndex(IntEnum):
    """Ten epistemic principles, ordered by the chain they govern."""

    REALITY = 1               # مبدأ الواقع
    SENSE = 2                 # مبدأ الحس
    PRIOR_KNOWLEDGE = 3       # مبدأ المعلومات السابقة
    BINDING = 4               # مبدأ الربط
    INPUT_PURITY = 5          # مبدأ تنقية المدخلات
    JUDGEMENT_GRADATION = 6   # مبدأ تفاضل الأحكام
    CONVENTION = 7            # مبدأ الوضع والدلالة
    UNDERSTANDING_SAFETY = 8  # مبدأ صيانة الفهم
    STANDARD = 9              # مبدأ المعيار
    PRACTICAL_GUIDANCE = 10   # مبدأ الهداية العملية


# ═══════════════════════════════════════════════════════════════════════
# §2  Principle dataclass
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EpistemicPrinciple:
    """A single epistemic principle with bilingual summary."""

    index: PrincipleIndex
    label_ar: str
    label_en: str
    summary_ar: str
    summary_en: str
    governs: tuple[NodeIndex, ...]  # chain nodes this principle governs
    principle_id: int


def _principle_id(idx: PrincipleIndex, governs: tuple[NodeIndex, ...]) -> int:
    gov_fold = (
        fractal_fold([cantor_pair(i + 1, int(n)) for i, n in enumerate(governs)])
        if governs
        else 0
    )
    return cantor_pair(400 + int(idx), gov_fold)


def _ep(
    idx: PrincipleIndex,
    ar: str,
    en: str,
    sum_ar: str,
    sum_en: str,
    governs: tuple[NodeIndex, ...],
) -> EpistemicPrinciple:
    return EpistemicPrinciple(
        index=idx,
        label_ar=ar,
        label_en=en,
        summary_ar=sum_ar,
        summary_en=sum_en,
        governs=governs,
        principle_id=_principle_id(idx, governs),
    )


# ═══════════════════════════════════════════════════════════════════════
# §3  The ten principles
# ═══════════════════════════════════════════════════════════════════════


EPISTEMIC_PRINCIPLES: tuple[EpistemicPrinciple, ...] = (
    _ep(
        PrincipleIndex.REALITY,
        "مبدأ الواقع",
        "Principle of Reality",
        "لا معرفة بلا واقعٍ أو ما يقوم مقام الواقع في جهة الإدراك",
        "No knowledge without reality or what stands in its place for perception",
        (NodeIndex.REALITY,),
    ),
    _ep(
        PrincipleIndex.SENSE,
        "مبدأ الحس",
        "Principle of Sense",
        "الحس شرط للنقل، لا هو نفسه الفكر",
        "Sense is a condition for transfer, not thought itself",
        (NodeIndex.SENSE,),
    ),
    _ep(
        PrincipleIndex.PRIOR_KNOWLEDGE,
        "مبدأ المعلومات السابقة",
        "Principle of Prior Knowledge",
        "لا يكفي الحس وحده؛ فلا بد من معلومات سابقة تُفسَّر بها المدركات",
        "Sense alone is insufficient; prior knowledge is required to interpret percepts",
        (NodeIndex.PRIOR_KNOWLEDGE,),
    ),
    _ep(
        PrincipleIndex.BINDING,
        "مبدأ الربط",
        "Principle of Binding",
        "العقل ربط الواقع المحسوس بالمعلومات السابقة للوصول إلى حكم",
        "The intellect binds perceived reality to prior knowledge to reach judgement",
        (NodeIndex.BINDING,),
    ),
    _ep(
        PrincipleIndex.INPUT_PURITY,
        "مبدأ تنقية المدخلات",
        "Principle of Input Purity",
        "ما ينبغي أن يدخل في الربط هو المعلومات السابقة لا الآراء السابقة",
        "Only prior knowledge — not prior opinion — should enter the binding process",
        (NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING),
    ),
    _ep(
        PrincipleIndex.JUDGEMENT_GRADATION,
        "مبدأ تفاضل الأحكام",
        "Principle of Judgement Gradation",
        "الحكم على الوجود أقوى من الحكم على الحقيقة أو الصفة",
        "Existential judgement is stronger than judgement on essence or attribute",
        (NodeIndex.JUDGEMENT,),
    ),
    _ep(
        PrincipleIndex.CONVENTION,
        "مبدأ الوضع والدلالة",
        "Principle of Convention and Signification",
        "اللغة اصطلاح للتعبير عما في الذهن، والدال لا يساوي الحقيقة الخارجية ضرورةً",
        "Language is a convention expressing mental content; the signifier does not "
        "necessarily equal external reality",
        (NodeIndex.SIGNIFIER, NodeIndex.COMPOSITION, NodeIndex.SIGNIFICATION),
    ),
    _ep(
        PrincipleIndex.UNDERSTANDING_SAFETY,
        "مبدأ صيانة الفهم",
        "Principle of Understanding Safety",
        "ينخرم الفهم إذا لم تُضبط احتمالات اللفظ: اشتراك ومجاز وإضمار وتخصيص ونقل",
        "Understanding breaks down when lexical ambiguity channels — polysemy, metaphor, "
        "ellipsis, specification, and semantic shift — are left unchecked",
        (NodeIndex.SIGNIFICATION,),
    ),
    _ep(
        PrincipleIndex.STANDARD,
        "مبدأ المعيار",
        "Principle of Standard",
        "المعرفة لا تقف عند الفهم بل تتجاوزه إلى التقويم: حق أم باطل",
        "Knowledge does not stop at understanding but proceeds to evaluation: truth or falsehood",
        (NodeIndex.TRUTH_VALUE,),
    ),
    _ep(
        PrincipleIndex.PRACTICAL_GUIDANCE,
        "مبدأ الهداية العملية",
        "Principle of Practical Guidance",
        "المعرفة الصحيحة إما هدى أو ضلال، ثم تثمر فعلًا فرديًا أو جماعيًا",
        "Sound knowledge leads to guidance or misguidance, "
        "then bears individual or collective fruit",
        (NodeIndex.GUIDANCE, NodeIndex.ACTION, NodeIndex.OUTCOME),
    ),
)


def epistemic_principle(idx: PrincipleIndex) -> EpistemicPrinciple:
    """Return the ``EpistemicPrinciple`` for a given index."""
    return EPISTEMIC_PRINCIPLES[int(idx) - 1]


def all_principles() -> tuple[EpistemicPrinciple, ...]:
    """Return the complete ordered tuple of ten principles."""
    return EPISTEMIC_PRINCIPLES
