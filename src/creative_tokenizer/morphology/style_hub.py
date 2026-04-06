"""Stylistic hubs for sentence-level economy.

Every sentence links to a shared StyleHub rather than re-encoding its full
stylistic structure from scratch.  Only local deviations (delta) are stored
per sentence.

  KHABAR subtypes: HAQIQI, TAQDIRI, IBTIDAI, TALABI
  INSHA  subtypes: AMMAR, NAHY, ISTIFHAM, TAMANNI, NIDA, AQD
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair


class StyleType(IntEnum):
    KHABAR = 1
    INSHA = 2


class KhabarSubtype(IntEnum):
    HAQIQI = 1
    TAQDIRI = 2
    IBTIDAI = 3
    TALABI = 4


class InshaSubtype(IntEnum):
    AMMAR = 1
    NAHY = 2
    ISTIFHAM = 3
    TAMANNI = 4
    NIDA = 5
    AQD = 6


@dataclass(frozen=True, slots=True)
class StyleHub:
    style_type: StyleType
    substyle: int  # KhabarSubtype or InshaSubtype value
    hub_id: int


def make_style_hub(style_type: StyleType, substyle: int) -> StyleHub:
    hub_id = cantor_pair(int(style_type), substyle)
    return StyleHub(style_type=style_type, substyle=substyle, hub_id=hub_id)
