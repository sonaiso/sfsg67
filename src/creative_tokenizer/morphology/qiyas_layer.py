"""Qiyas layer — nucleus 7 (القياس / analogy-inference).

A Qiyas has four structural pillars:

  asl_id            — the base case whose ruling is known (الأصل)
  far_id            — the derived case being analogized (الفرع)
  illa_id           — the effective cause / ratio legis shared between them (العلة)
  nisbah_id         — the transferred ruling/property (الحكم المنقول)

Formally:
  qiyas_id = F(π(1,asl_id), π(2,far_id), π(3,illa_id),
                π(4,nisbah_id), π(5,qiyas_type))

QiyasType:
  JALI   (جلي)   — the shared cause is explicit and unambiguous
  KHAFI  (خفي)   — the shared cause is inferred/implicit
  AWL    (الأولى) — a fortiori: far is more deserving of the ruling than asl

IllaMatchStrength — how strongly the illa holds between asl and far':
  QATII  (قطعي)  — certain
  ZANNI  (ظني)   — probable
  DAIF   (ضعيف)  — weak

Pre-condition for valid qiyas:
  - asl must have an established ground truth id (its ruling/nisbah is known)
  - illa must be present in both asl and far'
  - no semantic conflict blocks the transfer (conflict_resolution layer)
  - qiyas does not enter before all pre-judgment layers are complete

HUKM (nucleus 8 — truth/judgment) is not built here.
This module provides the preparatory infrastructure only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .exact_decimal import READY_FULL, ExactDecimal
from .fractal_storage import cantor_pair, fractal_fold


class QiyasType(IntEnum):
    JALI = 1    # قياس جلي
    KHAFI = 2   # قياس خفي
    AWL = 3     # قياس الأولى


class IllaMatchStrength(IntEnum):
    QATII = 1   # قطعي
    ZANNI = 2   # ظني
    DAIF = 3    # ضعيف


@dataclass(frozen=True, slots=True)
class QiyasNode:
    asl_id: int
    far_id: int
    illa_id: int
    nisbah_id: int                  # ruling / transferred property
    qiyas_type: QiyasType
    illa_strength: IllaMatchStrength
    confidence: ExactDecimal        # how confidently the transfer holds
    qiyas_id: int


def make_qiyas(
    asl_id: int,
    far_id: int,
    illa_id: int,
    nisbah_id: int,
    qiyas_type: QiyasType = QiyasType.JALI,
    illa_strength: IllaMatchStrength = IllaMatchStrength.QATII,
    confidence: tuple[int, int] = READY_FULL,
) -> QiyasNode:
    """Build a QiyasNode.  The ruling travels from asl to far' via illa.

    confidence uses ExactDecimal (numerator, scale) — same convention as
    readiness / iltizam strength in the rest of the system.
    """
    conf = ExactDecimal.from_pair(confidence)
    qiyas_id = fractal_fold(
        [
            cantor_pair(1, asl_id),
            cantor_pair(2, far_id),
            cantor_pair(3, illa_id),
            cantor_pair(4, nisbah_id),
            cantor_pair(5, int(qiyas_type)),
            cantor_pair(6, int(illa_strength)),
            cantor_pair(7, conf.fractal_id()),
        ]
    )
    return QiyasNode(
        asl_id=asl_id,
        far_id=far_id,
        illa_id=illa_id,
        nisbah_id=nisbah_id,
        qiyas_type=qiyas_type,
        illa_strength=illa_strength,
        confidence=conf,
        qiyas_id=qiyas_id,
    )
