"""Judgment construction and truth/guidance evaluation.

J: Gₛ × Gₘ × D → P   (judgment from signifier graph × signified graph × dalāla)
E: P × W → V           (evaluation from proposition × world state)

Design principle: judgment on existence (وجود) may be certain (قطعي),
but judgment on quality/property (حقيقة/صفة) is revisable (ظني).
Therefore evaluation separates truth_state from guidance_state.
"""

from __future__ import annotations

from dataclasses import dataclass

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

from ..core.enums import GuidanceState, TruthState

__all__ = [
    "EvalResult",
    "GuidanceState",
    "Judgment",
    "TruthState",
    "build_evaluation",
    "build_judgment",
]


@dataclass(frozen=True, slots=True)
class Judgment:
    """A propositional judgment built from dalāla-validated links.

    Attributes
    ----------
    subject:    subject token identity
    predicate:  predicate / verb token identity
    object_id:  object token identity (0 if intransitive)
    time:       temporal anchor (0 = unspecified)
    space:      spatial anchor (0 = unspecified)
    polarity:   1 = affirmative, -1 = negative
    judgment_id: stable fractal identity
    """

    subject: int
    predicate: int
    object_id: int
    time: int
    space: int
    polarity: int
    judgment_id: int


def build_judgment(
    subject: int,
    predicate: int,
    object_id: int = 0,
    time: int = 0,
    space: int = 0,
    polarity: int = 1,
) -> Judgment:
    """Construct a Judgment (proposition vector)."""
    jid = fractal_fold([
        cantor_pair(1, subject),
        cantor_pair(2, predicate),
        cantor_pair(3, object_id),
        cantor_pair(4, time if time >= 0 else 0),
        cantor_pair(5, space if space >= 0 else 0),
        cantor_pair(6, 1 if polarity >= 0 else 0),
    ])
    return Judgment(
        subject=subject,
        predicate=predicate,
        object_id=object_id,
        time=time,
        space=space,
        polarity=polarity,
        judgment_id=jid,
    )


@dataclass(frozen=True, slots=True)
class EvalResult:
    """Evaluation result: truth + guidance + confidence.

    Attributes
    ----------
    truth_state:    epistemic truth value (certain / probable / unknown / false)
    guidance_state: normative guidance (obligatory / recommended / … / neutral)
    confidence:     overall confidence in [0.0, 1.0]
    eval_id:        stable fractal identity
    """

    truth_state: TruthState
    guidance_state: GuidanceState
    confidence: float
    eval_id: int


def build_evaluation(
    judgment: Judgment,
    truth_state: TruthState = TruthState.PROBABLE,
    guidance_state: GuidanceState = GuidanceState.NEUTRAL,
    confidence: float = 0.8,
) -> EvalResult:
    """Evaluate a Judgment against world state.

    Produces truth_state + guidance_state + confidence.
    """
    eid = fractal_fold([
        cantor_pair(1, judgment.judgment_id),
        cantor_pair(2, int(truth_state)),
        cantor_pair(3, int(guidance_state)),
        cantor_pair(4, int(confidence * 1000)),
    ])
    return EvalResult(
        truth_state=truth_state,
        guidance_state=guidance_state,
        confidence=confidence,
        eval_id=eid,
    )
