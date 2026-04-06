"""Metaphor nodes: lexical and compositional.

A metaphor is triggered when the literal reading is blocked or a qarina
(قرينة صارفة) deflects interpretation from the literal meaning.

Rel_majaz(w, x0, x1) = F(
    π(1, literal_source_id),
    π(2, blocking_condition),
    π(3, qarina_id),
    π(4, figurative_target_id),
    π(5, metaphor_type),
)

LexicalMetaphorNode:        metaphor at the individual word level.
CompositionalMetaphorNode:  metaphor spanning a full clause/sentence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class MetaphorType(IntEnum):
    MUSHABAHA = 1  # مشابهة — similarity
    MUJAWARA = 2  # مجاورة — contiguity / metonymy
    SABABIYYA = 3  # سببية — causal
    MUSABBABIYYA = 4  # مسببية — resultant
    KULLIYYA = 5  # كلية — whole for part
    JUZ_IYYA = 6  # جزئية — part for whole


@dataclass(frozen=True, slots=True)
class LexicalMetaphorNode:
    literal_source_id: int
    blocking_condition: int
    qarina_id: int
    figurative_target_id: int
    metaphor_type: MetaphorType
    metaphor_id: int


@dataclass(frozen=True, slots=True)
class CompositionalMetaphorNode:
    sentence_id: int
    blocking_condition: int
    qarina_id: int
    metaphor_type: MetaphorType
    metaphor_id: int


def make_lexical_metaphor(
    literal_source_id: int,
    blocking_condition: int,
    qarina_id: int,
    figurative_target_id: int,
    metaphor_type: MetaphorType,
) -> LexicalMetaphorNode:
    metaphor_id = fractal_fold(
        [
            cantor_pair(1, literal_source_id),
            cantor_pair(2, blocking_condition),
            cantor_pair(3, qarina_id),
            cantor_pair(4, figurative_target_id),
            cantor_pair(5, int(metaphor_type)),
        ]
    )
    return LexicalMetaphorNode(
        literal_source_id=literal_source_id,
        blocking_condition=blocking_condition,
        qarina_id=qarina_id,
        figurative_target_id=figurative_target_id,
        metaphor_type=metaphor_type,
        metaphor_id=metaphor_id,
    )


def make_compositional_metaphor(
    sentence_id: int,
    blocking_condition: int,
    qarina_id: int,
    metaphor_type: MetaphorType,
) -> CompositionalMetaphorNode:
    metaphor_id = fractal_fold(
        [
            cantor_pair(1, sentence_id),
            cantor_pair(2, blocking_condition),
            cantor_pair(3, qarina_id),
            cantor_pair(4, int(metaphor_type)),
        ]
    )
    return CompositionalMetaphorNode(
        sentence_id=sentence_id,
        blocking_condition=blocking_condition,
        qarina_id=qarina_id,
        metaphor_type=metaphor_type,
        metaphor_id=metaphor_id,
    )
