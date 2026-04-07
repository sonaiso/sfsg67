# Architecture

See [charter.md](charter.md) for the official architectural charter
(الميثاق المعماري الرسمي) that defines the foundational principles, cognitive
nuclei pipeline, transition protocols, verification modes, and implementation
requirements governing this project.

## Layers

1. `normalization.py` — converts raw text into normalized text plus a positional
   mapping from normalized characters back to original indices.
2. `pretokenizer.py` — applies the word-boundary regex over normalized text and
   returns `PreToken` objects carrying both the normalized word and its span
   mapping. Shared by all tokenizer backends.
3. `tokenizer.py` — rule-based tokenizer with optional clitic segmentation.
   Delegates pre-tokenization to `pretokenizer.py`.
4. `trainer/bpe.py` — trains BPE merge rules from a corpus. Operates over
   pre-tokenized words; does not touch normalization directly.
5. `bpe_tokenizer.py` — encodes/decodes text and produces `Token` objects using
   learned BPE merge rules. Span contract is preserved.
6. `cli.py` — thin command-line wrapper around `CreativeTokenizer`.

## Span Contract

Every `Token` exposes:

- `text`: the exact original substring from the input text
- `normalized`: the normalized/BPE token form used internally
- `start`: inclusive start offset in the original text
- `end`: exclusive end offset in the original text

The critical invariant, upheld by all backends:

```python
token.text == source_text[token.start:token.end]
```

## Dependency Graph

```
normalization
    └── pretokenizer
            ├── tokenizer  (rule-based)
            ├── trainer/bpe
            └── bpe_tokenizer
```

## Extension Points

- Add richer normalization rules to `normalization.py` while preserving mapping.
- Add morphology hooks to `tokenizer.py` behind explicit feature flags.
- Add new trainer backends under `trainer/` (e.g., `trainer/unigram.py`).
- Add new tokenizer backends (e.g., `unigram_tokenizer.py`) reusing `pretokenizer.py`.

## Morphology Layer (Optional)

The `morphology/` subpackage provides a fractal identity system for Arabic word
analysis. It is **strictly independent** of the tokenizer pipeline and has no
effect on spans, normalization, or pretokenization.

### Mathematical Primitives (`fractal_storage.py`)

| Symbol | Function | Description |
|--------|----------|-------------|
| φ(u) | `phi(char)` | Unicode code-point identity: ord(u) |
| π(x,y) | `cantor_pair(x, y)` | Cantor pairing: (x+y)(x+y+1)//2 + y |
| π⁻¹ | `invert_cantor_pair(z)` | Inverse of Cantor pairing |
| F | `fractal_fold(values)` | F(x₁,…,xₙ) = π(x₁, F(x₂,…,xₙ)) |

### Word Identity Formula

```
𝕃(w) = π(U, π(Q, π(S, π(Θ, Γ))))

U  — unicode_surface(w)           raw Unicode surface, no code point discarded
Q  — π(π(C, K#), I)              skeleton + lexical type + independence
S  — carrier_id                    jamid / root / masdar / operator …
Θ  — semantic_envelope(features)  sorted feature-tag pairs
Γ  — relation_frame(roles)        sorted argument-role pairs
```

### Layers

| Module | Responsibility |
|--------|----------------|
| `fractal_storage.py` | φ, π, π⁻¹, F — mathematical primitives |
| `unicode_identity.py` | U(w) — full raw Unicode surface |
| `grapheme_atoms.py` | G(w), C(w) — cluster split and consonantal skeleton |
| `lexical_containers.py` | LexicalType, Independence, carrier builders |
| `semantic_envelope.py` | FeatureTag, Θ — 16 stable morpho-semantic tags |
| `relation_frame.py` | RoleTag, Γ — argument-role template |
| `word_identity.py` | WordIdentity, compute_word_identity |

### Extensibility Contract

- Adding new `FeatureTag` values does **not** change existing envelopes
  (sorted fold is stable under appended tags).
- Adding new `RoleTag` values does **not** change existing frames.
- Adding new `LexicalType` values does **not** affect existing carrier IDs.
- The fractal number system is preserved: all identities remain exact Python
  integers; a compact storage layer (DAG interning) can be built on top.

## Artifact Persistence

Trained models are serialized to JSON via `BpeMerges.save_json(path)` and
restored with `BpeMerges.load_json(path)`. The schema is versioned to allow
future backends without breaking existing files.

```json
{
  "format_version": 1,
  "model_type": "bpe",
  "merges": [["ك", "ت"], ...],
  "vocab": {"ك": 0, "ت": 1, "كت": 2, ...}
}
```

The `format_version` field is checked on load; mismatches raise `ValueError`
with a clear message. The `model_type` field is reserved for future backends
such as `"unigram"`. Behavioral identity (encode, decode, token spans) is
guaranteed between a freshly trained model and one restored from JSON.
