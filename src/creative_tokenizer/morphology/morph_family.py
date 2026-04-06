from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class FamilyTag(IntEnum):
    """Morpho-syntactic family tags.  Values are stable across versions."""

    SIMPLE_NOUN = 1
    SIMPLE_VERB = 2
    FIVE_VERBS = 3
    FIVE_NOUNS = 4
    DUAL = 5
    SOUND_MASC_PL = 6
    SOUND_FEM_PL = 7
    BROKEN_PL = 8
    DIPTOTE = 9
    INDECLINABLE = 10
    DEFECTIVE_NOUN = 11
    WEAK_VERB = 12
    HAMZATED = 13
    DOUBLED = 14
    PARTICLE = 15
    DEICTIC_BUILTIN = 16
    COPULAR_OPERATOR = 17
    RELATIVE_OPERATOR = 18


class FiveVerbTag(IntEnum):
    """Property tags for the Five Verbs family.  Values are stable."""

    PERSON = 1     # 1=first, 2=second, 3=third
    NUMBER = 2     # 2=dual, 3=plural
    GENDER = 3     # 1=masculine, 2=feminine
    SUFFIX = 4     # 1=alif-dual, 2=waw-plural, 3=ya-addressee
    NUN_STATE = 5  # 1=present, 0=deleted


class FiveNounTag(IntEnum):
    """Property tags for the Five Nouns family.  Values are stable."""

    LEXEME_CLASS = 1  # 1=ab, 2=akh, 3=ham, 4=faw, 5=dhu
    CASE_CARRIER = 2  # 1=waw, 2=alif, 3=ya
    IDAFA = 3         # 1=in construct state, 0=not
    VALIDITY = 4      # bitmask: bit0=singular, bit1=not-in-small-number


def morph_family_id(
    family: FamilyTag,
    properties: dict[int, int] | None = None,
) -> int:
    """Λ(w) = π(family, F(sorted property pairs)).

    Returns a stable identity for a morph family + optional property bundle.
    Returns cantor_pair(family, 0) when properties is absent or empty.
    New FamilyTag values do not affect existing family IDs.
    """
    if not properties:
        return cantor_pair(int(family), 0)
    props_id = fractal_fold(
        [cantor_pair(k, v) for k, v in sorted(properties.items())]
    )
    return cantor_pair(int(family), props_id)
