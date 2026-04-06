"""Formal layer registry — maps the 8 cognitive nuclei to Python modules.

The project architecture follows the document:
  نواة الإدراك → نواة الربط → نواة توليد المفهوم → نواة توالد المفاهيم
  → ذاكرة الأثر → الاسترجاع المفسر → القياس → الحكم

Each NucleusLayer records:
  nucleus_id      — which of the 8 nuclei this layer belongs to
  module_names    — Python source module names that implement this nucleus
  hub_types       — hub/container types used in this nucleus
  layer_id        — F(nucleus_id, fold(module_names)) — stable numeric id

The registry is the canonical map between the foundational document and the
codebase.  It is query-only; no mutation, no side-effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class NucleusId(IntEnum):
    IDRAK = 1           # نواة الإدراك       — perception / raw identity
    RABT = 2            # نواة الربط         — binding / structural assembly
    CONCEPT_GEN = 3     # نواة توليد المفهوم  — concept generation
    CONCEPT_PROLIF = 4  # نواة توالد المفاهيم — concept proliferation
    TRACE_MEMORY = 5    # ذاكرة الأثر        — trace / corpus stores
    RETRIEVAL = 6       # الاسترجاع المفسر   — explained retrieval
    QIYAS = 7           # القياس             — analogy / inference
    HUKM = 8            # الحكم              — judgment (future)


@dataclass(frozen=True, slots=True)
class NucleusLayer:
    nucleus_id: NucleusId
    label: str                    # human-readable Arabic label
    module_names: tuple[str, ...]  # Python module basenames
    hub_types: tuple[str, ...]     # hub/container type names used
    layer_id: int                  # F(nucleus_id, fold(hash of module names))


def _layer_id(nucleus_id: NucleusId, module_names: tuple[str, ...]) -> int:
    name_fold = fractal_fold(
        [cantor_pair(i + 1, hash(n) % (2**31)) for i, n in enumerate(module_names)]
    )
    return cantor_pair(int(nucleus_id), name_fold)


NUCLEUS_REGISTRY: dict[NucleusId, NucleusLayer] = {}


def _reg(
    nid: NucleusId,
    label: str,
    modules: tuple[str, ...],
    hubs: tuple[str, ...],
) -> None:
    NUCLEUS_REGISTRY[nid] = NucleusLayer(
        nucleus_id=nid,
        label=label,
        module_names=modules,
        hub_types=hubs,
        layer_id=_layer_id(nid, modules),
    )


_reg(
    NucleusId.IDRAK,
    "نواة الإدراك",
    ("unicode_identity", "grapheme_atoms"),
    ("UnicodeAtom",),
)

_reg(
    NucleusId.RABT,
    "نواة الربط",
    (
        "lexical_containers",
        "morph_family",
        "constraint_envelope",
        "carrier_layer",
        "inflectional_state",
        "base_class",
        "lexical_nature",
    ),
    ("LexicalType", "IndependenceGrade", "MorphFamily", "ConstraintEnvelope"),
)

_reg(
    NucleusId.CONCEPT_GEN,
    "نواة توليد المفهوم",
    (
        "sign_signified",
        "lexical_hub",
        "ontology_hub",
        "epistemic_hub",
        "conceptual_class",
    ),
    (
        "LexicalMeaningHub",
        "OntologyNode",
        "EpistemicMode",
        "SignSignifiedCoupling",
    ),
)

_reg(
    NucleusId.CONCEPT_PROLIF,
    "نواة توالد المفاهيم",
    (
        "triple_semantic",
        "transfer_sense",
        "metaphor",
        "semantic_functions",
        "conflict_resolution",
    ),
    (
        "TripleSemantic",
        "TransferNode",
        "LexicalMetaphorNode",
        "CompositionalMetaphorNode",
        "ConflictResolution",
    ),
)

_reg(
    NucleusId.TRACE_MEMORY,
    "ذاكرة الأثر",
    (
        "lexical_node",
        "example_record",
        "bayan_record",
        "generation_template",
        "cognitive_domain",
    ),
    (
        "LexicalNode",
        "ExampleRecord",
        "BayanRecord",
        "GenerationTemplate",
        "CognitiveConcept",
    ),
)

_reg(
    NucleusId.RETRIEVAL,
    "الاسترجاع المفسر",
    ("trace_record", "explained_retrieval"),
    ("TraceRecord", "ExplainedRetrievalResult"),
)

_reg(
    NucleusId.QIYAS,
    "القياس",
    ("qiyas_layer",),
    ("QiyasNode",),
)

_reg(
    NucleusId.HUKM,
    "الحكم",
    (),   # not yet implemented
    (),
)


def layer(nucleus_id: NucleusId) -> NucleusLayer:
    """Return the NucleusLayer for a given nucleus id."""
    return NUCLEUS_REGISTRY[nucleus_id]


def all_layers() -> list[NucleusLayer]:
    """Return all 8 nuclei in canonical order."""
    return [NUCLEUS_REGISTRY[nid] for nid in NucleusId]
