from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class RoleTag(IntEnum):
    """Argument role tags for the relational frame Γ.  Values are stable."""

    EVENT = 1
    AGENT = 2
    PATIENT = 3
    CAUSE = 4
    THEME = 5
    LOCATION = 6
    TIME = 7


def relation_frame(roles: dict[RoleTag, int]) -> int:
    """Γ = F(π(role, value), ...) sorted by role for identity stability.

    Encodes the argument-role template of the word, not the filled arguments.
    Returns 0 for an empty role set.
    New RoleTag values can be added without changing existing frames.
    """
    if not roles:
        return 0
    pairs = sorted(roles.items())
    return fractal_fold([cantor_pair(int(role), value) for role, value in pairs])
