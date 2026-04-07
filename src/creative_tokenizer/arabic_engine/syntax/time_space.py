"""Temporal and spatial anchoring layer (V2).

Anchors propositions to time and space coordinates.  Time is modeled as
a combination of tense + aspect + reference point; space as a location tag.

This implements the time/space dimensions of the judgment vector:
  p = (subject, predicate, object, time, space, polarity)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

__all__ = ["TimeAnchor", "TimeSpace", "build_time_space"]


class TimeAnchor(IntEnum):
    """Tense/aspect anchor for a proposition."""

    PAST = 1  # ماضٍ
    PRESENT = 2  # مضارع
    FUTURE = 3  # مستقبل
    TIMELESS = 4  # مطلق (no temporal anchor)


class SpaceAnchor(IntEnum):
    """Spatial anchor for a proposition."""

    HERE = 1  # هنا — deictic proximal
    THERE = 2  # هناك — deictic distal
    NAMED = 3  # مكان معيّن — named location
    UNSPECIFIED = 4  # لا تحديد


@dataclass(frozen=True, slots=True)
class TimeSpace:
    """Combined temporal-spatial anchor.

    Attributes
    ----------
    time_anchor:   tense/aspect category
    space_anchor:  spatial location category
    time_id:       numeric encoding of time anchor
    space_id:      numeric encoding of space anchor
    ts_id:         combined fractal identity
    """

    time_anchor: TimeAnchor
    space_anchor: SpaceAnchor
    time_id: int
    space_id: int
    ts_id: int


_PAST_PREFIXES = ("فَعَلَ", "فَعِلَ", "فَعُلَ")
_PRESENT_PREFIXES = ("يَفْعَلُ", "يَفْعِلُ")


def _infer_time(pos: str, pattern: str) -> TimeAnchor:
    """Infer temporal anchor from POS and pattern heuristics."""
    if pos == "verb":
        if pattern.startswith(_PAST_PREFIXES):
            return TimeAnchor.PAST
        if pattern.startswith(_PRESENT_PREFIXES):
            return TimeAnchor.PRESENT
    return TimeAnchor.TIMELESS


def build_time_space(
    pos: str = "",
    pattern: str = "",
    time_anchor: TimeAnchor | None = None,
    space_anchor: SpaceAnchor = SpaceAnchor.UNSPECIFIED,
) -> TimeSpace:
    """Build a TimeSpace anchor for a proposition.

    If time_anchor is not provided, it is inferred from POS and pattern.
    """
    ta = time_anchor if time_anchor is not None else _infer_time(pos, pattern)
    time_id = int(ta)
    space_id = int(space_anchor)
    ts_id = fractal_fold([
        cantor_pair(1, time_id),
        cantor_pair(2, space_id),
    ])
    return TimeSpace(
        time_anchor=ta,
        space_anchor=space_anchor,
        time_id=time_id,
        space_id=space_id,
        ts_id=ts_id,
    )
