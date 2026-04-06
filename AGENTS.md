# AGENTS.md

## Mission

Keep this repository focused on a small, inspectable tokenizer core with stable
spans and predictable Arabic normalization.

## Rules

- Preserve token spans against the original input text.
- Keep normalization behavior explicit and centrally defined.
- Prefer small, reversible tokenizer changes with tests that pin behavior.
- Do not add morphology-heavy heuristics to the core tokenizer without making
  them optional.
- Keep tests outside `src/` and cover both text and span behavior.

## Working Style

- When changing tokenization logic, add or update tests first or in the same
  change.
- Avoid broad refactors that obscure span mapping.
- Keep the CLI thin; core behavior belongs in the library.
