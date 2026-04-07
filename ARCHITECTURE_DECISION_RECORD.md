# Architecture Decision Record — Creative Tokenizer

## ADR-001: Multi-layer Package Structure

**Status:** Accepted  
**Date:** 2026-04-07  
**Context:** The project has grown from a simple tokenizer into a
multi-layer platform encompassing core tokenization, linguistic analysis,
and an epistemic knowledge engine.

### Decision

Organise the codebase into four logical zones:

| Zone | Package path | Purpose |
|------|-------------|---------|
| **Core** | `creative_tokenizer.core` | Tokenizer, normalization, BPE, clitic segmentation |
| **Linguistics** | `creative_tokenizer.linguistics` | `analyze_word()`, `LayerResult`, root extraction |
| **Knowledge** | `creative_tokenizer.knowledge` | Relation registry, epistemic engine, vertical slice |
| **Morphology** | `creative_tokenizer.morphology` | Formal chain, phonological sets, upper ontology (existing) |

### Consequences

1. **Core Product** is independently installable (`pip install creative-tokenizer`).
2. **Linguistics** is an optional layer (`pip install creative-tokenizer[linguistics]`).
3. **Knowledge** is an optional layer (`pip install creative-tokenizer[knowledge]`).
4. All old imports continue to work via re-exports in `creative_tokenizer/__init__.py`.
5. New imports use the structured paths: `from creative_tokenizer.core import ...`

---

## ADR-002: Span Contract as Primary Invariant

**Status:** Accepted  
**Date:** 2026-04-07  
**Context:** Arabic tokenization involves complex normalization (diacritics,
tatweel, hamza unification) that can break character-index alignment.

### Decision

Every `Token` object returned by any tokenizer path **must** satisfy:

```python
source_text[token.start : token.end] == token.text
```

This is enforced by 10+ dedicated span-contract tests covering edge cases
(full tashkeel, tatweel, mixed digits, orphaned diacritics, etc.).

### Consequences

- Normalization produces a `NormalizedText` with an explicit `mapping` tuple.
- No tokenizer optimization may bypass the mapping.
- Breaking this invariant is a regression.

---

## ADR-003: Normalization Profiles

**Status:** Accepted  
**Date:** 2026-04-07  
**Context:** Different use cases need different normalization strictness.

### Decision

Three profiles via `NormalizationProfile` enum:

| Profile | Removes | Preserves | Use case |
|---------|---------|-----------|----------|
| CONSERVATIVE | tatweel only | diacritics, hamza forms | Faithful display |
| STANDARD | diacritics + tatweel + hamza unification | — | General tokenization |
| MORPHOLOGICAL | like STANDARD + ة→ت | — | Morphological analysis |

Default is `STANDARD` (backward compatible).

---

## ADR-004: Configurable Clitic Rules

**Status:** Accepted  
**Date:** 2026-04-07  
**Context:** Hard-coded clitic lists prevent customization for dialects or
specialized corpora.

### Decision

`CliticRules` frozen dataclass with:
- `prefixes` / `suffixes` (ordered longest-first)
- `min_stem_length` (default 2)
- `bidirectional` flag (default True)
- `from_json()` / `save_json()` for file-based configuration

`CreativeTokenizer` accepts optional `clitic_rules` parameter.

---

## ADR-005: Epistemic Engine as Rule Layer

**Status:** Accepted  
**Date:** 2026-04-07  
**Context:** The ten epistemic principles were previously descriptive only.

### Decision

`EpistemicEngine` converts each principle into an executable rule:
- `validate(node, context)` → list of `EpistemicVerdict`
- `can_transition(source, target, context)` → (bool, verdicts)
- Every verdict includes an Arabic `reason` string for auditability.

Transitions in the upper ontology chain are gated by these rules.

---

## ADR-006: Concept Gate

**Status:** Accepted  
**Date:** 2026-04-07  
**Context:** Uncontrolled addition of concepts to the ontology risks
incoherence.

### Decision

`validate_concept()` requires every new concept to declare:
- A source node and upstream relation kind
- A target node and downstream relation kind

Both must correspond to existing entries in `RelationRegistry`.
