"""Word analysis pipeline — the bridge between tokenizer core and morphology.

``analyze_word`` runs the full stack:
  text → normalise → graphemes → skeleton → root lookup → pattern →
  event → word identity

Results that cannot be determined (e.g. root for an unknown word) are
``None``, and the overall ``confidence`` reflects the weakest link.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..morphology.event_layer import (
    Event,
    EventType,
    Transitivity,
    event_id,
    phi_event,
)
from ..morphology.formal_chain import LayerIndex
from ..morphology.grapheme_atoms import (
    consonantal_skeleton_id,
    grapheme_clusters,
    grapheme_surface_id,
)
from ..morphology.lexical_containers import IndependenceGrade, LexicalType
from ..morphology.root_pattern import (
    Pattern,
    Root,
    VerbPatternKind,
    make_root,
    make_verb_pattern,
    root_id,
)
from ..morphology.unicode_identity import unicode_surface
from ..morphology.word_identity import WordIdentity, compute_word_identity
from ..normalization import NormalizationProfile, NormalizedText, normalize_text
from .layer_result import LayerResult

__all__ = ["RootExtractor", "WordAnalysis", "analyze_word"]

# ── Common Arabic prefixes stripped before root lookup ────────────────

_DEFINITE_ARTICLE = "ال"
_COMMON_PREFIXES = ("ال", "و", "ف", "ب", "ك", "ل", "س")

# ── Event-type / transitivity mapping from lexicon strings ───────────

_EVENT_TYPE_MAP: dict[str, EventType] = {
    "ACTION": EventType.ACTION,
    "STATE": EventType.STATE,
    "PROCESS": EventType.PROCESS,
    "ACHIEVEMENT": EventType.ACHIEVEMENT,
    "ACCOMPLISHMENT": EventType.ACCOMPLISHMENT,
}

_TRANSITIVITY_MAP: dict[str, Transitivity] = {
    "INTRANSITIVE": Transitivity.INTRANSITIVE,
    "TRANSITIVE": Transitivity.TRANSITIVE,
    "DITRANSITIVE": Transitivity.DITRANSITIVE,
    "TRITRANSITIVE": Transitivity.TRITRANSITIVE,
}


# ═══════════════════════════════════════════════════════════════════════
# Root extractor protocol + default lexicon-based implementation
# ═══════════════════════════════════════════════════════════════════════


class RootExtractor(Protocol):
    """Pluggable strategy for extracting a root from a consonantal skeleton."""

    def extract(self, skeleton: str) -> tuple[Root, float] | None:
        """Return ``(root, confidence)`` or ``None`` if unknown."""
        ...  # pragma: no cover


@dataclass(frozen=True, slots=True)
class _LexiconEntry:
    root: Root
    verb_pattern: Pattern
    event_type: EventType
    transitivity: Transitivity


class LexiconRootExtractor:
    """Looks up roots in a JSON lexicon file."""

    def __init__(self, entries: dict[str, _LexiconEntry]) -> None:
        self._entries = entries

    @classmethod
    def from_json(cls, path: str | Path) -> LexiconRootExtractor:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
        entries: dict[str, _LexiconEntry] = {}
        for skeleton_key, info in raw.items():
            if skeleton_key.startswith("_"):
                continue
            root_cons = tuple(info["root"])
            root = make_root(root_cons)
            vp_template = info.get("default_verb_pattern", "فَعَلَ")
            verb_pattern = make_verb_pattern(vp_template, VerbPatternKind.MUJARRAD)
            et = _EVENT_TYPE_MAP.get(info.get("event_type", ""), EventType.ACTION)
            tr = _TRANSITIVITY_MAP.get(info.get("transitivity", ""), Transitivity.UNSPECIFIED)
            entries[skeleton_key] = _LexiconEntry(
                root=root, verb_pattern=verb_pattern, event_type=et, transitivity=tr
            )
        return cls(entries)

    @classmethod
    def default(cls) -> LexiconRootExtractor:
        """Load the bundled root_lexicon.json."""
        here = Path(__file__).parent
        return cls.from_json(here / "root_lexicon.json")

    def extract(self, skeleton: str) -> tuple[Root, float] | None:
        # Direct match
        entry = self._entries.get(skeleton)
        if entry is not None:
            return (entry.root, 1.0)
        # Try matching a 3-letter sub-skeleton against lexicon keys.
        # This handles derived nouns like كتاب (from كتب) or طالب (from طلب).
        # Extract only Arabic letter bases (strip long vowels / alef / ya / waw
        # that may be inserted by derivation).
        _VOWEL_LETTERS = frozenset("اويى")
        consonants = [c for c in skeleton if c not in _VOWEL_LETTERS]
        if len(consonants) >= 3:
            tri = "".join(consonants[:3])
            entry = self._entries.get(tri)
            if entry is not None:
                return (entry.root, 0.8)
        return None

    def lookup_full(self, skeleton: str) -> _LexiconEntry | None:
        entry = self._entries.get(skeleton)
        if entry is not None:
            return entry
        # Fallback via consonant extraction
        _VOWEL_LETTERS = frozenset("اويى")
        consonants = [c for c in skeleton if c not in _VOWEL_LETTERS]
        if len(consonants) >= 3:
            tri = "".join(consonants[:3])
            return self._entries.get(tri)
        return None


# ═══════════════════════════════════════════════════════════════════════
# WordAnalysis result
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class WordAnalysis:
    """Full analysis of a single word form."""

    text: str
    normalized: NormalizedText
    graphemes: tuple[tuple[str, tuple[str, ...]], ...]
    root: Root | None
    pattern: Pattern | None
    event: Event | None
    identity: WordIdentity
    trace: tuple[LayerResult, ...]
    confidence: float


# ═══════════════════════════════════════════════════════════════════════
# Main pipeline
# ═══════════════════════════════════════════════════════════════════════

# Module-level default extractor (lazy)
_default_extractor: LexiconRootExtractor | None = None


def _get_default_extractor() -> LexiconRootExtractor:
    global _default_extractor  # noqa: PLW0603
    if _default_extractor is None:
        _default_extractor = LexiconRootExtractor.default()
    return _default_extractor


def _strip_prefixes(text: str) -> tuple[str, list[str]]:
    """Strip common Arabic prefixes, returning (stem, [prefixes])."""
    stripped: list[str] = []
    remaining = text
    # Try definite article first
    if remaining.startswith(_DEFINITE_ARTICLE) and len(remaining) > len(_DEFINITE_ARTICLE) + 1:
        stripped.append(_DEFINITE_ARTICLE)
        remaining = remaining[len(_DEFINITE_ARTICLE):]
        return remaining, stripped
    # Then single-char proclitic prefixes
    while remaining and remaining[0] in ("و", "ف", "ب", "ك", "ل", "س"):
        if len(remaining) <= 2:
            break
        stripped.append(remaining[0])
        remaining = remaining[1:]
        # After prefix, check for definite article
        if remaining.startswith(_DEFINITE_ARTICLE) and len(remaining) > len(_DEFINITE_ARTICLE) + 1:
            stripped.append(_DEFINITE_ARTICLE)
            remaining = remaining[len(_DEFINITE_ARTICLE):]
            break
    return remaining, stripped


def analyze_word(
    text: str,
    *,
    extractor: RootExtractor | None = None,
) -> WordAnalysis:
    """Analyse a single Arabic word through all formal layers.

    Args:
        text: The raw word form (may include diacritics).
        extractor: Optional pluggable root extractor. Uses the bundled
            lexicon by default.

    Returns:
        A ``WordAnalysis`` with all available layers filled in.
        Layers that could not be determined are ``None``.
    """
    if extractor is None:
        extractor = _get_default_extractor()

    trace: list[LayerResult] = []

    # ── Layer 0: Unicode surface ──────────────────────────────────────
    u_id = unicode_surface(text)
    trace.append(LayerResult(
        layer=LayerIndex.UNICODE,
        value=text,
        identity=u_id,
        source_layer=LayerIndex.UNICODE,
        source_identity=0,
        confidence=1.0,
    ))

    # ── Normalisation ─────────────────────────────────────────────────
    norm = normalize_text(text, NormalizationProfile.MORPHOLOGICAL)

    # ── Layer 2: Grapheme clusters ────────────────────────────────────
    clusters_raw = grapheme_clusters(text)
    clusters = tuple(clusters_raw)
    g_id = grapheme_surface_id(text)
    trace.append(LayerResult(
        layer=LayerIndex.GRAPHEME,
        value=clusters,
        identity=g_id,
        source_layer=LayerIndex.UNICODE,
        source_identity=u_id,
        confidence=1.0,
    ))

    # ── Skeleton (basis for root lookup) ──────────────────────────────
    skel_id = consonantal_skeleton_id(text)

    # ── Layer 4: Root + Pattern ───────────────────────────────────────
    #
    # Strategy: try the full normalised form first, then try with
    # progressively more prefix stripping.  This avoids false positives
    # when the first letter of a word happens to be a proclitic letter
    # (e.g. ك in كتب is NOT a prefix).
    found_root: Root | None = None
    found_pattern: Pattern | None = None
    found_event: Event | None = None
    root_conf = 0.0

    # Candidate stems: full form first, then stripped forms
    candidates = [norm.text]
    stem, _prefixes = _strip_prefixes(norm.text)
    if stem != norm.text:
        candidates.append(stem)

    for candidate in candidates:
        result = extractor.extract(candidate)
        if result is not None:
            found_root, root_conf = result
            if isinstance(extractor, LexiconRootExtractor):
                entry = extractor.lookup_full(candidate)
                if entry is not None:
                    found_pattern = entry.verb_pattern
                    found_event = phi_event(
                        found_root,
                        found_pattern,
                        event_type=entry.event_type,
                        transitivity=entry.transitivity,
                    )
            break

    r_id = root_id(found_root) if found_root else 0
    trace.append(LayerResult(
        layer=LayerIndex.ROOT_PATTERN,
        value=(found_root, found_pattern),
        identity=r_id,
        source_layer=LayerIndex.GRAPHEME,
        source_identity=g_id,
        confidence=root_conf,
    ))

    # ── Layer 5: Event ────────────────────────────────────────────────
    e_id = event_id(found_event) if found_event else 0
    trace.append(LayerResult(
        layer=LayerIndex.LEXICAL,
        value=found_event,
        identity=e_id,
        source_layer=LayerIndex.ROOT_PATTERN,
        source_identity=r_id,
        confidence=root_conf if found_event else 0.0,
    ))

    # ── Layer 6: Word identity ────────────────────────────────────────
    lex_type = LexicalType.ROOT if found_root else LexicalType.JAMID
    indep = IndependenceGrade.AUTONOMOUS if found_root else IndependenceGrade.AUTONOMOUS
    carrier = r_id if found_root else skel_id

    wid = compute_word_identity(
        word=text,
        lexical_type=lex_type,
        independence=int(indep),
        carrier_id=carrier,
    )
    trace.append(LayerResult(
        layer=LayerIndex.CLOSED_WORD,
        value=wid,
        identity=wid.identity,
        source_layer=LayerIndex.LEXICAL,
        source_identity=e_id,
        confidence=1.0,
    ))

    # ── Overall confidence = weakest link ─────────────────────────────
    overall = min(lr.confidence for lr in trace) if trace else 0.0

    return WordAnalysis(
        text=text,
        normalized=norm,
        graphemes=clusters,
        root=found_root,
        pattern=found_pattern,
        event=found_event,
        identity=wid,
        trace=tuple(trace),
        confidence=overall,
    )
