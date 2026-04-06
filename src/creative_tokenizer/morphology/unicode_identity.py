from __future__ import annotations

from .fractal_storage import fractal_fold, phi


def unicode_surface(text: str) -> int:
    """U(w) = F(φ(u1), φ(u2), ..., φ(un)).

    Encodes the full raw Unicode surface without discarding any code point.
    The identity is order-sensitive and preserves every character position.
    Returns 0 for empty text.
    """
    if not text:
        return 0
    return fractal_fold([phi(c) for c in text])
