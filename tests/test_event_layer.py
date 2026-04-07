"""Tests for event_layer.py — event semantics and Φ_event."""

from creative_tokenizer.morphology.event_layer import (
    Agency,
    Aspect,
    Event,
    EventCount,
    EventDefiniteness,
    EventGender,
    EventType,
    Tense,
    Transitivity,
    event_id,
    phi_event,
    phi_event_id,
)
from creative_tokenizer.morphology.root_pattern import (
    VerbPatternKind,
    make_root,
    make_verb_pattern,
)


def test_phi_event_defaults() -> None:
    """Phi_event with defaults produces an ACTION event."""
    root = make_root(("ك", "ت", "ب"))
    pat = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    evt = phi_event(root, pat)
    assert evt.event_type == EventType.ACTION
    assert evt.tense == Tense.UNANCHORED
    assert evt.aspect == Aspect.UNSPECIFIED


def test_phi_event_custom() -> None:
    root = make_root(("ذ", "ه", "ب"))
    pat = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    evt = phi_event(
        root,
        pat,
        event_type=EventType.ACTION,
        tense=Tense.PAST,
        aspect=Aspect.PERFECTIVE,
        transitivity=Transitivity.INTRANSITIVE,
    )
    assert evt.tense == Tense.PAST
    assert evt.aspect == Aspect.PERFECTIVE
    assert evt.transitivity == Transitivity.INTRANSITIVE


def test_event_id_deterministic() -> None:
    evt = Event(
        event_type=EventType.ACTION,
        tense=Tense.PAST,
        aspect=Aspect.PERFECTIVE,
        agency=Agency.VOLUNTARY,
        transitivity=Transitivity.TRANSITIVE,
        count=EventCount.ONCE,
        gender=EventGender.MASCULINE,
        definiteness=EventDefiniteness.UNSPECIFIED,
    )
    assert event_id(evt) == event_id(evt)


def test_event_id_distinct_types() -> None:
    e1 = Event(
        EventType.ACTION,
        Tense.PAST,
        Aspect.PERFECTIVE,
        Agency.UNSPECIFIED,
        Transitivity.UNSPECIFIED,
        EventCount.UNSPECIFIED,
        EventGender.UNSPECIFIED,
        EventDefiniteness.UNSPECIFIED,
    )
    e2 = Event(
        EventType.STATE,
        Tense.PAST,
        Aspect.PERFECTIVE,
        Agency.UNSPECIFIED,
        Transitivity.UNSPECIFIED,
        EventCount.UNSPECIFIED,
        EventGender.UNSPECIFIED,
        EventDefiniteness.UNSPECIFIED,
    )
    assert event_id(e1) != event_id(e2)


def test_phi_event_id_embeds_root_and_pattern() -> None:
    """The combined identity should differ when root or pattern change."""
    r1 = make_root(("ك", "ت", "ب"))
    r2 = make_root(("ذ", "ه", "ب"))
    pat = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    evt = Event(
        EventType.ACTION,
        Tense.PAST,
        Aspect.PERFECTIVE,
        Agency.UNSPECIFIED,
        Transitivity.UNSPECIFIED,
        EventCount.UNSPECIFIED,
        EventGender.UNSPECIFIED,
        EventDefiniteness.UNSPECIFIED,
    )
    id1 = phi_event_id(r1, pat, evt)
    id2 = phi_event_id(r2, pat, evt)
    assert id1 != id2


def test_phi_event_id_deterministic() -> None:
    root = make_root(("ك", "ت", "ب"))
    pat = make_verb_pattern("فَعَلَ", VerbPatternKind.MUJARRAD)
    evt = phi_event(root, pat)
    assert phi_event_id(root, pat, evt) == phi_event_id(root, pat, evt)
