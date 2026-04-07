"""Tests for formal_chain.py — formal layer chain and function composition."""

from creative_tokenizer.morphology.formal_chain import (
    FORMAL_CHAIN,
    ChainDirection,
    LayerIndex,
    all_formal_layers,
    analytic_chain,
    chain_id,
    formal_layer,
    generative_chain,
)

# ---------------------------------------------------------------------------
# §16  Layer structure
# ---------------------------------------------------------------------------


def test_formal_chain_has_eight_layers() -> None:
    assert len(FORMAL_CHAIN) == 8


def test_layers_ordered() -> None:
    """Layers should be in ascending order of LayerIndex."""
    for i, layer in enumerate(FORMAL_CHAIN):
        assert int(layer.index) == i


def test_unicode_layer() -> None:
    layer = formal_layer(LayerIndex.UNICODE)
    assert layer.symbol == "𝒰"
    assert "unicode" in layer.modules[0]


def test_phonological_layer() -> None:
    layer = formal_layer(LayerIndex.PHONOLOGICAL)
    assert layer.symbol == "(𝒞, 𝒱, 𝒟)"


def test_sentence_layer() -> None:
    layer = formal_layer(LayerIndex.SENTENCE)
    assert layer.symbol == "𝒮"


def test_all_formal_layers_returns_tuple() -> None:
    result = all_formal_layers()
    assert isinstance(result, tuple)
    assert len(result) == 8


def test_layer_id_deterministic() -> None:
    l1 = formal_layer(LayerIndex.GRAPHEME)
    l2 = formal_layer(LayerIndex.GRAPHEME)
    assert l1.layer_id == l2.layer_id


def test_layer_ids_distinct() -> None:
    ids = [layer.layer_id for layer in FORMAL_CHAIN]
    assert len(set(ids)) == len(ids)


# ---------------------------------------------------------------------------
# §17  Generative and analytic chains
# ---------------------------------------------------------------------------


def test_generative_chain_has_seven_steps() -> None:
    """7 transitions between 8 layers."""
    assert len(generative_chain()) == 7


def test_analytic_chain_has_seven_steps() -> None:
    assert len(analytic_chain()) == 7


def test_generative_chain_starts_at_unicode() -> None:
    assert generative_chain()[0].source == LayerIndex.UNICODE


def test_generative_chain_ends_at_sentence() -> None:
    assert generative_chain()[-1].target == LayerIndex.SENTENCE


def test_analytic_chain_starts_at_sentence() -> None:
    assert analytic_chain()[0].source == LayerIndex.SENTENCE


def test_analytic_chain_ends_at_unicode() -> None:
    assert analytic_chain()[-1].target == LayerIndex.UNICODE


def test_generative_chain_is_contiguous() -> None:
    """Each step's target should be the next step's source."""
    steps = generative_chain()
    for i in range(len(steps) - 1):
        assert steps[i].target == steps[i + 1].source


def test_analytic_chain_is_contiguous() -> None:
    steps = analytic_chain()
    for i in range(len(steps) - 1):
        assert steps[i].target == steps[i + 1].source


def test_chain_id_generative_deterministic() -> None:
    assert chain_id(ChainDirection.GENERATIVE) == chain_id(ChainDirection.GENERATIVE)


def test_chain_id_distinct_directions() -> None:
    assert chain_id(ChainDirection.GENERATIVE) != chain_id(ChainDirection.ANALYTIC)


def test_generative_analytic_are_inverses() -> None:
    """Generative and analytic chains should cover the same layers in reverse."""
    gen_layers = [(s.source, s.target) for s in generative_chain()]
    ana_layers = [(s.target, s.source) for s in reversed(analytic_chain())]
    assert gen_layers == ana_layers
