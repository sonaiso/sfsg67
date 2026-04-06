"""Lexical nature: JAMID / MUSHTAQ / MASDAR / ROOT / OPERATOR / DEICTIC / RELATIVE / COPULAR.

𝕶(w) = τ(k)

This is a finer resolution of LexicalType that drives the contract-function
selector and determines which derived-node types are legal in composition.
"""
from __future__ import annotations

from enum import IntEnum


class LexicalNature(IntEnum):
    """Lexical derivation class of the word form."""
    JAMID     = 1  # جامد
    MUSHTAQ   = 2  # مشتق
    MASDAR    = 3  # مصدر
    ROOT      = 4  # جذر
    OPERATOR  = 5  # حرف / رابط
    DEICTIC   = 6  # إحالي / اسم إشارة
    RELATIVE  = 7  # موصول
    COPULAR   = 8  # ناسخ


def lexical_nature_id(nature: LexicalNature) -> int:
    """τ(k) = integer value (stable)."""
    return int(nature)
