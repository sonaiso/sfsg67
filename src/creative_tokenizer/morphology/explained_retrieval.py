"""Explained Retrieval — nucleus 6 (الاسترجاع المفسر).

Explained retrieval is NOT a mechanical fetch.  Every retrieved element must
carry with it the full path of its formation:

  ExplainedRetrievalResult = {
      query_id        — what was asked
      example         — the matched ExampleRecord
      bayan           — the BayanRecord explaining why this match
      trace           — the TraceRecord linking input to output
      result_id       — F(query_id, example_id, bayan_id, trace_id)
  }

This ensures that every retrieval answers not only "what" but:
  - Why was this selected?           (bayan.literal_blocking_condition,
                                       bayan.rule_path)
  - Which qarina deflected meaning?  (bayan.qarina_id)
  - What is the priority rank?       (bayan.semantic_rank)
  - How does it trace back to raw Unicode?  (trace.input_trace_id)
  - What economy principle applied?  (trace.economy_trace_id)
"""

from __future__ import annotations

from dataclasses import dataclass

from .bayan_record import BayanRecord
from .example_record import ExampleRecord
from .fractal_storage import cantor_pair, fractal_fold
from .trace_record import TraceRecord


@dataclass(frozen=True, slots=True)
class ExplainedRetrievalResult:
    query_id: int
    example: ExampleRecord
    bayan: BayanRecord
    trace: TraceRecord
    result_id: int  # F(query, example, bayan, trace)


def make_explained_retrieval(
    query_id: int,
    example: ExampleRecord,
    bayan: BayanRecord,
    trace: TraceRecord,
) -> ExplainedRetrievalResult:
    """Assemble a fully explained retrieval result.

    result_id encodes all four constituents, so any change in any layer
    changes the result identity.
    """
    result_id = fractal_fold(
        [
            cantor_pair(1, query_id),
            cantor_pair(2, example.example_id),
            cantor_pair(3, bayan.explanation_id),
            cantor_pair(4, trace.trace_id),
        ]
    )
    return ExplainedRetrievalResult(
        query_id=query_id,
        example=example,
        bayan=bayan,
        trace=trace,
        result_id=result_id,
    )
