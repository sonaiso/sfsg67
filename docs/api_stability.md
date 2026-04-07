# API Stability Guarantees

## Core Package (`creative_tokenizer`)

The following public names are **stable** from version 0.1.0 onward.
Removing or renaming any of them requires a minor version bump and a
deprecation period of at least one minor release.

### Classes and types

| Name | Module | Status |
|------|--------|--------|
| `Token` | `tokenizer` | Stable — frozen dataclass |
| `CreativeTokenizer` | `tokenizer` | Stable |
| `CliticRules` | `tokenizer` | Stable — frozen dataclass |
| `BpeTokenizer` | `bpe_tokenizer` | Stable |
| `BpeMerges` | `trainer.bpe` | Stable |
| `BpeTrainer` | `trainer.bpe` | Stable |
| `NormalizedText` | `normalization` | Stable — frozen dataclass |
| `NormalizationProfile` | `normalization` | Stable — enum |

### Functions

| Name | Module | Status |
|------|--------|--------|
| `normalize_text` | `normalization` | Stable |
| `pretokenize` | `pretokenizer` | Stable |

### Span contract

The following invariant is guaranteed for every `Token` returned by
`CreativeTokenizer.tokenize` and `BpeTokenizer.tokenize`:

```python
source_text[token.start : token.end] == token.text
```

### Deprecation policy

* Removals or signature-breaking changes require a minor version bump
  (e.g. 0.1 → 0.2).
* Deprecated features will emit a `DeprecationWarning` for at least one
  minor release before removal.
* Default parameter values will not change in patch releases.

## Linguistics and Knowledge sub-packages

These are currently **experimental** and may change between minor
releases.  They will be promoted to stable status once acceptance
criteria are met (documented in the roadmap).
