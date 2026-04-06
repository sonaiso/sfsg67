from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair
from .grapheme_atoms import consonantal_skeleton_id


class LexicalType(IntEnum):
    """Semantic carrier type tags.  Values are stable across versions."""

    JAMID = 101     # جامد: lexically independent, no productive derivational pattern
    ROOT = 102      # جذر: derivational root nucleus
    MASDAR = 103    # مصدر: verbal noun / event anchor
    OPERATOR = 104  # أداة: prepositions, connectives, particles
    DEICTIC = 105   # مبني إحالي: demonstratives, pronouns
    COPULAR = 106   # ناسخ: copular or raising verbs
    DEPENDENT = 107  # غير مستقل: any other bound form


class Independence(IntEnum):
    DEPENDENT = 0
    INDEPENDENT = 1


class IndependenceGrade(IntEnum):
    """Four-level independence scale for Arabic word forms.

    Replaces the binary Independence flag when finer discrimination is needed.
    0-3 values are stable across versions.
    """

    BOUND = 0       # غير مستقل إلا بالتعلق أو الإلصاق (e.g. bound pronoun)
    RELATIONAL = 1  # مستقل شكليًا لكنه علائقي الإغلاق (e.g. demonstrative)
    DERIVED = 2     # حامل حدثي/مصدري قابل للتشجير (e.g. verbal noun, derivative)
    AUTONOMOUS = 3  # مستقل ذاتي معجمي (e.g. jamid: شمس، جبل)


def jamid_carrier(text: str) -> int:
    """J(w) = π(JAMID, C(w)) — carrier for lexically opaque independent nouns."""
    return cantor_pair(LexicalType.JAMID, consonantal_skeleton_id(text))


def root_carrier(text: str) -> int:
    """R(w) = π(ROOT, C(w)) — carrier for derivational root nuclei."""
    return cantor_pair(LexicalType.ROOT, consonantal_skeleton_id(text))


def masdar_carrier(root_id: int, pattern_id: int) -> int:
    """M = π(MASDAR, π(root_id, pattern_id)) — event-anchor carrier."""
    return cantor_pair(LexicalType.MASDAR, cantor_pair(root_id, pattern_id))


def operator_carrier(text: str) -> int:
    """O(w) = π(OPERATOR, C(w)) — carrier for particles and functional words."""
    return cantor_pair(LexicalType.OPERATOR, consonantal_skeleton_id(text))


def pattern_carrier(masdar_id: int, pattern_id: int) -> int:
    """Derived-form carrier: S(w) = π(masdar_id, pattern_id)."""
    return cantor_pair(masdar_id, pattern_id)
