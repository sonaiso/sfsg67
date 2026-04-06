"""Bayān record — one entry in the explanation store.

The bayān store does not repeat facts from the data store; it records *why*
a particular analysis was chosen.  Each record answers:

  - Why was the literal reading preferred / blocked?
  - Which qarina (قرينة صارفة) deflected interpretation to figurative?
  - Why was this signified chosen in a polysemous context?
  - How was the semantic conflict resolved?
  - What economy principle justified the structural choice?

  reason_chain_id = F(π(i, rule_id) for each rule in rule_path)
                    or 0 if rule_path is empty
  explanation_id  = π(target_node_id, reason_chain_id)

literal_blocking_condition = 0  means the literal reading was NOT blocked
                                 (حقيقة applied).
qarina_id = 0 means no قرينة صارفة was needed.
"""

from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair, fractal_fold


@dataclass(frozen=True, slots=True)
class BayanRecord:
    explanation_id: int
    target_node_id: int
    rule_path: tuple[int, ...]       # ordered rule ids applied (empty = default literal)
    reason_chain_id: int             # F(rule_path) or 0
    economy_justification: int       # economy principle id; 0 = no special economy
    literal_blocking_condition: int  # 0 = literal holds; >0 = blocked
    qarina_id: int                   # 0 = no qarina
    semantic_rank: int               # final rank of chosen path (1 = highest/winner)
    traceback_ids: tuple[int, ...]   # ids of nodes / edges consulted


def make_bayan(
    target_node_id: int,
    rule_path: list[int],
    economy_justification: int = 0,
    literal_blocking_condition: int = 0,
    qarina_id: int = 0,
    semantic_rank: int = 1,
    traceback_ids: list[int] | None = None,
) -> BayanRecord:
    reason_chain_id = (
        fractal_fold([cantor_pair(i + 1, r) for i, r in enumerate(rule_path)])
        if rule_path
        else 0
    )
    explanation_id = cantor_pair(target_node_id, reason_chain_id)
    tb: tuple[int, ...] = tuple(traceback_ids) if traceback_ids else ()
    return BayanRecord(
        explanation_id=explanation_id,
        target_node_id=target_node_id,
        rule_path=tuple(rule_path),
        reason_chain_id=reason_chain_id,
        economy_justification=economy_justification,
        literal_blocking_condition=literal_blocking_condition,
        qarina_id=qarina_id,
        semantic_rank=semantic_rank,
        traceback_ids=tb,
    )
