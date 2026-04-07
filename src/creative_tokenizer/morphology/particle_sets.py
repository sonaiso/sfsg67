"""Particle / connector sets (ℒ) — §9 of the formal specification.

Particles form the *bridge from the single word to the sentence*.
They are classified into sub-sets:

* ℒ_conj      — conjunctions (حروف العطف)
* ℒ_cond      — conditional particles (أدوات الشرط)
* ℒ_neg       — negation particles (أدوات النفي)
* ℒ_interr    — interrogative particles (أدوات الاستفهام)
* ℒ_voc       — vocative particles (أدوات النداء)
* ℒ_emph      — emphatic particles (أدوات التوكيد)
* ℒ_cause     — causal particles (أدوات التعليل)
* ℒ_restrict  — restrictive particles (أدوات الحصر)
* ℒ_except    — exception particles (أدوات الاستثناء)
* ℒ_jar       — prepositions (حروف الجر)
* ℒ_nasikh    — modifying operators (النواسخ)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold, phi


class ParticleKind(IntEnum):
    """Sub-classification of particles — §9."""

    CONJUNCTION = 1  # حروف العطف
    CONDITIONAL = 2  # أدوات الشرط
    NEGATION = 3  # أدوات النفي
    INTERROGATIVE = 4  # أدوات الاستفهام
    VOCATIVE = 5  # أدوات النداء
    EMPHATIC = 6  # أدوات التوكيد
    CAUSAL = 7  # أدوات التعليل
    RESTRICTIVE = 8  # أدوات الحصر
    EXCEPTION = 9  # أدوات الاستثناء
    PREPOSITION = 10  # حروف الجر
    NASIKH = 11  # النواسخ (إنّ وأخواتها، كان وأخواتها، ظنّ وأخواتها)


@dataclass(frozen=True, slots=True)
class Particle:
    """A concrete particle with its surface form and classification.

    ``governance`` indicates the grammatical case this particle assigns
    to its complement (e.g. prepositions govern genitive = 3 / jarr).
    0 means no case governance.
    """

    surface: str
    kind: ParticleKind
    governance: int  # 0=none, 1=raf', 2=nasb, 3=jarr, 4=jazm


def make_particle(surface: str, kind: ParticleKind, governance: int = 0) -> Particle:
    """Construct a Particle."""
    return Particle(surface=surface, kind=kind, governance=governance)


def particle_id(p: Particle) -> int:
    """Fractal identity of a particle.

    l_id = π(kind, π(governance, F(φ(c) for c in surface)))
    """
    surface_fold = fractal_fold([phi(c) for c in p.surface]) if p.surface else 0
    return cantor_pair(int(p.kind), cantor_pair(p.governance, surface_fold))


# ---------------------------------------------------------------------------
# Canonical inventories (illustrative, extendable)
# ---------------------------------------------------------------------------

#: Common conjunctions  (§9)
CONJUNCTIONS: tuple[str, ...] = ("وَ", "فَ", "ثُمَّ", "أَوْ", "أَمْ", "بَلْ", "لَا", "لَكِنْ")

#: Common prepositions  (§9)
PREPOSITIONS: tuple[str, ...] = (
    "مِنْ",
    "إِلَى",
    "عَنْ",
    "عَلَى",
    "فِي",
    "بِ",
    "لِ",
    "كَ",
    "حَتَّى",
    "مُنْذُ",
    "مُذْ",
    "رُبَّ",
    "خَلَا",
    "عَدَا",
    "حَاشَا",
)

#: Conditional particles  (§9)
CONDITIONALS: tuple[str, ...] = ("إِنْ", "إِذَا", "لَوْ", "لَوْلَا", "أَمَّا")

#: Negation particles  (§9)
NEGATIONS: tuple[str, ...] = ("لَا", "لَمْ", "لَنْ", "مَا", "لَيْسَ", "لَمَّا")

#: Interrogative particles  (§9)
INTERROGATIVES: tuple[str, ...] = ("هَلْ", "أَ", "مَنْ", "مَا", "أَيْنَ", "مَتَى", "كَيْفَ", "كَمْ")

#: Vocative particles  (§9)
VOCATIVES: tuple[str, ...] = ("يَا", "أَيَا", "هَيَا", "أَيْ")

#: Nasikh operators  (§9)
NASIKHAAT: tuple[str, ...] = (
    "إِنَّ",
    "أَنَّ",
    "كَأَنَّ",
    "لَكِنَّ",
    "لَيْتَ",
    "لَعَلَّ",
    "كَانَ",
    "أَصْبَحَ",
    "أَمْسَى",
    "ظَلَّ",
    "بَاتَ",
    "صَارَ",
    "ظَنَّ",
    "حَسِبَ",
    "زَعَمَ",
    "خَالَ",
)
