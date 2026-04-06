# Creative Tokenizer Copilot Instructions

This repository values correctness over novelty.

- Preserve token spans against the original input text.
- Treat normalization as a distinct, testable layer.
- Keep tokenizer heuristics explicit and small.
- Avoid changes that silently alter segmentation behavior without tests.
- Prefer adding regression tests for Arabic punctuation, diacritics, and clitic boundaries.
- Keep CLI changes thin and delegate logic to library code.
