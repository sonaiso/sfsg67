"""Fractal graph node with proof identity vs storage identity.

Proof identity (proof_id):
    The full fractal integer rebuilt from all node components.
    Can always be reconstructed from (base_id, hub_ids, delta_id).

Storage identity (store_id):
    Compact integer = π(fractal_fold(sorted hub_ids), delta_id).
    Two nodes that share the same hubs and the same local delta share
    the same store_id — enabling row-level deduplication.

Constitutive edges vs overlay edges:
  hub_ids     — parent hub identities (constitutive, must form a DAG)
  overlay edges are separate TypedEdge objects and do not modify hub_ids.
"""

from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair, fractal_fold

_UNVIS = 0
_VIS = 1
_DONE = 2


@dataclass(frozen=True, slots=True)
class GraphNode:
    proof_id: int  # full reconstructible identity
    hub_ids: tuple[int, ...]  # constitutive parent hubs (sorted)
    delta_id: int  # local differences from hubs
    store_id: int  # compact: π(hub_fold, delta_id)


def make_graph_node(
    proof_id: int,
    hub_ids: list[int],
    delta_id: int = 0,
) -> GraphNode:
    """Build a GraphNode separating proof identity from storage identity.

    store_id = π( F(sorted hub_ids), delta_id )
    """
    sorted_hubs = sorted(hub_ids)
    hub_fold = fractal_fold(sorted_hubs) if sorted_hubs else 0
    store_id = cantor_pair(hub_fold, delta_id)
    return GraphNode(
        proof_id=proof_id,
        hub_ids=tuple(sorted_hubs),
        delta_id=delta_id,
        store_id=store_id,
    )


def is_dag_valid(nodes: list[GraphNode]) -> bool:
    """Return True iff the constitutive (hub) layer is acyclic.

    Uses DFS three-colour algorithm.  Only nodes whose proof_id appears in
    the provided list are checked; external singleton hubs are treated as
    safe sinks.
    """
    id_to_hubs: dict[int, tuple[int, ...]] = {
        n.proof_id: n.hub_ids for n in nodes
    }
    known: set[int] = set(id_to_hubs)
    state: dict[int, int] = {}

    def _visit(nid: int) -> bool:
        s = state.get(nid, _UNVIS)
        if s == _VIS:
            return False  # back-edge → cycle
        if s == _DONE:
            return True
        state[nid] = _VIS
        for hub in id_to_hubs.get(nid) or ():
            if hub in known and not _visit(hub):
                return False
        state[nid] = _DONE
        return True

    return all(_visit(n.proof_id) for n in nodes)
