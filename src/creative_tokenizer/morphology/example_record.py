"""Example record — one entry in the examples store.

Each example bundles the raw text, its unicode trace, token node ids,
compositional/semantic graph ids, and secondary-semantics ids into one
economy-tagged record.

  example_id = F(π(1,unicode_trace_id), π(2,compositional_graph_id),
                  π(3,style_hub_id), π(4,source_type))

SecondarySemantics packs the five pre-judgment semantic dimensions:
  condition (HAS_SHART), mafhum (HAS_MAFHUM), iqtida (HAS_IQTIDA),
  ishara (HAS_ISHARA), ghaya (HAS_GHAYA).
  Value 0 = dimension absent for this example.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class ExampleSource(IntEnum):
    CORPUS = 1
    GENERATED = 2
    MANUAL = 3


@dataclass(frozen=True, slots=True)
class SecondarySemantics:
    condition_id: int  # HAS_SHART  — 0 = absent
    mafhum_id: int     # HAS_MAFHUM — 0 = absent
    iqtida_id: int     # HAS_IQTIDA — 0 = absent
    ishara_id: int     # HAS_ISHARA — 0 = absent
    ghaya_id: int      # HAS_GHAYA  — 0 = absent
    pack_id: int       # F(all above)


def make_secondary_semantics(
    condition_id: int = 0,
    mafhum_id: int = 0,
    iqtida_id: int = 0,
    ishara_id: int = 0,
    ghaya_id: int = 0,
) -> SecondarySemantics:
    pack_id = fractal_fold(
        [
            cantor_pair(1, condition_id),
            cantor_pair(2, mafhum_id),
            cantor_pair(3, iqtida_id),
            cantor_pair(4, ishara_id),
            cantor_pair(5, ghaya_id),
        ]
    )
    return SecondarySemantics(
        condition_id=condition_id,
        mafhum_id=mafhum_id,
        iqtida_id=iqtida_id,
        ishara_id=ishara_id,
        ghaya_id=ghaya_id,
        pack_id=pack_id,
    )


@dataclass(frozen=True, slots=True)
class ExampleRecord:
    example_id: int
    domain_id: int
    source_type: ExampleSource
    unicode_trace_id: int
    token_node_ids: tuple[int, ...]
    compositional_graph_id: int
    mantuq_id: int
    secondary_semantics: SecondarySemantics
    style_hub_id: int
    i3rab_trace_id: int
    conflict_resolution_trace_id: int
    economy_trace_id: int
    raw_text: str  # preserved for corpus retrieval; not part of example_id


def make_example(
    domain_id: int,
    source_type: ExampleSource,
    unicode_trace_id: int,
    token_node_ids: list[int],
    compositional_graph_id: int,
    mantuq_id: int,
    secondary_semantics: SecondarySemantics,
    style_hub_id: int,
    i3rab_trace_id: int,
    raw_text: str = "",
    conflict_resolution_trace_id: int = 0,
    economy_trace_id: int = 0,
) -> ExampleRecord:
    example_id = fractal_fold(
        [
            cantor_pair(1, unicode_trace_id),
            cantor_pair(2, compositional_graph_id),
            cantor_pair(3, style_hub_id),
            cantor_pair(4, int(source_type)),
        ]
    )
    return ExampleRecord(
        example_id=example_id,
        domain_id=domain_id,
        source_type=source_type,
        unicode_trace_id=unicode_trace_id,
        token_node_ids=tuple(token_node_ids),
        compositional_graph_id=compositional_graph_id,
        mantuq_id=mantuq_id,
        secondary_semantics=secondary_semantics,
        style_hub_id=style_hub_id,
        i3rab_trace_id=i3rab_trace_id,
        conflict_resolution_trace_id=conflict_resolution_trace_id,
        economy_trace_id=economy_trace_id,
        raw_text=raw_text,
    )
