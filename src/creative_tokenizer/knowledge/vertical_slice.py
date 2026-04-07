"""Vertical slice — complete pipeline from Unicode input to epistemic classification.

``vertical_slice(text)`` runs a single Arabic sentence through every layer:

1. Unicode input
2. Normalization (MORPHOLOGICAL)
3. Pretokenization (word splitting)
4. Word-level analysis (analyze_word for each word)
5. Epistemic validation (EpistemicEngine checks)
6. Classification (خبر/إنشاء, قطعي/معلّق)

This is the proof-of-flow that demonstrates the entire architecture
works end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..linguistics.analyze import WordAnalysis, analyze_word
from ..normalization import NormalizationProfile, NormalizedText, normalize_text
from ..pretokenizer import PreToken, pretokenize
from .epistemic_engine import EpistemicEngine, EpistemicVerdict, SignificationStatus

__all__ = ["SliceResult", "vertical_slice"]


# ═══════════════════════════════════════════════════════════════════════
# §1  Classification types
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class SentenceClassification:
    """Final classification of the sentence."""

    sentence_type: str     # "خبر" (declarative) or "إنشاء" (performative)
    strength: str          # "قطعي" (decisive) or "معلّق" (suspended)
    epistemic_verdicts: tuple[EpistemicVerdict, ...]
    signification_status: SignificationStatus


# ═══════════════════════════════════════════════════════════════════════
# §2  Slice result
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class SliceResult:
    """Full vertical-slice result containing every pipeline stage."""

    # Stage 1: Raw input
    raw_text: str

    # Stage 2: Normalization
    normalized: NormalizedText

    # Stage 3: Pretokenization
    pretokens: tuple[PreToken, ...]

    # Stage 4: Word analyses
    word_analyses: tuple[WordAnalysis, ...]

    # Stage 5+6: Epistemic validation + classification
    classification: SentenceClassification

    # Overall pipeline confidence (weakest link)
    confidence: float


# ═══════════════════════════════════════════════════════════════════════
# §3  Heuristic helpers
# ═══════════════════════════════════════════════════════════════════════

# Interrogative particles that signal إنشاء (performative / non-declarative)
_INSHA_MARKERS = frozenset({"هل", "أ", "ما", "من", "متى", "أين", "كيف", "لماذا", "يا"})


def _classify_sentence_type(analyses: tuple[WordAnalysis, ...]) -> str:
    """Classify as خبر (declarative) or إنشاء (performative).

    Very simple heuristic: if any token matches an interrogative / vocative
    particle, treat as إنشاء; otherwise خبر.
    """
    for wa in analyses:
        if wa.normalized.text in _INSHA_MARKERS:
            return "إنشاء"
    return "خبر"


def _has_verb(analyses: tuple[WordAnalysis, ...]) -> bool:
    """Check if any word has a resolved event (i.e. is a verb)."""
    return any(wa.event is not None for wa in analyses)


# ═══════════════════════════════════════════════════════════════════════
# §4  Main pipeline
# ═══════════════════════════════════════════════════════════════════════


def vertical_slice(text: str) -> SliceResult:
    """Run the complete vertical slice pipeline on an Arabic sentence.

    Args:
        text: Raw Arabic text (may include diacritics, clitics, etc.)

    Returns:
        A :class:`SliceResult` with all stages populated.
    """
    # Stage 1: Raw input
    raw_text = text

    # Stage 2: Normalization
    normalized = normalize_text(text, NormalizationProfile.MORPHOLOGICAL)

    # Stage 3: Pretokenization
    pretokens_list = pretokenize(text)
    pretokens = tuple(pretokens_list)

    # Stage 4: Word analysis (using original text spans)
    word_analyses: list[WordAnalysis] = []
    for pt in pretokens_list:
        # Reconstruct original word form from mapping
        if pt.mapping:
            start = pt.mapping[0]
            end = pt.mapping[-1] + 1
            original_word = text[start:end]
        else:
            original_word = pt.word
        word_analyses.append(analyze_word(original_word))

    analyses_tuple = tuple(word_analyses)

    # Stage 5: Build epistemic context from word analyses
    has_verb_flag = _has_verb(analyses_tuple)
    any_root_found = any(wa.root is not None for wa in analyses_tuple)

    # Count ambiguity: if any word has no root, there's potential ambiguity
    unknown_count = sum(1 for wa in analyses_tuple if wa.root is None and len(wa.text) > 1)
    ambiguity = max(1, unknown_count)  # at least 1 if there are unknowns

    ctx: dict[str, object] = {
        "has_reality": True,            # any utterance refers to reality
        "has_sense": True,              # text is perceivable
        "has_prior_knowledge": any_root_found,  # we know some words
        "has_binding": has_verb_flag,    # verb binds agent/patient
        "has_prior_opinion": False,      # no contamination in pipeline
        "judgement_type": "existence" if has_verb_flag else "",
        "has_convention": any_root_found,  # words have lexical convention
        "ambiguity_count": ambiguity if unknown_count > 0 else 1,
        "has_standard": True,           # we have a formal standard (the ontology)
        "has_fruit": has_verb_flag and any_root_found,  # complete if verb + known words
    }

    # Stage 6: Epistemic validation
    engine = EpistemicEngine()

    # Walk the full chain and collect verdicts
    from ..morphology.upper_ontology import NodeIndex

    all_verdicts: list[EpistemicVerdict] = []
    for node in NodeIndex:
        verdicts = engine.validate(node, ctx)
        all_verdicts.extend(verdicts)

    sig_status = engine.signification_status(ctx)

    # Classification
    sentence_type = _classify_sentence_type(analyses_tuple)
    strength = "قطعي" if sig_status == SignificationStatus.DECIDED else "معلّق"

    classification = SentenceClassification(
        sentence_type=sentence_type,
        strength=strength,
        epistemic_verdicts=tuple(all_verdicts),
        signification_status=sig_status,
    )

    # Overall confidence = weakest word analysis
    word_confs = [wa.confidence for wa in analyses_tuple] if analyses_tuple else [0.0]
    overall = min(word_confs)

    return SliceResult(
        raw_text=raw_text,
        normalized=normalized,
        pretokens=pretokens,
        word_analyses=analyses_tuple,
        classification=classification,
        confidence=overall,
    )
