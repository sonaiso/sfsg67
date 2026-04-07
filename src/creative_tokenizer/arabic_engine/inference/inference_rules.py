"""Inference rules engine (V2).

Applies logical rules to derive new propositions or validate existing ones.
Rules are typed by RuleKind and produce InferenceResult outputs.

This closes the pipeline: once evaluation produces a truth/guidance value,
inference rules can propagate consequences back into the world model.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

from ..cognition.evaluation import EvalResult, Judgment
from ..core.enums import TruthState
from .world_model import Fact, WorldModel, make_fact

__all__ = ["InferenceEngine", "InferenceResult", "RuleKind"]


class RuleKind(IntEnum):
    """Kind of inference rule."""

    MODUS_PONENS = 1  # if P and P→Q then Q
    MODUS_TOLLENS = 2  # if ¬Q and P→Q then ¬P
    TRANSITIVITY = 3  # if P→Q and Q→R then P→R
    CONTRAPOSITIVE = 4  # if P→Q then ¬Q→¬P
    EXISTENTIAL = 5  # if ∃x P(x) then P(a) for witness a
    UNIVERSAL = 6  # if ∀x P(x) then P(a) for any a


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """Result of applying an inference rule.

    Attributes
    ----------
    rule:           which rule was applied
    premise_ids:    identities of premise judgments/facts
    conclusion:     derived Fact (may be new or confirmatory)
    confidence:     confidence in the inference
    result_id:      stable fractal identity
    """

    rule: RuleKind
    premise_ids: tuple[int, ...]
    conclusion: Fact
    confidence: float
    result_id: int


class InferenceEngine:
    """Simple forward-chaining inference engine.

    Maintains a rule registry and applies matching rules to produce
    new facts that are added to the world model.
    """

    def __init__(self, world: WorldModel) -> None:
        self._world = world
        self._results: list[InferenceResult] = []

    @property
    def world(self) -> WorldModel:
        return self._world

    @property
    def results(self) -> tuple[InferenceResult, ...]:
        return tuple(self._results)

    def apply_modus_ponens(
        self,
        antecedent: Fact,
        consequent_subject: str,
        consequent_predicate: str,
    ) -> InferenceResult:
        """If antecedent is true, derive consequent.

        Simplified: if the antecedent fact is CERTAIN or PROBABLE,
        produce a new PROBABLE fact for the consequent.
        """
        if antecedent.truth_state in (TruthState.CERTAIN, TruthState.PROBABLE):
            new_truth = TruthState.PROBABLE
            confidence = antecedent.confidence * 0.9
        else:
            new_truth = TruthState.UNKNOWN
            confidence = 0.1

        conclusion = make_fact(
            consequent_subject, consequent_predicate, new_truth, confidence
        )
        self._world.add_fact(conclusion)

        rid = fractal_fold([
            cantor_pair(1, int(RuleKind.MODUS_PONENS)),
            cantor_pair(2, antecedent.fact_id),
            cantor_pair(3, conclusion.fact_id),
        ])
        result = InferenceResult(
            rule=RuleKind.MODUS_PONENS,
            premise_ids=(antecedent.fact_id,),
            conclusion=conclusion,
            confidence=confidence,
            result_id=rid,
        )
        self._results.append(result)
        return result

    def apply_existential(
        self,
        judgment: Judgment,
        eval_result: EvalResult,
    ) -> InferenceResult:
        """From a judgment+evaluation, derive an existential fact.

        If the evaluation is confident enough, assert the proposition
        as a fact in the world model.
        """
        if eval_result.confidence >= 0.5:
            truth = eval_result.truth_state
        else:
            truth = TruthState.UNKNOWN

        conclusion = make_fact(
            subject=str(judgment.subject),
            predicate=str(judgment.predicate),
            truth_state=truth,
            confidence=eval_result.confidence,
        )
        self._world.add_fact(conclusion)

        rid = fractal_fold([
            cantor_pair(1, int(RuleKind.EXISTENTIAL)),
            cantor_pair(2, judgment.judgment_id),
            cantor_pair(3, eval_result.eval_id),
            cantor_pair(4, conclusion.fact_id),
        ])
        result = InferenceResult(
            rule=RuleKind.EXISTENTIAL,
            premise_ids=(judgment.judgment_id, eval_result.eval_id),
            conclusion=conclusion,
            confidence=eval_result.confidence,
            result_id=rid,
        )
        self._results.append(result)
        return result
