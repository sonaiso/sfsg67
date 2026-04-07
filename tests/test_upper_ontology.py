"""Tests for the upper ontology — nodes, layers, transitions, constraints, chain."""

from creative_tokenizer.morphology.upper_ontology import (
    GOVERNING_CONSTRAINTS,
    MACRO_LAYERS,
    UPPER_NODES,
    UPPER_TRANSITIONS,
    ChainMode,
    ConstraintIndex,
    MacroLayerIndex,
    NodeIndex,
    TransitionKind,
    all_constraints,
    all_macro_layers,
    all_transitions,
    all_upper_nodes,
    chain_identity,
    governing_constraint,
    is_circular,
    macro_layer,
    transition_for,
    upper_node,
)

# ── Node basics ───────────────────────────────────────────────────────


class TestNodes:
    def test_twelve_nodes(self):
        assert len(UPPER_NODES) == 12

    def test_node_lookup(self):
        n = upper_node(NodeIndex.REALITY)
        assert n.label_en == "Reality"
        assert n.label_ar == "الواقع"

    def test_all_upper_nodes_returns_same_tuple(self):
        assert all_upper_nodes() is UPPER_NODES

    def test_node_ids_unique(self):
        ids = [n.node_id for n in UPPER_NODES]
        assert len(ids) == len(set(ids))

    def test_node_ids_stable(self):
        """Calling upper_node twice returns the same id."""
        a = upper_node(NodeIndex.BINDING)
        b = upper_node(NodeIndex.BINDING)
        assert a.node_id == b.node_id

    def test_first_node_is_reality(self):
        assert UPPER_NODES[0].index == NodeIndex.REALITY

    def test_last_node_is_outcome(self):
        assert UPPER_NODES[-1].index == NodeIndex.OUTCOME

    def test_node_ordering(self):
        for i, node in enumerate(UPPER_NODES):
            assert int(node.index) == i


# ── Transitions ───────────────────────────────────────────────────────


class TestTransitions:
    def test_twelve_transitions(self):
        """Eleven forward + one feedback = twelve."""
        assert len(UPPER_TRANSITIONS) == 12

    def test_transition_ids_unique(self):
        ids = [t.transition_id for t in UPPER_TRANSITIONS]
        assert len(ids) == len(set(ids))

    def test_first_transition_is_subject(self):
        t = UPPER_TRANSITIONS[0]
        assert t.kind == TransitionKind.SUBJECT
        assert t.source == NodeIndex.REALITY
        assert t.target == NodeIndex.SENSE

    def test_feedback_edge(self):
        fb = UPPER_TRANSITIONS[-1]
        assert fb.kind == TransitionKind.FEEDBACK
        assert fb.source == NodeIndex.OUTCOME
        assert fb.target == NodeIndex.PRIOR_KNOWLEDGE

    def test_chain_continuity(self):
        """Each forward transition's target equals the next transition's source."""
        forward = UPPER_TRANSITIONS[:11]
        for i in range(len(forward) - 1):
            assert forward[i].target == forward[i + 1].source

    def test_transition_for_lookup(self):
        t = transition_for(TransitionKind.EVALUATE)
        assert t.source == NodeIndex.TRUTH_VALUE
        assert t.target == NodeIndex.GUIDANCE

    def test_all_transitions_returns_same_tuple(self):
        assert all_transitions() is UPPER_TRANSITIONS


# ── Macro layers ──────────────────────────────────────────────────────


class TestMacroLayers:
    def test_ten_layers(self):
        assert len(MACRO_LAYERS) == 10

    def test_layer_lookup(self):
        ml = macro_layer(MacroLayerIndex.STANDARD)
        assert ml.label_en == "Standard"
        assert "حق" in ml.concepts_ar
        assert "باطل" in ml.concepts_ar

    def test_layer_ids_unique(self):
        ids = [ml.layer_id for ml in MACRO_LAYERS]
        assert len(ids) == len(set(ids))

    def test_all_macro_layers_returns_same_tuple(self):
        assert all_macro_layers() is MACRO_LAYERS

    def test_existence_layer_concepts(self):
        ml = macro_layer(MacroLayerIndex.EXISTENCE)
        assert "reality" in ml.concepts_en
        assert "event" in ml.concepts_en

    def test_direction_layer_concepts(self):
        ml = macro_layer(MacroLayerIndex.DIRECTION)
        assert "هدى" in ml.concepts_ar
        assert "ضلال" in ml.concepts_ar


# ── Constraints ───────────────────────────────────────────────────────


class TestConstraints:
    def test_eight_constraints(self):
        assert len(GOVERNING_CONSTRAINTS) == 8

    def test_constraint_ids_unique(self):
        ids = [c.constraint_id for c in GOVERNING_CONSTRAINTS]
        assert len(ids) == len(set(ids))

    def test_constraint_lookup(self):
        c = governing_constraint(ConstraintIndex.NO_JUDGEMENT_WITHOUT_BINDING)
        assert c.antecedent == NodeIndex.BINDING
        assert c.consequent == NodeIndex.JUDGEMENT

    def test_no_guidance_without_truth(self):
        c = governing_constraint(ConstraintIndex.NO_GUIDANCE_WITHOUT_TRUTH)
        assert c.antecedent == NodeIndex.TRUTH_VALUE
        assert c.consequent == NodeIndex.GUIDANCE

    def test_all_constraints_returns_same_tuple(self):
        assert all_constraints() is GOVERNING_CONSTRAINTS


# ── Chain identity ────────────────────────────────────────────────────


class TestChain:
    def test_ascending_and_feedback_differ(self):
        a = chain_identity(ChainMode.ASCENDING)
        f = chain_identity(ChainMode.FEEDBACK)
        assert a != f

    def test_chain_is_circular(self):
        assert is_circular() is True

    def test_chain_identity_stable(self):
        a1 = chain_identity(ChainMode.ASCENDING)
        a2 = chain_identity(ChainMode.ASCENDING)
        assert a1 == a2
