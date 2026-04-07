"""Full Arabic Engine pipeline.

F = E ∘ J ∘ D ∘ O ∘ L ∘ S ∘ N

Pipeline stages:
  1. Normalize  (N) — unicode normalization
  2. Signifier  (S) — phonology + root/pattern extraction
  3. Lexical Closure (L) — token construction
  4. Ontology   (O) — concept mapping
  5. Dalāla     (D) — semantic linkage validation
  6. Syntax     — syntactic tree (V2)
  7. TimeSpace  — temporal/spatial anchoring (V2)
  8. Judgment   (J) — proposition construction
  9. Evaluation (E) — truth/guidance evaluation
  10. Inference  — forward-chaining rule application (V2)
"""

from __future__ import annotations

from dataclasses import dataclass

from .cognition.evaluation import EvalResult, Judgment, build_evaluation, build_judgment
from .core.enums import DalalType, GuidanceState, TruthState
from .core.types import Concept, DalalLink, Token, make_token
from .inference.inference_rules import InferenceEngine, InferenceResult
from .inference.world_model import WorldModel
from .linkage.dalala import validate_dalala
from .signified.ontology import map_to_ontology
from .signifier.phonology import PhonResult, analyze_phonology
from .signifier.root_pattern import RootPatternResult, extract_root_pattern
from .signifier.unicode_norm import NormResult, normalize_arabic
from .syntax.syntax import SyntaxNode, build_syntax_tree
from .syntax.time_space import TimeSpace, build_time_space

__all__ = ["PipelineResult", "run_pipeline"]


@dataclass(frozen=True, slots=True)
class WordAnalysis:
    """Full analysis of a single word through the pipeline."""

    surface: str
    norm: str
    phonology: PhonResult
    root_pattern: RootPatternResult
    token: Token
    concept: Concept
    dalala_mutabaqa: DalalLink
    dalala_isnad: DalalLink | None


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Complete pipeline output for an Arabic text.

    Contains all intermediate and final results from every stage.
    """

    original: str
    normalized: NormResult
    words: tuple[WordAnalysis, ...]
    syntax_tree: tuple[SyntaxNode, ...]
    time_space: TimeSpace
    judgment: Judgment
    evaluation: EvalResult
    inference: InferenceResult | None


def _split_words(text: str) -> list[tuple[str, int, int]]:
    """Split text into words with original spans."""
    words: list[tuple[str, int, int]] = []
    start = 0
    in_word = False
    for i, ch in enumerate(text):
        if ch == " ":
            if in_word:
                words.append((text[start:i], start, i))
                in_word = False
        else:
            if not in_word:
                start = i
                in_word = True
    if in_word:
        words.append((text[start:len(text)], start, len(text)))
    return words


def run_pipeline(
    text: str,
    world: WorldModel | None = None,
) -> PipelineResult:
    """Run the full Arabic Engine pipeline on input text.

    Parameters
    ----------
    text:   raw Arabic input (with or without diacritics)
    world:  optional world model for evaluation context

    Returns
    -------
    PipelineResult with all intermediate and final results.
    """
    # 1. Normalize
    norm = normalize_arabic(text)

    # 2–4. Per-word analysis: signifier → lexical closure → ontology → dalāla
    raw_words = _split_words(text)
    analyses: list[WordAnalysis] = []
    token_ids: list[int] = []
    pos_tags: list[str] = []

    for surface, span_start, span_end in raw_words:
        # Signifier layer
        phon = analyze_phonology(surface)
        rp = extract_root_pattern(surface)

        # Lexical closure
        tok = make_token(
            surface=surface,
            normalized=norm.text,
            lemma=rp.lemma,
            root=rp.root,
            pattern=rp.pattern,
            pos=rp.pos,
            span=(span_start, span_end),
        )

        # Ontological mapping
        concept = map_to_ontology(tok)

        # Dalāla validation (mutabaqa always; isnad if verb/noun pair)
        dalala_m = validate_dalala(tok, concept, DalalType.MUTABAQA)
        dalala_i = None

        analyses.append(WordAnalysis(
            surface=surface,
            norm=norm.text,
            phonology=phon,
            root_pattern=rp,
            token=tok,
            concept=concept,
            dalala_mutabaqa=dalala_m,
            dalala_isnad=dalala_i,
        ))
        token_ids.append(tok.token_id)
        pos_tags.append(rp.pos)

    # 5. Build isnad links between verb and nouns
    verb_idx = None
    for i, a in enumerate(analyses):
        if a.token.pos == "verb":
            verb_idx = i
            break

    if verb_idx is not None:
        for i, a in enumerate(analyses):
            if i != verb_idx and a.token.pos in ("noun", "unknown"):
                isnad_link = validate_dalala(
                    analyses[verb_idx].token, a.concept, DalalType.ISNAD
                )
                analyses[i] = WordAnalysis(
                    surface=a.surface,
                    norm=a.norm,
                    phonology=a.phonology,
                    root_pattern=a.root_pattern,
                    token=a.token,
                    concept=a.concept,
                    dalala_mutabaqa=a.dalala_mutabaqa,
                    dalala_isnad=isnad_link,
                )

    # 6. Syntax tree (V2)
    syntax_tree = build_syntax_tree(token_ids, pos_tags)

    # 7. Time/space anchoring (V2)
    verb_pos = ""
    verb_pattern = ""
    if verb_idx is not None:
        verb_pos = analyses[verb_idx].token.pos
        verb_pattern = analyses[verb_idx].root_pattern.pattern
    ts = build_time_space(pos=verb_pos, pattern=verb_pattern)

    # 8. Judgment construction
    subject_id = 0
    predicate_id = 0
    object_id = 0

    if verb_idx is not None:
        predicate_id = analyses[verb_idx].token.token_id

    nouns = [a for a in analyses if a.token.pos != "verb"]
    if len(nouns) >= 1:
        subject_id = nouns[0].token.token_id
    if len(nouns) >= 2:
        object_id = nouns[1].token.token_id

    judgment = build_judgment(
        subject=subject_id,
        predicate=predicate_id,
        object_id=object_id,
        time=ts.time_id,
        space=ts.space_id,
    )

    # 9. Evaluation
    avg_confidence = (
        sum(a.dalala_mutabaqa.confidence for a in analyses) / len(analyses)
        if analyses
        else 0.5
    )
    evaluation = build_evaluation(
        judgment=judgment,
        truth_state=TruthState.PROBABLE,
        guidance_state=GuidanceState.NEUTRAL,
        confidence=avg_confidence,
    )

    # 10. Inference (V2)
    inference_result: InferenceResult | None = None
    if world is not None:
        engine = InferenceEngine(world)
        inference_result = engine.apply_existential(judgment, evaluation)

    return PipelineResult(
        original=text,
        normalized=norm,
        words=tuple(analyses),
        syntax_tree=syntax_tree,
        time_space=ts,
        judgment=judgment,
        evaluation=evaluation,
        inference=inference_result,
    )
