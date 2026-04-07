"""Upper ontology — twelve top-level nodes, ten macro layers, eleven
transition relations, eight governing constraints, and a circular chain.

The ontology begins from **reality** (الواقع), not from the sign or from
logic, and ascends through perception, prior knowledge, rational binding,
judgement, signifier, composition, signification, truth/falsehood,
guidance/misguidance, individual/collective action, to outcome/system,
then loops back into prior knowledge as civilisational memory.

Top-level chain
~~~~~~~~~~~~~~~~
::

    واقع → حس → معلومات سابقة/أسماء → ربط عقلي → حكم → دال
    → تركيب/إحالة → دلالة → حق/باطل → هدى/ضلال → فعل → مآل/نظام
    ──────────────────────────────────────────────────── ↩ (feedback)

Transition relations
~~~~~~~~~~~~~~~~~~~~
::

    موضوع → نقل → تفسير → تركيب → إنتاج → تمثيل → إحالة
    → انتقال → تقويم → توجيه → إثمار → إرجاع (feedback)

Macro layers (ten)
~~~~~~~~~~~~~~~~~~
Existence · Perception · Knowledge · Sign · Signification ·
Standard · Direction · Action · Society · Outcome

Each node, layer, transition, and constraint receives a stable fractal
identity via ``cantor_pair`` / ``fractal_fold``, consistent with the
rest of the morphology package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

# ═══════════════════════════════════════════════════════════════════════
# §1  Top-level node index  (twelve nodes)
# ═══════════════════════════════════════════════════════════════════════


class NodeIndex(IntEnum):
    """Ordered position of each upper-ontology node."""

    REALITY = 0         # الواقع
    SENSE = 1           # الحس
    PRIOR_KNOWLEDGE = 2 # المعلومات السابقة / الأسماء
    BINDING = 3         # الربط العقلي
    JUDGEMENT = 4       # الحكم
    SIGNIFIER = 5       # الدال
    COMPOSITION = 6     # التركيب / الإحالة
    SIGNIFICATION = 7   # الدلالة
    TRUTH_VALUE = 8     # الحق / الباطل
    GUIDANCE = 9        # الهدى / الضلال
    ACTION = 10         # الفعل الفردي / الجماعي
    OUTCOME = 11        # المآل / النظام


# ═══════════════════════════════════════════════════════════════════════
# §2  Node dataclass
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class OntologyNode:
    """A single upper-ontology node with bilingual labels."""

    index: NodeIndex
    label_ar: str
    label_en: str
    node_id: int  # stable fractal identity


def _node_id(idx: NodeIndex) -> int:
    # Tag 100 disambiguates upper-ontology nodes from other id spaces.
    return cantor_pair(100, int(idx))


def _node(idx: NodeIndex, ar: str, en: str) -> OntologyNode:
    return OntologyNode(index=idx, label_ar=ar, label_en=en, node_id=_node_id(idx))


UPPER_NODES: tuple[OntologyNode, ...] = (
    _node(NodeIndex.REALITY,         "الواقع",               "Reality"),
    _node(NodeIndex.SENSE,           "الحس",                 "Sense"),
    _node(NodeIndex.PRIOR_KNOWLEDGE, "المعلومات السابقة",     "Prior knowledge / Names"),
    _node(NodeIndex.BINDING,         "الربط العقلي",          "Rational binding"),
    _node(NodeIndex.JUDGEMENT,       "الحكم",                "Judgement"),
    _node(NodeIndex.SIGNIFIER,       "الدال",                "Signifier"),
    _node(NodeIndex.COMPOSITION,     "التركيب / الإحالة",     "Composition / Reference"),
    _node(NodeIndex.SIGNIFICATION,   "الدلالة",              "Signification"),
    _node(NodeIndex.TRUTH_VALUE,     "الحق / الباطل",        "Truth / Falsehood"),
    _node(NodeIndex.GUIDANCE,        "الهدى / الضلال",        "Guidance / Misguidance"),
    _node(NodeIndex.ACTION,          "الفعل",                "Action (individual / collective)"),
    _node(NodeIndex.OUTCOME,         "المآل / النظام",        "Outcome / System"),
)


def upper_node(idx: NodeIndex) -> OntologyNode:
    """Return the ``OntologyNode`` for a given index."""
    return UPPER_NODES[int(idx)]


def all_upper_nodes() -> tuple[OntologyNode, ...]:
    """Return the complete ordered tuple of twelve nodes."""
    return UPPER_NODES


# ═══════════════════════════════════════════════════════════════════════
# §3  Transition relation index  (eleven + feedback)
# ═══════════════════════════════════════════════════════════════════════


class TransitionKind(IntEnum):
    """Kind of transition between consecutive upper-ontology nodes."""

    SUBJECT = 1     # موضوع — Reality is the *subject* of Sense
    TRANSFER = 2    # نقل   — Sense *transfers* to interpretation locus
    INTERPRET = 3   # تفسير — Prior knowledge *interprets* the percept
    SYNTHESISE = 4  # تركيب — Binding *synthesises* percept + knowledge
    PRODUCE = 5     # إنتاج — Judgement *produces* a representation
    REPRESENT = 6   # تمثيل — Signifier *represents* the judgement
    REFER = 7       # إحالة — Composition *refers* to meaning
    TRANSIT = 8     # انتقال — Signification *transits* to standard
    EVALUATE = 9    # تقويم — Truth/Falsehood *evaluates*
    DIRECT = 10     # توجيه — Guidance/Misguidance *directs*
    BEAR_FRUIT = 11 # إثمار — Action *bears fruit* as outcome
    FEEDBACK = 12   # إرجاع — Outcome feeds back into Prior Knowledge


@dataclass(frozen=True, slots=True)
class Transition:
    """A directed edge between two upper-ontology nodes."""

    source: NodeIndex
    target: NodeIndex
    kind: TransitionKind
    label_ar: str
    label_en: str
    transition_id: int


def _transition_id(src: NodeIndex, tgt: NodeIndex, kind: TransitionKind) -> int:
    return fractal_fold([
        cantor_pair(101, int(src)),
        cantor_pair(102, int(tgt)),
        cantor_pair(103, int(kind)),
    ])


def _tr(
    src: NodeIndex,
    tgt: NodeIndex,
    kind: TransitionKind,
    ar: str,
    en: str,
) -> Transition:
    return Transition(
        source=src,
        target=tgt,
        kind=kind,
        label_ar=ar,
        label_en=en,
        transition_id=_transition_id(src, tgt, kind),
    )


_N = NodeIndex
_K = TransitionKind

UPPER_TRANSITIONS: tuple[Transition, ...] = (
    _tr(_N.REALITY, _N.SENSE, _K.SUBJECT, "موضوع", "subject-of"),
    _tr(_N.SENSE, _N.PRIOR_KNOWLEDGE, _K.TRANSFER, "نقل", "transfer"),
    _tr(_N.PRIOR_KNOWLEDGE, _N.BINDING, _K.INTERPRET, "تفسير", "interpret"),
    _tr(_N.BINDING, _N.JUDGEMENT, _K.SYNTHESISE, "تركيب", "synthesise"),
    _tr(_N.JUDGEMENT, _N.SIGNIFIER, _K.PRODUCE, "إنتاج", "produce"),
    _tr(_N.SIGNIFIER, _N.COMPOSITION, _K.REPRESENT, "تمثيل", "represent"),
    _tr(_N.COMPOSITION, _N.SIGNIFICATION, _K.REFER, "إحالة", "refer"),
    _tr(_N.SIGNIFICATION, _N.TRUTH_VALUE, _K.TRANSIT, "انتقال", "transit"),
    _tr(_N.TRUTH_VALUE, _N.GUIDANCE, _K.EVALUATE, "تقويم", "evaluate"),
    _tr(_N.GUIDANCE, _N.ACTION, _K.DIRECT, "توجيه", "direct"),
    _tr(_N.ACTION, _N.OUTCOME, _K.BEAR_FRUIT, "إثمار", "bear-fruit"),
    _tr(_N.OUTCOME, _N.PRIOR_KNOWLEDGE, _K.FEEDBACK, "إرجاع", "feedback"),
)


def all_transitions() -> tuple[Transition, ...]:
    """Return the complete ordered tuple of transitions."""
    return UPPER_TRANSITIONS


def transition_for(kind: TransitionKind) -> Transition:
    """Look up a single transition by its ``TransitionKind``."""
    return UPPER_TRANSITIONS[int(kind) - 1]


# ═══════════════════════════════════════════════════════════════════════
# §4  Macro layer index  (ten layers)
# ═══════════════════════════════════════════════════════════════════════


class MacroLayerIndex(IntEnum):
    """Ten macro layers that group the twelve nodes."""

    EXISTENCE = 0       # طبقة الوجود
    PERCEPTION = 1      # طبقة الإدراك
    KNOWLEDGE = 2       # طبقة المعرفة
    SIGN = 3            # طبقة العلامة
    SIGNIFICATION = 4   # طبقة الدلالة
    STANDARD = 5        # طبقة المعيار
    DIRECTION = 6       # طبقة التوجيه
    ACTION = 7          # طبقة الفعل
    SOCIETY = 8         # طبقة الاجتماع
    OUTCOME = 9         # طبقة المآل


@dataclass(frozen=True, slots=True)
class MacroLayer:
    """A macro layer grouping concepts that serve as values in higher layers."""

    index: MacroLayerIndex
    label_ar: str
    label_en: str
    concepts_ar: tuple[str, ...]
    concepts_en: tuple[str, ...]
    layer_id: int


def _macro_id(idx: MacroLayerIndex, concepts: tuple[str, ...]) -> int:
    concept_fold = (
        fractal_fold([cantor_pair(i + 1, hash(c) % (2**31)) for i, c in enumerate(concepts)])
        if concepts
        else 0
    )
    return cantor_pair(200 + int(idx), concept_fold)


def _layer(
    idx: MacroLayerIndex,
    ar: str,
    en: str,
    concepts_ar: tuple[str, ...],
    concepts_en: tuple[str, ...],
) -> MacroLayer:
    return MacroLayer(
        index=idx,
        label_ar=ar,
        label_en=en,
        concepts_ar=concepts_ar,
        concepts_en=concepts_en,
        layer_id=_macro_id(idx, concepts_en),
    )


MACRO_LAYERS: tuple[MacroLayer, ...] = (
    _layer(
        MacroLayerIndex.EXISTENCE,
        "طبقة الوجود",
        "Existence",
        ("واقع", "ذات", "حدث", "زمان", "مكان", "علاقة"),
        ("reality", "entity", "event", "time", "place", "relation"),
    ),
    _layer(
        MacroLayerIndex.PERCEPTION,
        "طبقة الإدراك",
        "Perception",
        ("حس", "شعور", "انتباه", "نقل", "حضور"),
        ("sense", "feeling", "attention", "transfer", "presence"),
    ),
    _layer(
        MacroLayerIndex.KNOWLEDGE,
        "طبقة المعرفة",
        "Knowledge",
        ("معلومات سابقة", "أسماء", "تصنيف", "تمييز", "ربط", "حكم"),
        ("prior-knowledge", "names", "classification", "distinction", "binding", "judgement"),
    ),
    _layer(
        MacroLayerIndex.SIGN,
        "طبقة العلامة",
        "Sign",
        ("دال", "مدلول", "إحالة", "تركيب", "نسبة"),
        ("signifier", "signified", "reference", "composition", "relation"),
    ),
    _layer(
        MacroLayerIndex.SIGNIFICATION,
        "طبقة الدلالة",
        "Signification",
        ("مطابقة", "تضمن", "التزام", "منطوق", "مفهوم", "خبر", "إنشاء"),
        ("correspondence", "entailment", "implication",
         "explicit", "implicit", "report", "performative"),
    ),
    _layer(
        MacroLayerIndex.STANDARD,
        "طبقة المعيار",
        "Standard",
        ("حق", "باطل", "برهان", "ريب", "يقين", "ظن"),
        ("truth", "falsehood", "proof", "doubt", "certainty", "presumption"),
    ),
    _layer(
        MacroLayerIndex.DIRECTION,
        "طبقة التوجيه",
        "Direction",
        ("هدى", "ضلال", "رشد", "غي", "تقوى", "هوى"),
        ("guidance", "misguidance", "rectitude", "deviance", "piety", "caprice"),
    ),
    _layer(
        MacroLayerIndex.ACTION,
        "طبقة الفعل",
        "Action",
        ("قول", "أمر", "نهي", "اتباع", "ترك", "بناء", "إفساد", "إصلاح"),
        ("speech", "command", "prohibition", "following",
         "abandonment", "building", "corruption", "reform"),
    ),
    _layer(
        MacroLayerIndex.SOCIETY,
        "طبقة الاجتماع",
        "Society",
        ("فرد", "جماعة", "أمة", "ميثاق", "عهد", "تعاون", "شقاق"),
        ("individual", "group", "nation", "covenant", "pact", "cooperation", "schism"),
    ),
    _layer(
        MacroLayerIndex.OUTCOME,
        "طبقة المآل",
        "Outcome",
        ("فلاح", "خسران", "رحمة", "عذاب", "عمران", "خراب"),
        ("success", "loss", "mercy", "punishment", "flourishing", "ruin"),
    ),
)


def macro_layer(idx: MacroLayerIndex) -> MacroLayer:
    """Return the ``MacroLayer`` for a given index."""
    return MACRO_LAYERS[int(idx)]


def all_macro_layers() -> tuple[MacroLayer, ...]:
    """Return the complete ordered tuple of ten layers."""
    return MACRO_LAYERS


# ═══════════════════════════════════════════════════════════════════════
# §5  Governing constraints  (eight rules)
# ═══════════════════════════════════════════════════════════════════════


class ConstraintIndex(IntEnum):
    """Eight epistemic/ontological governing constraints."""

    NO_JUDGEMENT_WITHOUT_BINDING = 1       # لا حكم بلا ربط
    NO_BINDING_WITHOUT_PRIOR = 2           # لا ربط بلا معلومات سابقة
    NO_PRIOR_WITH_OPINION_CONTAMINATION = 3  # لا معلومات نافعة مع الرأي المسبق
    NO_SIGNIFIER_WITHOUT_CONVENTION = 4    # لا دال معتبر بلا وضع أو قرينة
    NO_SIGNIFICATION_WITHOUT_SAFEGUARD = 5 # لا دلالة سليمة مع بقاء الخلل
    NO_EVALUATION_WITHOUT_STANDARD = 6     # لا تقويم بلا معيار حق/باطل
    NO_GUIDANCE_WITHOUT_TRUTH = 7          # لا هدى بلا حق
    NO_KNOWLEDGE_WITHOUT_FRUIT = 8         # لا معرفة كاملة بلا إثمار


@dataclass(frozen=True, slots=True)
class GoverningConstraint:
    """A governing epistemic constraint on the chain."""

    index: ConstraintIndex
    rule_ar: str
    rule_en: str
    antecedent: NodeIndex   # node that must be present / valid
    consequent: NodeIndex   # node that depends on the antecedent
    constraint_id: int


def _constraint_id(idx: ConstraintIndex, ante: NodeIndex, cons: NodeIndex) -> int:
    return fractal_fold([
        cantor_pair(300, int(idx)),
        cantor_pair(301, int(ante)),
        cantor_pair(302, int(cons)),
    ])


def _gc(
    idx: ConstraintIndex,
    ar: str,
    en: str,
    ante: NodeIndex,
    cons: NodeIndex,
) -> GoverningConstraint:
    return GoverningConstraint(
        index=idx,
        rule_ar=ar,
        rule_en=en,
        antecedent=ante,
        consequent=cons,
        constraint_id=_constraint_id(idx, ante, cons),
    )


GOVERNING_CONSTRAINTS: tuple[GoverningConstraint, ...] = (
    _gc(
        ConstraintIndex.NO_JUDGEMENT_WITHOUT_BINDING,
        "لا حكم بلا ربط",
        "No judgement without rational binding",
        NodeIndex.BINDING, NodeIndex.JUDGEMENT,
    ),
    _gc(
        ConstraintIndex.NO_BINDING_WITHOUT_PRIOR,
        "لا ربط بلا معلومات سابقة",
        "No binding without prior knowledge",
        NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING,
    ),
    _gc(
        ConstraintIndex.NO_PRIOR_WITH_OPINION_CONTAMINATION,
        "لا معلومات نافعة إذا اختلطت بالرأي المسبق",
        "Prior knowledge is void when contaminated by prejudgement",
        NodeIndex.PRIOR_KNOWLEDGE, NodeIndex.BINDING,
    ),
    _gc(
        ConstraintIndex.NO_SIGNIFIER_WITHOUT_CONVENTION,
        "لا دال معتبر بلا وضع أو قرينة أو اصطلاح",
        "No valid signifier without convention or contextual cue",
        NodeIndex.SIGNIFIER, NodeIndex.COMPOSITION,
    ),
    _gc(
        ConstraintIndex.NO_SIGNIFICATION_WITHOUT_SAFEGUARD,
        "لا دلالة سليمة مع بقاء أبواب الخلل مفتوحة",
        "No sound signification while ambiguity channels remain open",
        NodeIndex.COMPOSITION, NodeIndex.SIGNIFICATION,
    ),
    _gc(
        ConstraintIndex.NO_EVALUATION_WITHOUT_STANDARD,
        "لا تقويم بلا معيار حق/باطل",
        "No evaluation without a truth/falsehood standard",
        NodeIndex.TRUTH_VALUE, NodeIndex.GUIDANCE,
    ),
    _gc(
        ConstraintIndex.NO_GUIDANCE_WITHOUT_TRUTH,
        "لا هدى بلا حق، ولا ضلال إلا مع انحراف",
        "No guidance without truth; misguidance only with deviation",
        NodeIndex.TRUTH_VALUE, NodeIndex.GUIDANCE,
    ),
    _gc(
        ConstraintIndex.NO_KNOWLEDGE_WITHOUT_FRUIT,
        "لا معرفة كاملة إن بقيت حبيسة الذهن ولم تُثمر",
        "Knowledge is incomplete until it bears practical fruit",
        NodeIndex.ACTION, NodeIndex.OUTCOME,
    ),
)


def governing_constraint(idx: ConstraintIndex) -> GoverningConstraint:
    """Look up a single constraint by its index."""
    return GOVERNING_CONSTRAINTS[int(idx) - 1]


def all_constraints() -> tuple[GoverningConstraint, ...]:
    """Return the complete ordered tuple of eight constraints."""
    return GOVERNING_CONSTRAINTS


# ═══════════════════════════════════════════════════════════════════════
# §6  Chain identity and directionality
# ═══════════════════════════════════════════════════════════════════════


class ChainMode(IntEnum):
    """Traversal direction for the upper-ontology chain."""

    ASCENDING = 1   # واقع → مآل (bottom-up)
    FEEDBACK = 2    # مآل → معلومات سابقة (loop-back)


def chain_identity(mode: ChainMode) -> int:
    """Stable fractal identity for the entire chain in a given mode."""
    if mode == ChainMode.ASCENDING:
        steps = UPPER_TRANSITIONS[:11]  # eleven forward transitions
    else:
        steps = (UPPER_TRANSITIONS[11],)  # feedback edge
    return cantor_pair(
        int(mode),
        fractal_fold([t.transition_id for t in steps]),
    )


def is_circular() -> bool:
    """Return ``True`` — the chain is circular (ascending + feedback)."""
    return UPPER_TRANSITIONS[-1].target == NodeIndex.PRIOR_KNOWLEDGE
