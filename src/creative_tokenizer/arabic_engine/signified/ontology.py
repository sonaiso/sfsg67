"""Ontological concept mapping (المطابقة الأنطولوجية).

O: T → C   where C = (concept_id, semantic_type_id, property_vector)

Maps lexical closure tokens to ontological concepts.  The five categories
are: entity (ذات), event (حدث), attribute (صفة), relation (نسبة),
norm (حكم).
"""

from __future__ import annotations

from creative_tokenizer.arabic_engine.core.enums import SemanticType
from creative_tokenizer.arabic_engine.core.types import Concept, Token, make_concept

__all__ = ["map_to_ontology"]


# ── POS → SemanticType heuristic ──────────────────────────────────────

_POS_MAP: dict[str, SemanticType] = {
    "verb": SemanticType.EVENT,
    "noun": SemanticType.ENTITY,
    "adj": SemanticType.ATTRIBUTE,
    "particle": SemanticType.RELATION,
    "unknown": SemanticType.ENTITY,
}


def _infer_semantic_type(pos: str) -> SemanticType:
    return _POS_MAP.get(pos, SemanticType.ENTITY)


def map_to_ontology(token: Token) -> Concept:
    """Map a Token to its ontological Concept.

    Uses POS as primary heuristic, with root-based refinement for
    known verbal/nominal patterns.
    """
    sem_type = _infer_semantic_type(token.pos)

    # Build property vector from token features
    props: list[tuple[str, str]] = [
        ("root", token.root),
        ("pattern", token.pattern),
        ("pos", token.pos),
    ]
    for feat in token.features:
        if "=" in feat:
            key, val = feat.split("=", 1)
            props.append((key, val))
        else:
            props.append(("feature", feat))

    # Construct bilingual labels
    label_ar = token.lemma
    label_en = f"{token.lemma}[{sem_type.name.lower()}]"

    return make_concept(
        label_ar=label_ar,
        label_en=label_en,
        semantic_type=sem_type,
        properties=tuple(props),
    )
