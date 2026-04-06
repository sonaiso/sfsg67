from __future__ import annotations

import math
from collections.abc import Sequence


def phi(char: str) -> int:
    """Unicode code-point identity: φ(u) = ord(u)."""
    if len(char) != 1:
        raise ValueError(f"phi() requires a single character, got {char!r}")
    return ord(char)


def cantor_pair(x: int, y: int) -> int:
    """Cantor pairing function: π(x, y) = (x+y)(x+y+1)//2 + y.

    Bijectively maps two non-negative integers to one non-negative integer.
    """
    if x < 0 or y < 0:
        raise ValueError(
            f"cantor_pair requires non-negative integers, got ({x}, {y})"
        )
    s = x + y
    return s * (s + 1) // 2 + y


def invert_cantor_pair(z: int) -> tuple[int, int]:
    """Inverse of cantor_pair: returns (x, y) such that π(x, y) = z."""
    if z < 0:
        raise ValueError(
            f"invert_cantor_pair requires a non-negative integer, got {z}"
        )
    w = (math.isqrt(8 * z + 1) - 1) // 2
    t = w * (w + 1) // 2
    y = z - t
    x = w - y
    return x, y


def fractal_fold(values: Sequence[int]) -> int:
    """Fractal fold: F(x1,…,xn) = π(x1, F(x2,…,xn)).

    F([]) = 0, F([x]) = x.
    Order-sensitive: permutations produce distinct identities.
    """
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    return cantor_pair(values[0], fractal_fold(values[1:]))
