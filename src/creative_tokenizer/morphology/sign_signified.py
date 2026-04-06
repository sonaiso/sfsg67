"""Sign ↔ Signified coupling.

𝔻_s(w)     = ℙ(w)           — sign/signifier value (already in pre_compositional)
𝔻_m(x)     = F(O,E,U,K,R)   — signified/meaning node
ℂ_sd(w, x) = F(sign, signified, type, strength) — the coupling bond

CouplingType distinguishes how sign maps to signified:
  WADI_ASLI  — original lexical placement (وضع أصلي)
  URFI       — common usage (عرفي)
  ISTILAHI   — technical/terminological (اصطلاحي)
  TADAWULI   — pragmatic/contextual (تداولي)
  MAJAZI     — metaphorical (مجازي)
  MUSHTARAK  — polysemous shared sign (مشترك)
  MUTARADIF  — synonymous cluster (مترادف)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .exact_decimal import READY_FULL, ExactDecimal
from .fractal_storage import cantor_pair, fractal_fold


class CouplingType(IntEnum):
    WADI_ASLI = 1
    URFI = 2
    ISTILAHI = 3
    TADAWULI = 4
    MAJAZI = 5
    MUSHTARAK = 6
    MUTARADIF = 7


@dataclass(frozen=True, slots=True)
class SignifiedNode:
    ontology_id: int  # O(x)
    epistemic_id: int  # E(x)
    universality: int  # U(x) — PARTICULAR=1 / UNIVERSAL=2
    kind_id: int  # K(x) — conceptual class node id
    relations_id: int  # R(x) — internal semantic relations
    signified_id: int  # F(O,E,U,K,R)


def make_signified(
    ontology_id: int,
    epistemic_id: int,
    universality: int,
    kind_id: int,
    relations_id: int = 0,
) -> SignifiedNode:
    signified_id = fractal_fold(
        [
            cantor_pair(1, ontology_id),
            cantor_pair(2, epistemic_id),
            cantor_pair(3, universality),
            cantor_pair(4, kind_id),
            cantor_pair(5, relations_id),
        ]
    )
    return SignifiedNode(
        ontology_id=ontology_id,
        epistemic_id=epistemic_id,
        universality=universality,
        kind_id=kind_id,
        relations_id=relations_id,
        signified_id=signified_id,
    )


@dataclass(frozen=True, slots=True)
class SignSignifiedCoupling:
    sign_id: int
    signified_id: int
    coupling_type: CouplingType
    strength: ExactDecimal
    coupling_id: int


def make_coupling(
    sign_id: int,
    signified_id: int,
    coupling_type: CouplingType,
    strength: tuple[int, int] = READY_FULL,
) -> SignSignifiedCoupling:
    s = ExactDecimal.from_pair(strength)
    coupling_id = fractal_fold(
        [
            cantor_pair(1, sign_id),
            cantor_pair(2, signified_id),
            cantor_pair(3, int(coupling_type)),
            cantor_pair(4, s.fractal_id()),
        ]
    )
    return SignSignifiedCoupling(
        sign_id=sign_id,
        signified_id=signified_id,
        coupling_type=coupling_type,
        strength=s,
        coupling_id=coupling_id,
    )
