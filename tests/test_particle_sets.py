"""Tests for particle_sets.py — particle classification and identity."""

from creative_tokenizer.morphology.particle_sets import (
    CONJUNCTIONS,
    NASIKHAAT,
    PREPOSITIONS,
    ParticleKind,
    make_particle,
    particle_id,
)


def test_make_particle_conjunction() -> None:
    p = make_particle("وَ", ParticleKind.CONJUNCTION)
    assert p.kind == ParticleKind.CONJUNCTION
    assert p.governance == 0


def test_make_particle_preposition() -> None:
    p = make_particle("فِي", ParticleKind.PREPOSITION, governance=3)
    assert p.kind == ParticleKind.PREPOSITION
    assert p.governance == 3


def test_particle_id_deterministic() -> None:
    p = make_particle("مِنْ", ParticleKind.PREPOSITION, governance=3)
    assert particle_id(p) == particle_id(p)


def test_particle_id_distinct_kind() -> None:
    p1 = make_particle("لَا", ParticleKind.NEGATION)
    p2 = make_particle("لَا", ParticleKind.CONJUNCTION)
    assert particle_id(p1) != particle_id(p2)


def test_particle_id_distinct_governance() -> None:
    p1 = make_particle("فِي", ParticleKind.PREPOSITION, governance=3)
    p2 = make_particle("فِي", ParticleKind.PREPOSITION, governance=0)
    assert particle_id(p1) != particle_id(p2)


def test_conjunctions_non_empty() -> None:
    assert len(CONJUNCTIONS) > 0


def test_prepositions_non_empty() -> None:
    assert len(PREPOSITIONS) > 0


def test_nasikhaat_non_empty() -> None:
    assert len(NASIKHAAT) > 0


def test_particle_id_distinct_surface() -> None:
    p1 = make_particle("مِنْ", ParticleKind.PREPOSITION, governance=3)
    p2 = make_particle("إِلَى", ParticleKind.PREPOSITION, governance=3)
    assert particle_id(p1) != particle_id(p2)
