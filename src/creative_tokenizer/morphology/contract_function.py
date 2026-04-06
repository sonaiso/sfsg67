"""Contract function: value-slots the word form offers before composition.

ℂ(w) = F( π(t1,v1), π(t2,v2), … )

Separate tag-enums exist for noun / verb / particle slots.
Only populate the slots relevant to your word's BaseClass; the rest default to 0.
"""
from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

# ── Shared value tags ─────────────────────────────────────────────────


class SharedContractTag(IntEnum):
    """Tags shared across all word classes."""
    GENDER      = 1   # 1=masc 2=fem
    NUMBER      = 2   # 1=sg 2=dual 3=pl 4=many(كثرة)
    DEFINITENESS = 3  # 1=definite 0=indefinite


# ── Noun-specific tags ────────────────────────────────────────────────


class NounContractTag(IntEnum):
    """Tags specific to nouns (ISM)."""
    IDAFA             = 10  # إضافة:    1=in construct 0=free
    TANWEEN           = 11  # تنوين:    1=present 0=absent
    NISBA             = 12  # نسبة:     1=yes
    DIMINUTION        = 13  # تصغير:    1=yes
    AUGMENTATION      = 14  # تكبير:    1=yes
    INDUSTRIAL_MASDAR = 15  # مصدر صناعي: 1=yes
    UNIT              = 16  # وحدة مفردة: 1=yes (تمرة من تمر)
    PLURALITY         = 17  # كثرة:     1=yes
    TIME_NAME         = 18  # اسم زمان: 1=yes
    PLACE_NAME        = 19  # اسم مكان: 1=yes
    INSTRUMENT_NAME   = 20  # اسم آلة:  1=yes
    INSTANCE_MASDAR   = 21  # اسم مرة:  1=yes
    SHAPE_MASDAR      = 22  # اسم هيئة: 1=yes


# ── Verb-specific tags ────────────────────────────────────────────────


class VerbContractTag(IntEnum):
    """Tags specific to verbs (FI'L)."""
    TENSE         = 30  # 1=past 2=present 3=imperative
    EVENT_MODE    = 31  # 1=completed 2=ongoing 3=potential
    VOICE         = 32  # 1=active 2=passive
    TRANSITIVITY  = 33  # 1=transitive 0=intransitive
    CAUSATIVITY   = 34  # 1=causative
    RESULTATIVITY = 35  # 1=resultative
    PERSON        = 36  # 1/2/3
    NUN_STATE     = 37  # 1=present 0=deleted
    REFLEXIVITY   = 38  # 1=reflexive
    RECIPROCITY   = 39  # 1=reciprocal
    REQUEST_MODE  = 40  # 1=request/imperative meaning
    PASSIVIZABILITY = 41 # 1=can be passivized


# ── Particle-specific tags ────────────────────────────────────────────


class ParticleContractTag(IntEnum):
    """Tags specific to particles / operators (HARF)."""
    OPERATOR_TYPE     = 50  # 1=jarr 2=nasb 3=jazm 4=naskh 5=clauselinker
    SCOPE             = 51  # 1=nominal 2=verbal 3=clausal
    CLOSURE           = 52  # 1=requires complement
    GOVERNANCE_TARGET = 53  # 1=ism 2=fi'l 3=jumla
    SEMANTIC_LINK     = 54  # 1=cause 2=result 3=cond 4=concess 5=purpose


# ── Main function ─────────────────────────────────────────────────────


def contract_function(slots: dict[int, int]) -> int:
    """ℂ(w) = F( π(tag, value), … )  sorted by tag for stability.

    Pass tag→value pairs from *any* of the tag enums above.
    Tags with value 0 are included (zero is a meaningful value, e.g. absent
    tanween).  Remove a tag entirely if it is genuinely unspecified.
    """
    if not slots:
        return 0
    return fractal_fold(
        [cantor_pair(tag, val) for tag, val in sorted(slots.items())]
    )
