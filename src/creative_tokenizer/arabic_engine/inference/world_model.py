"""World model for evaluation context (V2).

W in E: P × W → V

Maintains a set of known facts against which propositions are evaluated.
Each fact is a (subject, predicate, truth_state) triple with a confidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

from ..core.enums import TruthState

__all__ = ["Fact", "WorldModel"]


@dataclass(frozen=True, slots=True)
class Fact:
    """A single fact in the world model.

    Attributes
    ----------
    subject:     subject identifier or label
    predicate:   predicate identifier or label
    truth_state: epistemic truth value
    confidence:  certainty level in [0.0, 1.0]
    fact_id:     stable fractal identity
    """

    subject: str
    predicate: str
    truth_state: TruthState
    confidence: float
    fact_id: int


def make_fact(
    subject: str,
    predicate: str,
    truth_state: TruthState = TruthState.PROBABLE,
    confidence: float = 0.8,
) -> Fact:
    """Build a Fact with a deterministic fractal identity."""
    fid = fractal_fold([
        cantor_pair(1, sum(ord(c) for c in subject)),
        cantor_pair(2, sum(ord(c) for c in predicate)),
        cantor_pair(3, int(truth_state)),
        cantor_pair(4, int(confidence * 1000)),
    ])
    return Fact(
        subject=subject,
        predicate=predicate,
        truth_state=truth_state,
        confidence=confidence,
        fact_id=fid,
    )


class WorldModel:
    """A mutable collection of facts representing world state.

    Used as the W parameter in evaluation: E: P × W → V.
    """

    def __init__(self) -> None:
        self._facts: dict[int, Fact] = {}

    def add_fact(self, fact: Fact) -> None:
        """Add or update a fact."""
        self._facts[fact.fact_id] = fact

    def add(
        self,
        subject: str,
        predicate: str,
        truth_state: TruthState = TruthState.PROBABLE,
        confidence: float = 0.8,
    ) -> Fact:
        """Convenience: create and add a fact in one step."""
        f = make_fact(subject, predicate, truth_state, confidence)
        self.add_fact(f)
        return f

    def lookup(self, subject: str, predicate: str) -> Fact | None:
        """Find a fact matching subject and predicate."""
        for f in self._facts.values():
            if f.subject == subject and f.predicate == predicate:
                return f
        return None

    def all_facts(self) -> tuple[Fact, ...]:
        """Return all facts as a tuple."""
        return tuple(self._facts.values())

    def __len__(self) -> int:
        return len(self._facts)

    def __contains__(self, fact_id: int) -> bool:
        return fact_id in self._facts
