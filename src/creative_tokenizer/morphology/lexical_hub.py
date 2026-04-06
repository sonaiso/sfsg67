"""Shared lexical meaning hubs (مطابقة / تضمن / التزام).

Three hub types give each lexeme an economy storage entry.  Multiple surface
forms that share the same primary meaning reuse the same hub rather than
duplicating its content.

  MUTABAQA  — central denotation (المعنى الموضوع بالمطابقة)
  TADAMMUN  — component/entailed parts (بالتضمن)
  ILTIZAM   — conditional inferential implicature (بالالتزام)

iltizam is always conditional: obligation_mode is hardcoded to 0.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .exact_decimal import ExactDecimal
from .fractal_storage import cantor_pair, fractal_fold

_T_COND = 1
_T_STR = 2
_T_OBL = 3


class LexicalHubType(IntEnum):
    MUTABAQA = 1
    TADAMMUN = 2
    ILTIZAM = 3


@dataclass(frozen=True, slots=True)
class LexicalMeaningHub:
    hub_type: LexicalHubType
    content_id: int
    hub_id: int  # π(hub_type, content_id)


def make_lexical_hub(
    hub_type: LexicalHubType,
    content_id: int,
) -> LexicalMeaningHub:
    """Return a shared lexical hub identified by (hub_type, content_id)."""
    hub_id = cantor_pair(int(hub_type), content_id)
    return LexicalMeaningHub(hub_type=hub_type, content_id=content_id, hub_id=hub_id)


def iltizam_hub(
    condition_schema: int,
    strength: ExactDecimal,
) -> LexicalMeaningHub:
    """Build an iltizam hub with obligation_mode=0 (always conditional).

    obligation_mode=0 means this meaning is inferential, not obligatory.
    It activates only when condition_schema is satisfied in context.
    """
    content_id = fractal_fold(
        [
            cantor_pair(_T_COND, condition_schema),
            cantor_pair(_T_STR, strength.fractal_id()),
            cantor_pair(_T_OBL, 0),  # always 0: conditional, not obligatory
        ]
    )
    return make_lexical_hub(LexicalHubType.ILTIZAM, content_id)
