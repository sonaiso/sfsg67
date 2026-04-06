---
applyTo: "tests/**/*.py"
---

When editing tests:

- Assert both normalized token text and original spans.
- Prefer small behavior-focused fixtures over large text blobs.
- Add regression coverage for Arabic punctuation, diacritic removal, and clitic segmentation.
- Keep tests readable enough to document tokenizer behavior.
