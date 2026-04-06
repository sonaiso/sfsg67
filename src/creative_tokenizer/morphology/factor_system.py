"""Factor system (عوامل نحوية): slots a word can *accept* or *emit*.

𝔸(w) = F( π(a1,v1), … )

Three distinct tag-enums: noun / verb / particle.
"""
from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

# ── Noun factor tags ──────────────────────────────────────────────────


class NounFactorTag(IntEnum):
    """Grammatical roles a noun can occupy or accept."""
    ACCEPT_RAF      = 1   # يقبل رفعًا
    ACCEPT_NASB     = 2   # يقبل نصبًا
    ACCEPT_JARR     = 3   # يقبل جرًا
    ACCEPT_IDAFA    = 4   # يدخل في إضافة
    ACCEPT_NA_T     = 5   # ينعت
    ACCEPT_BADAL    = 6   # يقع بدلًا
    ACCEPT_KHABAR   = 7   # يقع خبرًا
    ACCEPT_MUBTADA  = 8   # يقع مبتدأ


# ── Verb factor tags ──────────────────────────────────────────────────


class VerbFactorTag(IntEnum):
    """Grammatical obligations / capabilities of a verb."""
    NEEDS_SUBJECT    = 1   # يحتاج فاعلًا
    ALLOWS_OBJECT    = 2   # يقبل مفعولًا
    ACCEPTS_NASB     = 3   # يقبل نصب في المضارع
    ACCEPTS_JAZM     = 4   # يقبل جزم في المضارع
    ALLOWS_PASSIVE   = 5   # يُبنى للمجهول
    AGREEMENT_FRAME  = 6   # تفاصيل المطابقة (يُخزن كمعرف)


# ── Particle factor tags ──────────────────────────────────────────────


class ParticleFactorTag(IntEnum):
    """What a particle does to its syntactic environment."""
    GOVERNS_JARR  = 1  # يجر
    GOVERNS_NASB  = 2  # ينصب
    GOVERNS_JAZM  = 3  # يجزم
    GOVERNS_NASKH = 4  # ينسخ (كان، إن …)
    LINKS_CLAUSE  = 5  # يربط جملة بجملة
    OPENS_SLOT    = 6  # يفتح فتحة (حرف استفهام، نداء …)


# ── Main function ─────────────────────────────────────────────────────


def factor_system(slots: dict[int, int]) -> int:
    """𝔸(w) = F( π(tag, value), … )  sorted by tag.

    Use tag constants from NounFactorTag / VerbFactorTag / ParticleFactorTag.
    Value 1 = yes / 0 = no; other integers encode degree/type.
    """
    if not slots:
        return 0
    return fractal_fold(
        [cantor_pair(tag, val) for tag, val in sorted(slots.items())]
    )
