"""DAG interning layer for fractal identities.

Provides compact deduplication and storage of fractal identity subtrees as a
directed acyclic graph (DAG).  Each unique ``(label, children…)`` node is
stored exactly once and identified by a stable integer key.  This allows
efficient comparison, storage, and retrieval of word-identity subtrees.

Usage::

    dag = DagStore()
    leaf_a = dag.intern_leaf(42)
    leaf_b = dag.intern_leaf(99)
    branch = dag.intern_node("pair", [leaf_a, leaf_b])

    # Same structure always returns the same key
    assert dag.intern_node("pair", [leaf_a, leaf_b]) == branch

    # Lookup
    node = dag.get(branch)
    assert node.label == "pair"
    assert node.children == (leaf_a, leaf_b)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DagNode:
    """An interned node in the DAG.

    Attributes:
        key:      unique integer identity assigned by the ``DagStore``.
        label:    a semantic label (e.g. ``"cantor_pair"``, ``"surface"``, or
                  an integer value for leaf nodes).
        children: tuple of child node keys (empty for leaves).
    """

    key: int
    label: str | int
    children: tuple[int, ...]


class DagStore:
    """Intern and deduplicate DAG nodes.

    Two nodes with the same ``(label, children)`` are guaranteed to share a
    single key.  Keys are positive integers assigned in insertion order.
    """

    def __init__(self) -> None:
        self._signature_to_key: dict[tuple[str | int, tuple[int, ...]], int] = {}
        self._key_to_node: dict[int, DagNode] = {}
        self._next_key: int = 1

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def intern_leaf(self, value: int) -> int:
        """Intern a leaf node carrying an integer *value* (no children).

        Returns the stable key for this leaf.
        """
        return self._intern(value, ())

    def intern_node(self, label: str, children: list[int]) -> int:
        """Intern a branch node with *label* and *children* keys.

        Returns the stable key for this node.

        Raises ``KeyError`` if any child key is unknown.
        """
        for child_key in children:
            if child_key not in self._key_to_node:
                raise KeyError(f"unknown child key {child_key}")
        return self._intern(label, tuple(children))

    def get(self, key: int) -> DagNode:
        """Retrieve the ``DagNode`` for *key*.

        Raises ``KeyError`` if *key* is unknown.
        """
        return self._key_to_node[key]

    def __len__(self) -> int:
        """Number of interned nodes."""
        return len(self._key_to_node)

    def __contains__(self, key: int) -> bool:
        return key in self._key_to_node

    def keys(self) -> list[int]:
        """All interned keys in insertion order."""
        return list(self._key_to_node)

    # ------------------------------------------------------------------
    # Bulk helpers
    # ------------------------------------------------------------------

    def intern_cantor_pair(self, left: int, right: int) -> int:
        """Intern a ``cantor_pair`` node with two child keys.

        This is a convenience wrapper for the common pattern of interning a
        binary pair node.
        """
        return self.intern_node("cantor_pair", [left, right])

    def intern_fractal_fold(self, child_keys: list[int]) -> int:
        """Intern a ``fractal_fold`` node over a list of child keys.

        Empty lists produce a leaf with value 0 (matching ``fractal_fold([])``).
        Single-element lists return the element itself (no wrapper node).
        """
        if not child_keys:
            return self.intern_leaf(0)
        if len(child_keys) == 1:
            return child_keys[0]
        return self.intern_node("fractal_fold", child_keys)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _intern(self, label: str | int, children: tuple[int, ...]) -> int:
        sig = (label, children)
        existing = self._signature_to_key.get(sig)
        if existing is not None:
            return existing
        key = self._next_key
        self._next_key += 1
        self._signature_to_key[sig] = key
        self._key_to_node[key] = DagNode(key=key, label=label, children=children)
        return key
