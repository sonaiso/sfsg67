from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class ConstraintTag(IntEnum):
    """Morpho-syntactic constraint tags.  Values are stable across versions."""

    DIPTOTE = 1            # 1=diptote (ممنوع من الصرف)
    TANWEEN_BLOCKED = 2    # 1=tanween blocked
    GENITIVE_BY_FATHA = 3  # 1=genitive expressed by fatha not kasra
    IDAFA_REQUIRED = 4     # 1=must be in construct state to be well-formed
    NUN_STATE = 5          # 1=nun present, 0=nun deleted
    DECLINABLE = 6         # 1=declinable (معرب), 0=indeclinable (مبني)
    DEFINITE = 7           # 1=definite, 0=indefinite
    CASE_CARRIER = 8       # carrier tag value (from CarrierTag)
    MOOD_CARRIER = 9       # mood carrier tag value (from CarrierTag)
    BUILT_STATE = 10       # 1=built/frozen (مبني على …)
    TANWEEN_PRESENT = 11   # 1=tanween present (has nunation)


def constraint_envelope(constraints: dict[ConstraintTag, int]) -> int:
    """Ξ(w) = F(π(tag, value), …) sorted by tag for identity stability.

    Returns 0 for an empty constraint set.
    Adding new ConstraintTag values does not change existing envelopes.
    """
    if not constraints:
        return 0
    pairs = sorted(constraints.items())
    return fractal_fold([cantor_pair(int(tag), value) for tag, value in pairs])
