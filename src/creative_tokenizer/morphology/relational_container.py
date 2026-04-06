from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class RelationalType(IntEnum):
    """Top-level type discriminant for relational containers."""

    PRONOUN = 1        # ضمير
    DEMONSTRATIVE = 2  # اسم إشارة
    RELATIVE = 3       # اسم موصول
    COPULAR = 4        # فعل ناسخ


# ---------------------------------------------------------------------------
# Pronoun (ضمير) property tags
# ---------------------------------------------------------------------------


class PronounTag(IntEnum):
    """Property tags for pronoun relational containers.  Values are stable."""

    PERSON = 1      # 1=first, 2=second, 3=third
    NUMBER = 2      # 1=singular, 2=dual, 3=plural
    GENDER = 3      # 1=masculine, 2=feminine
    ATTACHMENT = 4  # 0=free (منفصل), 1=bound (متصل), 2=implicit (مستتر)
    ROLE = 5        # 1=subject, 2=object, 3=genitive, 4=possessive
    CLOSURE = 6     # 1=needs antecedent or discourse anchor


# ---------------------------------------------------------------------------
# Demonstrative (اسم إشارة) property tags
# ---------------------------------------------------------------------------


class DemonstrativeTag(IntEnum):
    """Property tags for demonstrative relational containers.  Values are stable."""

    DISTANCE = 1     # 0=proximal (هذا), 1=medial, 2=distal (ذلك), 3=discourse
    TARGET_KIND = 2  # 1=entity, 2=person, 3=place, 4=time, 5=discourse-unit
    NUMBER = 3       # 1=singular, 2=dual, 3=plural
    GENDER = 4       # 1=masculine, 2=feminine
    CLOSURE = 5      # 1=needs demonstratum (مشار إليه)


# ---------------------------------------------------------------------------
# Relative (اسم موصول) property tags
# ---------------------------------------------------------------------------


class RelativeTag(IntEnum):
    """Property tags for relative pronoun relational containers.  Values are stable."""

    SUBTYPE = 1         # 1=specific (الذي/التي…), 2=generic (من/ما)
    NUMBER = 2          # 1=singular, 2=dual, 3=plural
    GENDER = 3          # 1=masculine, 2=feminine
    REQUIRES_SILA = 4   # 1=requires a relative clause (صلة)
    REQUIRES_AID = 5    # 1=requires a return-link (عائد) inside sila
    DEFINITENESS = 6    # always 1 (موصول inherently definite)


# ---------------------------------------------------------------------------
# Copular (فعل ناسخ) property tags
# ---------------------------------------------------------------------------


class CopularTag(IntEnum):
    """Property tags for copular verb relational containers.  Values are stable."""

    SUBTYPE = 1         # 1=kana, 2=sara, 3=laysa, 4=asbaha, 5=zalla, 6=bata
    EFFECT = 2          # 1=tense, 2=becoming, 3=continuity, 4=negation, 5=inchoative
    SUBJECT_SLOT = 3    # 1=opens subject slot (اسم الناسخ)
    PREDICATE_SLOT = 4  # 1=opens predicate slot (خبر الناسخ)
    CLOSURE = 5         # 1=requires both subject and predicate
    MODE = 6            # 1=eventive, 2=predicative-transform


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------


def relational_container(
    rel_type: RelationalType,
    properties: dict[int, int],
) -> int:
    """Ω(w) = π(rel_type, F(sorted property pairs)).

    Encodes the relational closure requirements of a word.
    The RelationalType discriminant guarantees that PRONOUN, DEMONSTRATIVE,
    RELATIVE, and COPULAR occupy disjoint identity spaces even when their
    property bundles happen to be numerically identical.

    Returns cantor_pair(rel_type, 0) when properties is empty.
    """
    if not properties:
        return cantor_pair(int(rel_type), 0)
    props_id = fractal_fold(
        [cantor_pair(k, v) for k, v in sorted(properties.items())]
    )
    return cantor_pair(int(rel_type), props_id)
