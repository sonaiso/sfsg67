from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class FeatureTag(IntEnum):
    """Stable morpho-semantic feature tags.  Values must not be reused."""

    TENSE = 1
    ASPECT = 2
    TRANSITIVITY = 3
    CAUSATIVITY = 4
    RESULTATIVITY = 5
    TEMPORALIZATION = 6
    LOCALIZATION = 7
    DIMINUTION = 8
    AUGMENTATION = 9
    NISBA = 10
    MASDAR_INDUSTRIAL = 11
    UNIT = 12
    PLURALITY = 13
    FEMININE = 14
    MASCULINE = 15
    PASSIVE = 16


def semantic_envelope(features: dict[FeatureTag, int]) -> int:
    """Θ = F(π(t1,v1), π(t2,v2), ...) sorted by tag for identity stability.

    Sorting ensures Θ is independent of dict insertion order.
    Returns 0 for an empty feature set.
    New FeatureTag values can be added without changing existing envelopes.
    """
    if not features:
        return 0
    pairs = sorted(features.items())
    return fractal_fold([cantor_pair(int(tag), value) for tag, value in pairs])
