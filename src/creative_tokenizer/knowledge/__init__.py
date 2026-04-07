"""Knowledge sub-package — upper ontology tools and epistemic engine.

Provides:
* :class:`RelationRegistry` / :func:`validate_concept` — concept gate
* :class:`EpistemicEngine` / :class:`EpistemicVerdict` — executable epistemic rules
* :func:`vertical_slice` — complete pipeline from Unicode to classification
"""

from .epistemic_engine import EpistemicEngine, EpistemicVerdict, SignificationStatus
from .relation_registry import (
    ConceptProposal,
    RelationEntry,
    RelationKind,
    RelationRegistry,
    validate_concept,
)
from .vertical_slice import SliceResult, vertical_slice

__all__ = [
    "ConceptProposal",
    "EpistemicEngine",
    "EpistemicVerdict",
    "RelationEntry",
    "RelationKind",
    "RelationRegistry",
    "SignificationStatus",
    "SliceResult",
    "validate_concept",
    "vertical_slice",
]
