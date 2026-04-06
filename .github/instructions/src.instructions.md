---
applyTo: "src/**/*.py"
---

When editing tokenizer source files:

- Preserve the contract that token spans index the original input string.
- Keep normalization and segmentation logic separate.
- Prefer typed, small helper functions over dense inline branching.
- Do not introduce morphology-heavy behavior into the default tokenizer path.
- Update tests whenever token text, normalization, or spans could change.
