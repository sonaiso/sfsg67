"""Cognitive domain nodes — bridging language to experience.

Three macro-domains cover the full scope of represented knowledge:

  PHYSICAL   — sensory / empirical events, states, objects, causal relations
  FORMAL     — mathematical / logical structures (unity, order, conditions …)
  DISCOURSE  — intentional / social / speech-act layer

PhysicalTag  → values 1-11  (motion, heat, light …)
FormalTag    → values 1-15  (unity, order, condition, necessity …)
DiscourseTag → values 1-12  (intent, address, judgment …)

CognitiveConcept.concept_id = π(domain, tag)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair


class CognitiveDomain(IntEnum):
    PHYSICAL = 1
    FORMAL = 2
    DISCOURSE = 3


class PhysicalTag(IntEnum):
    MOTION = 1
    HEAT = 2
    LIGHT = 3
    MASS = 4
    FALL = 5
    GROWTH = 6
    CHANGE = 7
    LOCATION = 8
    TIME_ENTITY = 9
    PHYSICAL_CAUSE = 10
    PHYSICAL_EFFECT = 11


class FormalTag(IntEnum):
    UNITY = 1
    MULTIPLICITY = 2
    ORDER = 3
    CONDITION = 4
    GOAL = 5
    UNIVERSALITY = 6
    PARTICULARITY = 7
    EQUALITY = 8
    DIFFERENCE = 9
    PROPORTION = 10
    NECESSITY = 11
    POSSIBILITY = 12
    IMPOSSIBILITY = 13
    CONSTRAINT = 14
    MEASURE = 15


class DiscourseTag(IntEnum):
    INTENT = 1
    ADDRESS = 2
    REFERENCE = 3
    REQUEST = 4
    PROHIBITION = 5
    ASSERTION = 6
    PROMISE = 7
    WARNING = 8
    CONVENTION = 9
    TERMINOLOGY = 10
    JUDGMENT = 11
    VALUE = 12


@dataclass(frozen=True, slots=True)
class CognitiveConcept:
    domain: CognitiveDomain
    tag: int  # value from PhysicalTag | FormalTag | DiscourseTag
    concept_id: int  # π(domain, tag)


def make_cognitive(domain: CognitiveDomain, tag: int) -> CognitiveConcept:
    """Build a CognitiveConcept node.  Pass IntEnum tag values directly."""
    return CognitiveConcept(
        domain=domain,
        tag=tag,
        concept_id=cantor_pair(int(domain), tag),
    )
