"""Iʿrab node: case/mood marker derived from compositional relations.

ℑ(N_i) = F( π(t_case,  c),
             π(t_carrier, k),
             π(t_visibility, v),
             π(t_origin, o),
             π(t_cause, a) )

The node is *generated* by the system from the relation structure, not
pre-stored from a lookup table.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

# ── Enums ─────────────────────────────────────────────────────────────


class IrabCase(IntEnum):
    """حالة الإعراب / البناء."""
    RAF    = 1   # رفع
    NASB   = 2   # نصب
    JARR   = 3   # جر
    JAZM   = 4   # جزم
    MABNI  = 5   # مبني (لا محل له / له محل)


class IrabCarrier(IntEnum):
    """حامل العلامة الإعرابية."""
    DAMMA        = 1
    FATHA        = 2
    KASRA        = 3
    SUKUN        = 4
    ALIF         = 5
    WAW          = 6
    YA           = 7
    NUN_DELETION = 8   # حذف النون
    ESTIMATED    = 9   # مقدر (تعذر / ثقل)
    DELETED      = 10  # محذوف


class IrabVisibility(IntEnum):
    """هل العلامة ظاهرة أم مقدرة؟"""
    OVERT     = 1  # ظاهرة
    ESTIMATED = 2  # مقدرة (للتعذر أو الثقل)
    DELETED   = 3  # محذوفة


class IrabOrigin(IntEnum):
    """هل العلامة أصلية أم فرعية؟"""
    ORIGINAL   = 1  # أصلية
    SECONDARY  = 2  # فرعية (مثل: ممنوع من الصرف)


# ── Dataclass ─────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class IrabNode:
    """A single case/mood assignment derived from compositional structure.

    Attributes
    ----------
    word_index:     position of the governed word in the sequence
    node_id:        ℙ(w) of the word being marked
    case:           IrabCase
    carrier:        IrabCarrier
    visibility:     IrabVisibility
    origin:         IrabOrigin
    cause_relation: identity of the RelationNode that triggered this marking
    identity:       single fractal id for this iʿrab node
    """

    word_index:     int
    node_id:        int
    case:           IrabCase
    carrier:        IrabCarrier
    visibility:     IrabVisibility
    origin:         IrabOrigin
    cause_relation: int   # RelationNode.identity
    identity:       int


# ── Constructor ───────────────────────────────────────────────────────

_T_CASE       = 1
_T_CARRIER    = 2
_T_VISIBILITY = 3
_T_ORIGIN     = 4
_T_CAUSE      = 5
_T_NODE       = 6


def make_irab_node(
    word_index: int,
    node_id: int,
    case: IrabCase,
    carrier: IrabCarrier,
    visibility: IrabVisibility,
    origin: IrabOrigin,
    cause_relation: int,
) -> IrabNode:
    """ℑ(N_i) from the relation that governs N_i."""
    identity = fractal_fold([
        cantor_pair(_T_NODE,       node_id),
        cantor_pair(_T_CASE,       int(case)),
        cantor_pair(_T_CARRIER,    int(carrier)),
        cantor_pair(_T_VISIBILITY, int(visibility)),
        cantor_pair(_T_ORIGIN,     int(origin)),
        cantor_pair(_T_CAUSE,      cause_relation),
    ])
    return IrabNode(
        word_index=word_index,
        node_id=node_id,
        case=case,
        carrier=carrier,
        visibility=visibility,
        origin=origin,
        cause_relation=cause_relation,
        identity=identity,
    )
