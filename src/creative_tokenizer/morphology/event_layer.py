"""Event layer (ℰ) — §7 of the formal hierarchical specification.

An event is an independent semantic entity that is *not* collapsed into a
verb or a masdar.  It has its own identity layer:

    e = (event_type, tense, aspect, agency, transitivity,
         count, gender, definiteness)

The key function:

    Φ_event : ℛ × 𝒲_verb → ℰ

maps a root and a verb pattern to a structured event value.

This layer is crucial because it makes the verb–root–pattern triple yield
a *controlled event value* rather than leaving event semantics implicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold
from .root_pattern import Pattern, Root, pattern_id, root_id

# ---------------------------------------------------------------------------
# Event feature enums
# ---------------------------------------------------------------------------


class EventType(IntEnum):
    """Broad semantic type of the event — §7."""

    ACTION = 1  # حدث فعلي
    STATE = 2  # حالة
    PROCESS = 3  # صيرورة
    ACHIEVEMENT = 4  # إنجاز (punctual)
    ACCOMPLISHMENT = 5  # تحقيق (durative + telic)


class Tense(IntEnum):
    """Temporal anchoring of the event."""

    PAST = 1
    PRESENT = 2
    FUTURE = 3
    UNANCHORED = 0  # masdar / infinitive — no temporal fixing


class Aspect(IntEnum):
    """Aspectual contour of the event."""

    PERFECTIVE = 1
    IMPERFECTIVE = 2
    PROGRESSIVE = 3
    HABITUAL = 4
    UNSPECIFIED = 0


class Agency(IntEnum):
    """Agent control over the event."""

    VOLUNTARY = 1  # إرادي
    INVOLUNTARY = 2  # لا إرادي
    NATURAL = 3  # طبيعي
    UNSPECIFIED = 0


class Transitivity(IntEnum):
    """Argument-structure transitivity."""

    INTRANSITIVE = 1  # لازم
    TRANSITIVE = 2  # متعدٍّ لواحد
    DITRANSITIVE = 3  # متعدٍّ لاثنين
    TRITRANSITIVE = 4  # متعدٍّ لثلاثة
    UNSPECIFIED = 0


class EventCount(IntEnum):
    """Number / quantification of the event occurrence."""

    ONCE = 1  # مرة
    REPEATED = 2  # تكرار
    HABITUAL = 3  # عادة
    UNSPECIFIED = 0


class EventGender(IntEnum):
    """Grammatical gender agreement of the event predicate."""

    MASCULINE = 1
    FEMININE = 2
    UNSPECIFIED = 0


class EventDefiniteness(IntEnum):
    """Definiteness of the event nominalisation (masdar context)."""

    DEFINITE = 1
    INDEFINITE = 2
    UNSPECIFIED = 0


# ---------------------------------------------------------------------------
# Event dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Event:
    """A structured event value — §7.

    Each field corresponds to one dimension of event semantics.
    """

    event_type: EventType
    tense: Tense
    aspect: Aspect
    agency: Agency
    transitivity: Transitivity
    count: EventCount
    gender: EventGender
    definiteness: EventDefiniteness


# ---------------------------------------------------------------------------
# Event identity
# ---------------------------------------------------------------------------


def event_id(evt: Event) -> int:
    """Fractal identity of an event.

    e_id = F(event_type, tense, aspect, agency, transitivity,
             count, gender, definiteness)
    """
    return fractal_fold(
        [
            int(evt.event_type),
            int(evt.tense),
            int(evt.aspect),
            int(evt.agency),
            int(evt.transitivity),
            int(evt.count),
            int(evt.gender),
            int(evt.definiteness),
        ]
    )


# ---------------------------------------------------------------------------
# §7  Φ_event : ℛ × 𝒲_verb → ℰ
# ---------------------------------------------------------------------------


def phi_event(
    root: Root,
    pat: Pattern,
    event_type: EventType = EventType.ACTION,
    tense: Tense = Tense.UNANCHORED,
    aspect: Aspect = Aspect.UNSPECIFIED,
    agency: Agency = Agency.UNSPECIFIED,
    transitivity: Transitivity = Transitivity.UNSPECIFIED,
    count: EventCount = EventCount.UNSPECIFIED,
    gender: EventGender = EventGender.UNSPECIFIED,
    definiteness: EventDefiniteness = EventDefiniteness.UNSPECIFIED,
) -> Event:
    """Map a root × verb-pattern to a structured event.

    The caller provides the semantic dimensions that are known; the rest
    default to UNSPECIFIED / UNANCHORED.  The identity of the resulting
    event embeds the root and pattern identities.
    """
    return Event(
        event_type=event_type,
        tense=tense,
        aspect=aspect,
        agency=agency,
        transitivity=transitivity,
        count=count,
        gender=gender,
        definiteness=definiteness,
    )


def phi_event_id(root: Root, pat: Pattern, evt: Event) -> int:
    """Combined identity: π(root_id, π(pattern_id, event_id)).

    This is the value of Φ_event(r, w) after all dimensions are fixed.
    """
    return cantor_pair(root_id(root), cantor_pair(pattern_id(pat), event_id(evt)))
