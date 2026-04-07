"""Shared enumerations for the Arabic Engine.

SemanticType — ontological categories for concepts (entity, event, …)
DalalType    — dalāla relation kinds (mutabaqa, tadammun, iltizam, isnad, taqyid)
TruthState   — truth-value labels (certain, probable, unknown, false)
GuidanceState — action/guidance labels (obligatory, recommended, … forbidden)

The engine distinguishes truth (existence) judgments, which may be certain (قطعي),
from property/quality judgments, which are revisable (ظني); hence TruthState and
GuidanceState are separate enums.
"""

from __future__ import annotations

from enum import IntEnum

__all__ = ["DalalType", "GuidanceState", "SemanticType", "TruthState"]


class SemanticType(IntEnum):
    """Ontological category of a concept node."""

    ENTITY = 1  # ذات — substance / object
    EVENT = 2  # حدث — action / process
    ATTRIBUTE = 3  # صفة — quality / state
    RELATION = 4  # نسبة — relation between concepts
    NORM = 5  # حكم — normative / evaluative


class DalalType(IntEnum):
    """Kind of dalāla (semantic linkage) between signifier and signified.

    mutabaqa  — full primary denotation (مطابقة)
    tadammun  — partial / entailed component (تضمّن)
    iltizam   — inferential implicature (التزام)
    isnad     — predicative attribution (إسناد)
    taqyid    — restrictive qualification (تقييد)
    ihala     — referential linkage (إحالة)
    """

    MUTABAQA = 1
    TADAMMUN = 2
    ILTIZAM = 3
    ISNAD = 4
    TAQYID = 5
    IHALA = 6


class TruthState(IntEnum):
    """Epistemic truth value of a proposition.

    Judgment on existence may be certain (قطعي); judgment on qualities
    is revisable (ظني).
    """

    CERTAIN = 1  # قطعي — established beyond reasonable doubt
    PROBABLE = 2  # ظني — likely but revisable
    UNKNOWN = 3  # مجهول — no evidence either way
    FALSE = 4  # باطل — contradicted by evidence


class GuidanceState(IntEnum):
    """Action/normative guidance derived from evaluation.

    Separate from truth because a true proposition may or may not
    entail an obligation.
    """

    OBLIGATORY = 1  # واجب
    RECOMMENDED = 2  # مستحب
    PERMISSIBLE = 3  # مباح
    DISLIKED = 4  # مكروه
    FORBIDDEN = 5  # حرام
    NEUTRAL = 6  # لا حكم
