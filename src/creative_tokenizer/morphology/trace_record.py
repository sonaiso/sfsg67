"""Trace record — one entry in the traceability store.

Every transformation pass through the system produces a TraceRecord that
links input to output through all intermediate layers:

  input_trace_id           — raw text / unicode surface id
  normalization_trace_id   — post-normalization id
  lexical_trace_id         — lexical node resolution id
  compositional_trace_id   — compositional graph id
  semantic_trace_id        — semantic resolution id (conflict, mantuq …)
  economy_trace_id         — minimal-closure / hub-sharing id
  output_trace_id          — final output node / sentence id

  trace_id = F(π(1,input), π(2,norm), π(3,lex), π(4,comp),
                π(5,sem), π(6,eco), π(7,out))

Changing any single layer changes trace_id, making every transformation
fully auditable back to raw input.
"""

from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair, fractal_fold


@dataclass(frozen=True, slots=True)
class TraceRecord:
    trace_id: int
    input_trace_id: int
    normalization_trace_id: int
    lexical_trace_id: int
    compositional_trace_id: int
    semantic_trace_id: int
    economy_trace_id: int
    output_trace_id: int


def make_trace(
    input_trace_id: int,
    normalization_trace_id: int,
    lexical_trace_id: int,
    compositional_trace_id: int,
    semantic_trace_id: int,
    economy_trace_id: int,
    output_trace_id: int,
) -> TraceRecord:
    trace_id = fractal_fold(
        [
            cantor_pair(1, input_trace_id),
            cantor_pair(2, normalization_trace_id),
            cantor_pair(3, lexical_trace_id),
            cantor_pair(4, compositional_trace_id),
            cantor_pair(5, semantic_trace_id),
            cantor_pair(6, economy_trace_id),
            cantor_pair(7, output_trace_id),
        ]
    )
    return TraceRecord(
        trace_id=trace_id,
        input_trace_id=input_trace_id,
        normalization_trace_id=normalization_trace_id,
        lexical_trace_id=lexical_trace_id,
        compositional_trace_id=compositional_trace_id,
        semantic_trace_id=semantic_trace_id,
        economy_trace_id=economy_trace_id,
        output_trace_id=output_trace_id,
    )
