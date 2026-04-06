# Roadmap

## Completed

- Baseline rule-based tokenizer with diacritic normalization and clitic segmentation.
- Stable span contract (`token.text == source[start:end]`) enforced across backends.
- Shared `pretokenizer.py` layer — normalization + word-boundary split reused by all backends.
- `BpeTrainer` — trains merge rules from a raw-text corpus.
- `BpeTokenizer` — encode/decode and span-preserving `tokenize()` using BPE merges.
- `BpeMerges` JSON serialization — versioned artifact schema with `save_json`/`load_json`;
  encode/decode/span behavior guaranteed identical after roundtrip.
- `morphology/` subpackage — fractal identity system for Arabic word forms:
  Unicode surface, consonantal skeleton, lexical type, independence,
  semantic feature envelope (Θ16 tags), relational argument frame (Γ7 roles),
  and unified word identity 𝕃(w). Fully independent of the tokenizer pipeline.

## Near Term

- Corpus-driven evaluation fixtures with ground-truth segmentations.
- Expand punctuation and mixed-script (Latin/Arabic) test coverage.

## Next Phase

- `UnigramTrainer` and `UnigramTokenizer` under `trainer/unigram.py`.
- Reproducible benchmark suite comparing backends on fixed corpora.
- DAG interning layer for compact storage of fractal identities.

## Longer Term

- Dataset adapters for common Arabic NLP corpora (e.g., OSIAN, CAMeL).
- Tokenizer configuration profiles (presets for different domains).
- Span stability tracking across releases to catch silent regressions.