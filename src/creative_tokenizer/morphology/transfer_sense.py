"""Lexical sense transfer chain.

Each lexeme may carry a chain of transferred senses:

  WADI_ASLI   — original lexical placement (وضع أصلي)
  URFI        — common usage / عرفي  (حقيقة عرفية)
  ISTILAHI    — terminological       (حقيقة اصطلاحية)
  DOMAIN_SPEC — domain-specific      (شرعي / طبي / رياضي …)

Transfers form edges: original_sense → transferred_sense.
The chain is non-circular: WADI_ASLI is always the root.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class TransferType(IntEnum):
    WADI_ASLI = 1
    URFI = 2
    ISTILAHI = 3
    DOMAIN_SPEC = 4


@dataclass(frozen=True, slots=True)
class TransferNode:
    source_sense_id: int
    target_sense_id: int
    transfer_type: TransferType
    domain_id: int  # 0 = general; >0 = specific domain key
    transfer_id: int


def make_transfer(
    source_sense_id: int,
    target_sense_id: int,
    transfer_type: TransferType,
    domain_id: int = 0,
) -> TransferNode:
    transfer_id = fractal_fold(
        [
            cantor_pair(1, source_sense_id),
            cantor_pair(2, target_sense_id),
            cantor_pair(3, int(transfer_type)),
            cantor_pair(4, domain_id),
        ]
    )
    return TransferNode(
        source_sense_id=source_sense_id,
        target_sense_id=target_sense_id,
        transfer_type=transfer_type,
        domain_id=domain_id,
        transfer_id=transfer_id,
    )
