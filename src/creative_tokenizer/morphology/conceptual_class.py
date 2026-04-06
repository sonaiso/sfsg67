"""Conceptual classification of signifieds.

PARTICULAR (جزئي): applies to one individual only.
UNIVERSAL  (كلي):  can apply to many.

Universal subtypes:
  MUTAWATI   (متواطئ): uniform predication, no gradation (e.g. رجل, جبل)
  MUSHAKKAK  (مشكك):  graded predication (e.g. نور — from dim to radiant)
  MUTABAYIN  (متباين): distinct fields, no shared core (e.g. سواد vs بياض)
  MUSHTARAK  (مشترك): one sign, many signifieds (e.g. عين)
  MUTARADIF  (مترادف): synonym cluster (one signified, many signs)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

_T_CLASS = 1
_T_UNIFORMITY = 2
_T_GRADATION = 3
_T_SHARED_CORE = 4
_T_POLYSEMY_N = 5


class ConceptualClass(IntEnum):
    PARTICULAR = 1
    UNIVERSAL = 2
    MUTAWATI = 3
    MUSHAKKAK = 4
    MUTABAYIN = 5
    MUSHTARAK = 6
    MUTARADIF = 7


@dataclass(frozen=True, slots=True)
class ConceptNode:
    concept_class: ConceptualClass
    uniformity: int  # 1=uniform  0=graded (relevant for MUSHAKKAK)
    gradation: int  # grade-system id when graded
    shared_core: int  # 0=no shared core (MUTABAYIN)
    polysemy_n: int  # number of distinct signifieds (MUSHTARAK)
    concept_id: int


def make_concept(
    concept_class: ConceptualClass,
    uniformity: int = 1,
    gradation: int = 0,
    shared_core: int = 0,
    polysemy_n: int = 1,
) -> ConceptNode:
    concept_id = fractal_fold(
        [
            cantor_pair(_T_CLASS, int(concept_class)),
            cantor_pair(_T_UNIFORMITY, uniformity),
            cantor_pair(_T_GRADATION, gradation),
            cantor_pair(_T_SHARED_CORE, shared_core),
            cantor_pair(_T_POLYSEMY_N, polysemy_n),
        ]
    )
    return ConceptNode(
        concept_class=concept_class,
        uniformity=uniformity,
        gradation=gradation,
        shared_core=shared_core,
        polysemy_n=polysemy_n,
        concept_id=concept_id,
    )
