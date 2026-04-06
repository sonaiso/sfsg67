"""Ontological category and domain hubs.

Every lexeme links to an ontology hub:
  - JAMID (solid noun) → existence-class hubs (ENTITY, SUBSTANCE …)
  - MUSHTAQ (derived)  → process-class hubs (EVENT, PROCESS, AGENT …)

Domain hubs provide macro-groupings shared by many nodes:
  KAWN  (الكون)   — physical / cosmic
  INSAN (الإنسان) — human / social
  HAYAT (الحياة)  — living / biological
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair


class OntologyCategory(IntEnum):
    ENTITY = 1
    EVENT = 2
    STATE = 3
    ATTRIBUTE = 4
    RELATION = 5
    PROCESS = 6
    SUBSTANCE = 7
    AGENT = 8
    RESULT = 9


class DomainHub(IntEnum):
    KAWN = 1
    INSAN = 2
    HAYAT = 3


@dataclass(frozen=True, slots=True)
class OntologyNode:
    category: OntologyCategory
    domain: DomainHub
    hub_id: int  # π(category, domain)


def make_ontology_node(
    category: OntologyCategory,
    domain: DomainHub,
) -> OntologyNode:
    hub_id = cantor_pair(int(category), int(domain))
    return OntologyNode(category=category, domain=domain, hub_id=hub_id)
