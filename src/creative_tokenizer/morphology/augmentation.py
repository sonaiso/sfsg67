"""Augmentation letter roles (𝒵) — §10 of the formal specification.

𝒵 ⊆ 𝒞 is the subset of consonants that serve as augmentation letters.
The traditional mnemonic is سألتمونيها.

Each augmentation letter receives a role from:

* وزنية      — pattern-structural (adds to the morphological template)
* اشتقاقية   — derivational (changes the root meaning)
* صرفية      — inflectional (changes tense/person/number)
* دلالية     — semantic (adds a meaning nuance)
* تقوية      — intensification (shadda-like strengthening)
* نقل صنفي   — category transfer (converts noun ↔ verb)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold, phi


class AugmentRole(IntEnum):
    """Functional role of an augmentation letter — §10."""

    PATTERN = 1  # زيادة وزنية
    DERIVATIONAL = 2  # زيادة اشتقاقية
    INFLECTIONAL = 3  # زيادة صرفية
    SEMANTIC = 4  # زيادة دلالية
    INTENSIFYING = 5  # تقوية
    CATEGORY_TRANSFER = 6  # نقل صنفي


#: The ten augmentation letters (سألتمونيها) as code-points.
AUGMENTATION_LETTERS: frozenset[int] = frozenset(
    {
        0x0633,  # س
        0x0623,  # أ
        0x0644,  # ل
        0x062A,  # ت
        0x0645,  # م
        0x0648,  # و
        0x0646,  # ن
        0x064A,  # ي
        0x0647,  # هـ
        0x0627,  # ا
    }
)


@dataclass(frozen=True, slots=True)
class Augmentation:
    """A specific augmentation instance: a letter together with its role(s).

    ``position`` is the zero-based index within the augmented form where
    the augmentation letter appears.
    """

    letter: str
    roles: frozenset[AugmentRole]
    position: int


def make_augmentation(
    letter: str,
    roles: frozenset[AugmentRole],
    position: int = 0,
) -> Augmentation:
    """Construct an Augmentation."""
    if len(letter) != 1:
        raise ValueError(f"Augmentation letter must be a single character, got {letter!r}")
    return Augmentation(letter=letter, roles=roles, position=position)


def augmentation_id(aug: Augmentation) -> int:
    """Fractal identity of an augmentation instance.

    z_id = π(φ(letter), π(position, F(sorted roles)))
    """
    role_fold = fractal_fold(sorted(int(r) for r in aug.roles)) if aug.roles else 0
    return cantor_pair(phi(aug.letter), cantor_pair(aug.position, role_fold))


def is_augmentation_letter(cp: int) -> bool:
    """Return True if the code-point is one of the ten augmentation letters."""
    return cp in AUGMENTATION_LETTERS
