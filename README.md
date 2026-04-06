# creative-tokenizer

Creative Tokenizer is a small Arabic-first tokenization project with a modern
Python package layout, explicit normalization, optional clitic segmentation, and
stable token spans.

## Features

- `src/` package layout with `pyproject.toml`
- Arabic-aware normalization with source-to-normalized index mapping
- Token spans preserved against the original input text
- Optional `segment_clitics` mode for a baseline Arabic segmentation pass
- CLI for quick inspection
- `pytest`, GitHub Actions CI, and Copilot repository instructions

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
python -m creative_tokenizer.cli --text "وبالكتابِ ذهبنا." --segment-clitics
```

## Example

```python
from creative_tokenizer import CreativeTokenizer

tokenizer = CreativeTokenizer(segment_clitics=True)
tokens = tokenizer.tokenize("وبالكتابِ ذهبنا.")

for token in tokens:
	print(token.text, token.start, token.end)
```

## Repository Layout

- `src/creative_tokenizer/`: package source
- `tests/`: unit tests
- `docs/`: architecture notes and roadmap
- `.github/`: CI and Copilot instructions

## Validation

- `pytest`
- `python -m compileall src tests`
- `ruff check .`
- `mypy src`