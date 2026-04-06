"""Epistemic mode hubs.

Labels how the knowledge about a lexeme / node is grounded:

  EMPIRICAL            — rooted in sensory / observable reality
  FORMAL               — logical or definitional, sense-independent
  MIXED                — both empirical and formal dimensions
  DISCOURSE_ANCHORED   — meaning fixed by discourse context
  STRUCTURALLY_DERIVED — meaning derived from structural relations alone
"""

from __future__ import annotations

from enum import IntEnum


class EpistemicMode(IntEnum):
    EMPIRICAL = 1
    FORMAL = 2
    MIXED = 3
    DISCOURSE_ANCHORED = 4
    STRUCTURALLY_DERIVED = 5


def epistemic_mode_id(mode: EpistemicMode) -> int:
    return int(mode)
