"""Tests for the DAG interning layer."""

import pytest

from creative_tokenizer.morphology.dag_interning import DagStore


def test_intern_leaf_returns_stable_key() -> None:
    dag = DagStore()
    k1 = dag.intern_leaf(42)
    k2 = dag.intern_leaf(42)
    assert k1 == k2


def test_intern_leaf_distinct_values_get_distinct_keys() -> None:
    dag = DagStore()
    k1 = dag.intern_leaf(1)
    k2 = dag.intern_leaf(2)
    assert k1 != k2


def test_get_leaf() -> None:
    dag = DagStore()
    k = dag.intern_leaf(99)
    node = dag.get(k)
    assert node.label == 99
    assert node.children == ()
    assert node.key == k


def test_intern_node_deduplicates() -> None:
    dag = DagStore()
    a = dag.intern_leaf(10)
    b = dag.intern_leaf(20)
    n1 = dag.intern_node("pair", [a, b])
    n2 = dag.intern_node("pair", [a, b])
    assert n1 == n2


def test_intern_node_different_children_different_keys() -> None:
    dag = DagStore()
    a = dag.intern_leaf(10)
    b = dag.intern_leaf(20)
    c = dag.intern_leaf(30)
    n1 = dag.intern_node("pair", [a, b])
    n2 = dag.intern_node("pair", [a, c])
    assert n1 != n2


def test_intern_node_different_labels_different_keys() -> None:
    dag = DagStore()
    a = dag.intern_leaf(10)
    b = dag.intern_leaf(20)
    n1 = dag.intern_node("pair", [a, b])
    n2 = dag.intern_node("fold", [a, b])
    assert n1 != n2


def test_get_branch_node() -> None:
    dag = DagStore()
    a = dag.intern_leaf(1)
    b = dag.intern_leaf(2)
    k = dag.intern_node("pair", [a, b])
    node = dag.get(k)
    assert node.label == "pair"
    assert node.children == (a, b)


def test_get_unknown_key_raises() -> None:
    dag = DagStore()
    with pytest.raises(KeyError):
        dag.get(999)


def test_intern_node_unknown_child_raises() -> None:
    dag = DagStore()
    with pytest.raises(KeyError):
        dag.intern_node("bad", [999])


def test_len_counts_all_interned() -> None:
    dag = DagStore()
    assert len(dag) == 0
    a = dag.intern_leaf(1)
    assert len(dag) == 1
    dag.intern_leaf(2)
    assert len(dag) == 2
    dag.intern_node("pair", [a, dag.intern_leaf(3)])
    assert len(dag) == 4  # leaf(1), leaf(2), leaf(3), node


def test_contains() -> None:
    dag = DagStore()
    k = dag.intern_leaf(7)
    assert k in dag
    assert 999 not in dag


def test_keys_insertion_order() -> None:
    dag = DagStore()
    k1 = dag.intern_leaf(10)
    k2 = dag.intern_leaf(20)
    k3 = dag.intern_node("pair", [k1, k2])
    assert dag.keys() == [k1, k2, k3]


def test_intern_cantor_pair_convenience() -> None:
    dag = DagStore()
    a = dag.intern_leaf(3)
    b = dag.intern_leaf(7)
    k = dag.intern_cantor_pair(a, b)
    node = dag.get(k)
    assert node.label == "cantor_pair"
    assert node.children == (a, b)


def test_intern_cantor_pair_deduplicates() -> None:
    dag = DagStore()
    a = dag.intern_leaf(3)
    b = dag.intern_leaf(7)
    k1 = dag.intern_cantor_pair(a, b)
    k2 = dag.intern_cantor_pair(a, b)
    assert k1 == k2


def test_intern_fractal_fold_empty() -> None:
    dag = DagStore()
    k = dag.intern_fractal_fold([])
    node = dag.get(k)
    assert node.label == 0
    assert node.children == ()


def test_intern_fractal_fold_single_returns_element() -> None:
    dag = DagStore()
    a = dag.intern_leaf(42)
    k = dag.intern_fractal_fold([a])
    assert k == a


def test_intern_fractal_fold_multi() -> None:
    dag = DagStore()
    a = dag.intern_leaf(1)
    b = dag.intern_leaf(2)
    c = dag.intern_leaf(3)
    k = dag.intern_fractal_fold([a, b, c])
    node = dag.get(k)
    assert node.label == "fractal_fold"
    assert node.children == (a, b, c)


def test_intern_fractal_fold_deduplicates() -> None:
    dag = DagStore()
    a = dag.intern_leaf(1)
    b = dag.intern_leaf(2)
    k1 = dag.intern_fractal_fold([a, b])
    k2 = dag.intern_fractal_fold([a, b])
    assert k1 == k2


def test_deep_dag_structure() -> None:
    """Build a multi-level DAG and verify deduplication works throughout."""
    dag = DagStore()
    # Level 0: leaves
    leaves = [dag.intern_leaf(i) for i in range(5)]
    # Level 1: pair nodes
    p1 = dag.intern_cantor_pair(leaves[0], leaves[1])
    p2 = dag.intern_cantor_pair(leaves[2], leaves[3])
    # Level 2: fold
    fold = dag.intern_fractal_fold([p1, p2, leaves[4]])
    # Verify dedup
    assert dag.intern_fractal_fold([p1, p2, leaves[4]]) == fold
    # Verify structure
    node = dag.get(fold)
    assert node.label == "fractal_fold"
    assert len(node.children) == 3
