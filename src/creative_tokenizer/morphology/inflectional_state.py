"""Inflectional state: MABNI / MU'RAB / MIXED.

𝔹(w) = F( π(t_state, b), π(t_carrier, c), π(t_mode, d) )

Fields
------
state       MABNI=1 | MU'RAB=2 | MIXED=3
carrier     what physically carries the inflection marker
mode        how the case/mood manifests
"""
from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

# ── Tags ──────────────────────────────────────────────────────────────


class InflState(IntEnum):
    """حالة البنية الإعرابية."""
    MABNI       = 1  # مبني — fixed form
    MU_RAB      = 2  # معرب — case-inflected
    SEMI_MIXED  = 3  # مختلط (some slots fixed)


class InflCarrier(IntEnum):
    """حامل علامة الإعراب أو البناء."""
    SHORT_VOWEL        = 1   # حركة قصيرة
    ALIF               = 2   # ألف
    WAW                = 3   # واو
    YA                 = 4   # ياء
    NUN                = 5   # نون
    NUN_DELETION       = 6   # حذف نون
    FATHA_FOR_KASRA    = 7   # فتحة بدل كسرة
    SUKUN              = 8   # سكون
    SHADDA             = 9   # شدة
    NONE               = 10  # محذوف / no overt carrier


class InflMode(IntEnum):
    """نمط الإعراب أو البناء."""
    RAF_NASB_JARR      = 1  # يقبل رفع/نصب/جر
    RAF_NASB_JAZM      = 2  # يقبل رفع/نصب/جزم
    MABNI_SUKUN        = 3  # مبني على السكون
    MABNI_FATH         = 4  # مبني على الفتح
    MABNI_DAMM         = 5  # مبني على الضم
    MABNI_KASR         = 6  # مبني على الكسر
    PARTIAL_LETTER     = 7  # بحرف أصيل (الأفعال الخمسة / الأسماء الستة)


# ── Tag constants used inside fractal fold ────────────────────────────
_T_STATE   = 1
_T_CARRIER = 2
_T_MODE    = 3


def inflectional_state_id(
    state: InflState,
    carrier: InflCarrier,
    mode: InflMode,
) -> int:
    """𝔹(w) = F( π(1,b), π(2,c), π(3,d) ).

    The tag prefix (1/2/3) ensures that reordering does not collide.
    """
    return fractal_fold([
        cantor_pair(_T_STATE,   int(state)),
        cantor_pair(_T_CARRIER, int(carrier)),
        cantor_pair(_T_MODE,    int(mode)),
    ])
