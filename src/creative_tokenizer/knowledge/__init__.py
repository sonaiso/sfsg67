"""Knowledge sub-package — upper ontology tools and epistemic engine.

Provides:
* :class:`RelationRegistry` / :func:`validate_concept` — concept gate
* :class:`EpistemicEngine` / :class:`EpistemicVerdict` — executable epistemic rules
"""

from .epistemic_engine import EpistemicEngine, EpistemicVerdict, SignificationStatus
from .relation_registry import (
    ConceptProposal,
    RelationEntry,
    RelationKind,
    RelationRegistry,
    validate_concept,
)

__all__ = [
    "ConceptProposal",
    "EpistemicEngine",
    "EpistemicVerdict",
    "RelationEntry",
    "RelationKind",
    "RelationRegistry",
    "SignificationStatus",
    "validate_concept",
]
