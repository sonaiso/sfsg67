"""Base word class: ISM (noun) / FI'L (verb) / HARF (particle).

𝕹(w) = τ(n)  where  n ∈ {ISM=1, FI'L=2, HARF=3}

This is *not* a redundant copy of LexicalType; it is a coarser gate that
selects the correct contract-function and factor-system for the word.
"""
from __future__ import annotations

from enum import IntEnum


class BaseClass(IntEnum):
    """Coarse grammatical category — governs contract + factor spaces."""

    ISM   = 1  # اسم
    FI_L  = 2  # فعل
    HARF  = 3  # حرف


def base_class_id(bc: BaseClass) -> int:
    """τ(n) = integer value of the BaseClass enum (stable)."""
    return int(bc)
