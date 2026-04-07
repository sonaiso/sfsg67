"""Root (ℛ) and pattern / وزن (𝒲) formal sets — §5–6 of the specification.

Roots are ordered tuples of root consonants:

* ℛ₃ — trilateral roots  (c₁, c₂, c₃)
* ℛ₄ — quadrilateral roots  (c₁, c₂, c₃, c₄)
* ℛ_frozen — frozen / non-productive bases

Patterns (أوزان) are classified by part of speech and derivation type:

* 𝒲_verb — verb patterns (مجرد، مزيد، رباعي)
* 𝒲_noun — noun patterns (جامد، مشتق)
* Derived noun sub-patterns: مصدر، اسم فاعل، اسم مفعول، صفة مشبهة،
  اسم تفضيل، اسم آلة، اسم زمان ومكان، اسم مرة، اسم هيئة

Fractal identities use the standard π / F primitives so roots and patterns
can be embedded into higher layers by value.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold, phi

# =====================================================================
# §5  Roots  (ℛ)
# =====================================================================


class RootKind(IntEnum):
    """Sub-classification of Arabic roots — §5."""

    TRILATERAL = 3  # ℛ₃  — ثلاثي
    QUADRILATERAL = 4  # ℛ₄  — رباعي
    FROZEN = 0  # ℛ_frozen — جامد غير قياسي


@dataclass(frozen=True, slots=True)
class Root:
    """An Arabic root: an ordered tuple of consonant code-points.

    ``kind`` is inferred from the consonant count unless overridden
    (e.g. a three-consonant frozen root is FROZEN, not TRILATERAL).
    """

    consonants: tuple[str, ...]
    kind: RootKind

    def __post_init__(self) -> None:
        if self.kind == RootKind.TRILATERAL and len(self.consonants) != 3:
            raise ValueError(
                f"Trilateral root must have exactly 3 consonants, "
                f"got {len(self.consonants)}: {self.consonants}"
            )
        if self.kind == RootKind.QUADRILATERAL and len(self.consonants) != 4:
            raise ValueError(
                f"Quadrilateral root must have exactly 4 consonants, "
                f"got {len(self.consonants)}: {self.consonants}"
            )


def make_root(consonants: tuple[str, ...], kind: RootKind | None = None) -> Root:
    """Construct a Root, inferring kind from consonant count if not given."""
    if kind is None:
        if len(consonants) == 3:
            kind = RootKind.TRILATERAL
        elif len(consonants) == 4:
            kind = RootKind.QUADRILATERAL
        else:
            kind = RootKind.FROZEN
    return Root(consonants=consonants, kind=kind)


def root_id(root: Root) -> int:
    """Fractal identity of a root.

    r_id = π(kind, F(φ(c₁), φ(c₂), …))
    """
    if not root.consonants:
        return 0
    letter_fold = fractal_fold([phi(c) for c in root.consonants])
    return cantor_pair(int(root.kind), letter_fold)


# =====================================================================
# §6  Patterns / أوزان  (𝒲)
# =====================================================================


class PatternDomain(IntEnum):
    """Top-level domain of a pattern — §6."""

    VERB = 1  # 𝒲_verb
    NOUN = 2  # 𝒲_noun
    MASDAR = 3  # 𝒲_masdar
    PARTICIPLE = 4  # 𝒲_participle  (اسم فاعل / اسم مفعول)
    ADJECTIVE = 5  # 𝒲_adj         (صفة مشبهة / اسم تفضيل)
    INSTRUMENT = 6  # 𝒲_instrument  (اسم آلة)
    TIME_PLACE = 7  # 𝒲_time_place  (اسم زمان ومكان)


# §6.1  Verb sub-patterns


class VerbPatternKind(IntEnum):
    """Verb pattern sub-classification — §6.1."""

    MUJARRAD = 1  # مجرد — base trilateral
    MAZEED = 2  # مزيد — augmented
    RUBAI = 3  # رباعي — quadrilateral verb


# §6.2  Noun sub-patterns


class NounPatternKind(IntEnum):
    """Noun pattern sub-classification — §6.2."""

    JAMID = 1  # جامد
    MASDAR = 2  # مصدر
    ISM_FAEIL = 3  # اسم فاعل
    ISM_MAFOUL = 4  # اسم مفعول
    SIFA_MUSHABBAHA = 5  # صفة مشبهة
    TAFDEEL = 6  # اسم تفضيل
    MARRA = 7  # اسم مرة
    HAYAH = 8  # اسم هيئة
    INSTRUMENT = 9  # اسم آلة
    TIME_PLACE = 10  # اسم زمان ومكان


@dataclass(frozen=True, slots=True)
class Pattern:
    """An Arabic morphological pattern (وزن).

    ``template`` is the canonical pattern string (e.g. "فَعَلَ", "مَفْعُول").
    ``domain`` and ``sub_kind`` classify the pattern.
    """

    template: str
    domain: PatternDomain
    sub_kind: int  # VerbPatternKind or NounPatternKind value


def make_verb_pattern(template: str, kind: VerbPatternKind) -> Pattern:
    """Create a verb-domain pattern."""
    return Pattern(template=template, domain=PatternDomain.VERB, sub_kind=int(kind))


def make_noun_pattern(template: str, kind: NounPatternKind) -> Pattern:
    """Create a noun-domain pattern."""
    return Pattern(template=template, domain=PatternDomain.NOUN, sub_kind=int(kind))


def pattern_id(pat: Pattern) -> int:
    """Fractal identity of a pattern.

    w_id = π(domain, π(sub_kind, F(φ(c) for c in template)))
    """
    template_fold = fractal_fold([phi(c) for c in pat.template]) if pat.template else 0
    return cantor_pair(int(pat.domain), cantor_pair(pat.sub_kind, template_fold))


# ---------------------------------------------------------------------------
# Canonical pattern inventories (illustrative, extendable)
# ---------------------------------------------------------------------------

#: Base trilateral verb patterns — §6.1
MUJARRAD_PATTERNS: tuple[str, ...] = (
    "فَعَلَ",
    "فَعِلَ",
    "فَعُلَ",
)

#: Common augmented verb patterns — §6.1
MAZEED_PATTERNS: tuple[str, ...] = (
    "أَفْعَلَ",
    "فَعَّلَ",
    "فَاعَلَ",
    "اِنْفَعَلَ",
    "اِفْتَعَلَ",
    "تَفَعَّلَ",
    "تَفَاعَلَ",
    "اِسْتَفْعَلَ",
    "اِفْعَلَّ",
    "اِفْعَوْعَلَ",
)
