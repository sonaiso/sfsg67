"""Dalāla (semantic linkage) validation.

D: T × C → {0,1} × [0,1]

Validates the semantic bond between a signifier (Token) and a signified
(Concept), producing acceptance/rejection and a confidence score.

Dalāla types (from Arabic semantics):
  mutabaqa  — full primary denotation
  tadammun  — partial / entailed component
  iltizam   — conditional inferential implicature
  isnad     — predicative attribution (verb↔subject, subject↔predicate)
  taqyid    — restrictive qualification (adjective, iḍāfa, adverb)
  ihala     — referential linkage (pronoun, demonstrative)
"""

from __future__ import annotations

from creative_tokenizer.arabic_engine.core.enums import DalalType, SemanticType
from creative_tokenizer.arabic_engine.core.types import (
    Concept,
    DalalLink,
    Token,
    make_dalal_link,
)

__all__ = ["validate_dalala"]


def _mutabaqa_score(token: Token, concept: Concept) -> float:
    """Full-match confidence: high when POS aligns with semantic type."""
    if token.pos == "verb" and concept.semantic_type == SemanticType.EVENT:
        return 1.0
    if token.pos == "noun" and concept.semantic_type == SemanticType.ENTITY:
        return 1.0
    if token.pos == "adj" and concept.semantic_type == SemanticType.ATTRIBUTE:
        return 0.9
    return 0.5


def _tadammun_score(token: Token, concept: Concept) -> float:
    """Entailment score: based on root/pattern alignment."""
    if token.root and any(v == token.root for _, v in concept.properties):
        return 0.8
    return 0.4


def _iltizam_score(_token: Token, _concept: Concept) -> float:
    """Inferential implicature: conservative default."""
    return 0.3


def validate_dalala(
    token: Token,
    concept: Concept,
    dalal_type: DalalType,
) -> DalalLink:
    """Validate a dalāla link between token and concept.

    Returns a DalalLink with acceptance status and confidence score.
    The validation applies the mutabaqa/tadammun/iltizam hierarchy
    and the isnad/taqyid compositional relations.
    """
    if dalal_type == DalalType.MUTABAQA:
        confidence = _mutabaqa_score(token, concept)
    elif dalal_type == DalalType.TADAMMUN:
        confidence = _tadammun_score(token, concept)
    elif dalal_type == DalalType.ILTIZAM:
        confidence = _iltizam_score(token, concept)
    elif dalal_type == DalalType.ISNAD:
        # Predicative: verb-subject or subject-predicate
        confidence = 0.9 if token.pos in ("verb", "noun") else 0.5
    elif dalal_type == DalalType.TAQYID:
        # Restrictive: adjective-noun, iḍāfa, adverb
        confidence = 0.85 if token.pos in ("adj", "noun") else 0.4
    elif dalal_type == DalalType.IHALA:
        # Referential
        confidence = 0.7
    else:
        confidence = 0.5

    accepted = confidence >= 0.3

    return make_dalal_link(
        token_id=token.token_id,
        concept_id=concept.concept_id,
        dalal_type=dalal_type,
        accepted=accepted,
        confidence=confidence,
    )
