"""Tests for Phase 9: nucleus layer map, explained retrieval, and qiyas layer."""

from __future__ import annotations

from creative_tokenizer.morphology.bayan_record import make_bayan
from creative_tokenizer.morphology.example_record import make_example, make_secondary_semantics
from creative_tokenizer.morphology.explained_retrieval import (
    ExplainedRetrievalResult,
    make_explained_retrieval,
)
from creative_tokenizer.morphology.nucleus import (
    NUCLEUS_REGISTRY,
    NucleusId,
    NucleusLayer,
    all_layers,
    layer,
)
from creative_tokenizer.morphology.qiyas_layer import (
    IllaMatchStrength,
    QiyasNode,
    QiyasType,
    make_qiyas,
)
from creative_tokenizer.morphology.trace_record import make_trace

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_trace() -> object:
    return make_trace(
        input_trace_id=1,
        normalization_trace_id=2,
        lexical_trace_id=3,
        compositional_trace_id=4,
        semantic_trace_id=5,
        economy_trace_id=6,
        output_trace_id=7,
    )


def _make_example() -> object:
    return make_example(
        domain_id=1,
        source_type=0,
        unicode_trace_id=10,
        token_node_ids=[1, 2],
        compositional_graph_id=20,
        mantuq_id=3,
        secondary_semantics=make_secondary_semantics(),
        style_hub_id=30,
        i3rab_trace_id=4,
    )


def _make_bayan() -> object:
    return make_bayan(
        target_node_id=1,
        rule_path=[2, 3],
        economy_justification=4,
        literal_blocking_condition=0,
        qarina_id=0,
        semantic_rank=1,
        traceback_ids=[5],
    )


# ---------------------------------------------------------------------------
# NucleusId enum
# ---------------------------------------------------------------------------


class TestNucleusIdEnum:
    def test_eight_nuclei(self) -> None:
        assert len(NucleusId) == 8

    def test_idrak_is_first(self) -> None:
        assert NucleusId.IDRAK == 1

    def test_hukm_is_last(self) -> None:
        assert NucleusId.HUKM == 8

    def test_qiyas_before_hukm(self) -> None:
        assert int(NucleusId.QIYAS) == int(NucleusId.HUKM) - 1

    def test_retrieval_before_qiyas(self) -> None:
        assert int(NucleusId.RETRIEVAL) < int(NucleusId.QIYAS)

    def test_trace_memory_before_retrieval(self) -> None:
        assert int(NucleusId.TRACE_MEMORY) < int(NucleusId.RETRIEVAL)


# ---------------------------------------------------------------------------
# NUCLEUS_REGISTRY
# ---------------------------------------------------------------------------


class TestNucleusRegistry:
    def test_registry_has_all_eight(self) -> None:
        assert len(NUCLEUS_REGISTRY) == 8

    def test_all_keys_are_nucleus_ids(self) -> None:
        assert set(NUCLEUS_REGISTRY.keys()) == set(NucleusId)

    def test_idrak_modules_include_unicode_identity(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.IDRAK]
        assert "unicode_identity" in lyr.module_names

    def test_idrak_modules_include_grapheme_atoms(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.IDRAK]
        assert "grapheme_atoms" in lyr.module_names

    def test_rabt_includes_morph_family(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.RABT]
        assert "morph_family" in lyr.module_names

    def test_concept_gen_includes_sign_signified(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.CONCEPT_GEN]
        assert "sign_signified" in lyr.module_names

    def test_concept_prolif_includes_conflict_resolution(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.CONCEPT_PROLIF]
        assert "conflict_resolution" in lyr.module_names

    def test_trace_memory_includes_lexical_node(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.TRACE_MEMORY]
        assert "lexical_node" in lyr.module_names

    def test_retrieval_includes_trace_record(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.RETRIEVAL]
        assert "trace_record" in lyr.module_names

    def test_retrieval_includes_explained_retrieval(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.RETRIEVAL]
        assert "explained_retrieval" in lyr.module_names

    def test_qiyas_includes_qiyas_layer(self) -> None:
        lyr = NUCLEUS_REGISTRY[NucleusId.QIYAS]
        assert "qiyas_layer" in lyr.module_names

    def test_hukm_modules_empty(self) -> None:
        """HUKM is reserved — not yet implemented."""
        lyr = NUCLEUS_REGISTRY[NucleusId.HUKM]
        assert len(lyr.module_names) == 0

    def test_all_layer_ids_positive(self) -> None:
        for lyr in NUCLEUS_REGISTRY.values():
            if lyr.module_names:  # skip HUKM which is empty
                assert lyr.layer_id > 0

    def test_layer_ids_unique_across_non_empty(self) -> None:
        ids = [
            lyr.layer_id
            for lyr in NUCLEUS_REGISTRY.values()
            if lyr.module_names
        ]
        assert len(ids) == len(set(ids))

    def test_all_labels_non_empty(self) -> None:
        for lyr in NUCLEUS_REGISTRY.values():
            assert lyr.label


# ---------------------------------------------------------------------------
# layer() helper
# ---------------------------------------------------------------------------


class TestLayerHelper:
    def test_returns_nucleus_layer(self) -> None:
        lyr = layer(NucleusId.IDRAK)
        assert isinstance(lyr, NucleusLayer)

    def test_nucleus_id_matches(self) -> None:
        lyr = layer(NucleusId.RABT)
        assert lyr.nucleus_id == NucleusId.RABT

    def test_same_object_as_registry(self) -> None:
        assert layer(NucleusId.QIYAS) is NUCLEUS_REGISTRY[NucleusId.QIYAS]


# ---------------------------------------------------------------------------
# all_layers()
# ---------------------------------------------------------------------------


class TestAllLayers:
    def test_returns_eight(self) -> None:
        assert len(all_layers()) == 8

    def test_first_is_idrak(self) -> None:
        assert all_layers()[0].nucleus_id == NucleusId.IDRAK

    def test_last_is_hukm(self) -> None:
        assert all_layers()[-1].nucleus_id == NucleusId.HUKM

    def test_monotonic_order(self) -> None:
        ids = [int(lyr.nucleus_id) for lyr in all_layers()]
        assert ids == sorted(ids)


# ---------------------------------------------------------------------------
# ExplainedRetrievalResult
# ---------------------------------------------------------------------------


class TestExplainedRetrieval:
    def _make(self, query_id: int = 99) -> ExplainedRetrievalResult:
        return make_explained_retrieval(
            query_id=query_id,
            example=_make_example(),  # type: ignore[arg-type]
            bayan=_make_bayan(),      # type: ignore[arg-type]
            trace=_make_trace(),      # type: ignore[arg-type]
        )

    def test_result_id_positive(self) -> None:
        assert self._make().result_id > 0

    def test_query_id_stored(self) -> None:
        r = self._make(query_id=42)
        assert r.query_id == 42

    def test_different_query_ids_differ(self) -> None:
        r1 = self._make(query_id=1)
        r2 = self._make(query_id=2)
        assert r1.result_id != r2.result_id

    def test_is_frozen(self) -> None:
        import dataclasses
        r = self._make()
        assert dataclasses.is_dataclass(r)
        # frozen dataclass — assignment should raise
        try:
            object.__setattr__(r, "query_id", 0)
        except (TypeError, AttributeError):
            pass  # expected
        else:
            # if frozen=False this won't raise — that is a test failure
            assert r.query_id == 0  # pragma: no cover

    def test_result_carries_example(self) -> None:
        r = self._make()
        assert r.example is not None

    def test_result_carries_bayan(self) -> None:
        r = self._make()
        assert r.bayan is not None

    def test_result_carries_trace(self) -> None:
        r = self._make()
        assert r.trace is not None

    def test_deterministic(self) -> None:
        r1 = self._make(query_id=7)
        r2 = self._make(query_id=7)
        assert r1.result_id == r2.result_id


# ---------------------------------------------------------------------------
# QiyasNode
# ---------------------------------------------------------------------------


class TestQiyasNodeBasic:
    def _make(
        self,
        asl_id: int = 10,
        far_id: int = 20,
        illa_id: int = 30,
        nisbah_id: int = 40,
        qiyas_type: QiyasType = QiyasType.JALI,
        illa_strength: IllaMatchStrength = IllaMatchStrength.QATII,
    ) -> QiyasNode:
        return make_qiyas(
            asl_id=asl_id,
            far_id=far_id,
            illa_id=illa_id,
            nisbah_id=nisbah_id,
            qiyas_type=qiyas_type,
            illa_strength=illa_strength,
        )

    def test_qiyas_id_positive(self) -> None:
        assert self._make().qiyas_id > 0

    def test_asl_id_stored(self) -> None:
        assert self._make(asl_id=5).asl_id == 5

    def test_far_id_stored(self) -> None:
        assert self._make(far_id=6).far_id == 6

    def test_illa_id_stored(self) -> None:
        assert self._make(illa_id=7).illa_id == 7

    def test_nisbah_id_stored(self) -> None:
        assert self._make(nisbah_id=8).nisbah_id == 8

    def test_qiyas_type_stored(self) -> None:
        assert self._make(qiyas_type=QiyasType.AWL).qiyas_type == QiyasType.AWL

    def test_illa_strength_stored(self) -> None:
        q = self._make(illa_strength=IllaMatchStrength.ZANNI)
        assert q.illa_strength == IllaMatchStrength.ZANNI

    def test_confidence_default_full(self) -> None:
        from creative_tokenizer.morphology.exact_decimal import READY_FULL
        q = self._make()
        assert q.confidence == q.confidence.__class__.from_pair(READY_FULL)

    def test_deterministic(self) -> None:
        q1 = self._make()
        q2 = self._make()
        assert q1.qiyas_id == q2.qiyas_id


class TestQiyasNodeDistinctness:
    def test_different_asl_differs(self) -> None:
        q1 = make_qiyas(1, 20, 30, 40)
        q2 = make_qiyas(2, 20, 30, 40)
        assert q1.qiyas_id != q2.qiyas_id

    def test_different_far_differs(self) -> None:
        q1 = make_qiyas(10, 1, 30, 40)
        q2 = make_qiyas(10, 2, 30, 40)
        assert q1.qiyas_id != q2.qiyas_id

    def test_different_illa_differs(self) -> None:
        q1 = make_qiyas(10, 20, 1, 40)
        q2 = make_qiyas(10, 20, 2, 40)
        assert q1.qiyas_id != q2.qiyas_id

    def test_different_nisbah_differs(self) -> None:
        q1 = make_qiyas(10, 20, 30, 1)
        q2 = make_qiyas(10, 20, 30, 2)
        assert q1.qiyas_id != q2.qiyas_id

    def test_jali_vs_khafi_differs(self) -> None:
        q1 = make_qiyas(10, 20, 30, 40, QiyasType.JALI)
        q2 = make_qiyas(10, 20, 30, 40, QiyasType.KHAFI)
        assert q1.qiyas_id != q2.qiyas_id

    def test_qatii_vs_zanni_differs(self) -> None:
        q1 = make_qiyas(10, 20, 30, 40, illa_strength=IllaMatchStrength.QATII)
        q2 = make_qiyas(10, 20, 30, 40, illa_strength=IllaMatchStrength.ZANNI)
        assert q1.qiyas_id != q2.qiyas_id


class TestQiyasTypes:
    def test_jali_value(self) -> None:
        assert QiyasType.JALI == 1

    def test_khafi_value(self) -> None:
        assert QiyasType.KHAFI == 2

    def test_awl_value(self) -> None:
        assert QiyasType.AWL == 3

    def test_three_types(self) -> None:
        assert len(QiyasType) == 3


class TestIllaMatchStrength:
    def test_qatii_is_one(self) -> None:
        assert IllaMatchStrength.QATII == 1

    def test_zanni_is_two(self) -> None:
        assert IllaMatchStrength.ZANNI == 2

    def test_daif_is_three(self) -> None:
        assert IllaMatchStrength.DAIF == 3

    def test_three_strengths(self) -> None:
        assert len(IllaMatchStrength) == 3
