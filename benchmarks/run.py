"""Reproducible benchmark suite comparing tokenizer backends.

Runs the rule-based tokenizer, BPE tokenizer, and unigram tokenizer on a fixed
Arabic corpus and reports:

- **Tokens/sec**: throughput of the tokenize() call.
- **Vocab coverage**: fraction of corpus characters covered by the vocabulary.
- **Token count**: total tokens produced from the fixed corpus.
- **Avg token length**: mean normalized-token character length.

Usage::

    python benchmarks/run.py
    python benchmarks/run.py --iterations 20
"""

from __future__ import annotations

import argparse
import sys
import time

sys.path.insert(0, "src")

from creative_tokenizer import BpeTrainer, CreativeTokenizer, Token  # noqa: E402
from creative_tokenizer.trainer.unigram import UnigramTrainer  # noqa: E402
from creative_tokenizer.unigram_tokenizer import UnigramTokenizer  # noqa: E402
from creative_tokenizer.bpe_tokenizer import BpeTokenizer  # noqa: E402

# ---------------------------------------------------------------------------
# Fixed benchmark corpus — representative Arabic text
# ---------------------------------------------------------------------------

_CORPUS_LINES = [
    "ذهب الطالب إلى المدرسة وكتب الدرس في الدفتر",
    "وبالكتاب تعلمنا كيف نقرأ ونكتب بالعربية",
    "الحمد لله رب العالمين الرحمن الرحيم مالك يوم الدين",
    "في البداية خلق الله السماوات والأرض",
    "قال المعلم للطلاب اقرأوا الكتاب واكتبوا الإجابات",
    "مرحبا، كيف حالك؟ أنا بخير والحمد لله",
    "العلم نور والجهل ظلام",
    "لغة Python مفيدة جدا في مجال NLP والذكاء الاصطناعي",
    "سافرنا إلى القاهرة وزرنا الأهرامات والمتحف المصري",
    "قرأت كتابا عن تاريخ الحضارة العربية الإسلامية",
]


def _measure_throughput(
    tokenize_fn: object,
    text: str,
    iterations: int,
) -> tuple[float, list[Token]]:
    """Return (tokens_per_second, last_tokens)."""
    tokens: list[Token] = []
    start = time.perf_counter()
    for _ in range(iterations):
        tokens = tokenize_fn(text)  # type: ignore[operator]
    elapsed = time.perf_counter() - start
    total_tokens = len(tokens) * iterations
    tps = total_tokens / elapsed if elapsed > 0 else float("inf")
    return tps, tokens


def _vocab_coverage(tokens: list[Token], text: str) -> float:
    """Fraction of text characters covered by token spans."""
    covered = set()
    for t in tokens:
        for i in range(t.start, t.end):
            covered.add(i)
    non_space = {i for i, ch in enumerate(text) if not ch.isspace()}
    if not non_space:
        return 1.0
    return len(covered & non_space) / len(non_space)


def _avg_token_len(tokens: list[Token]) -> float:
    if not tokens:
        return 0.0
    return sum(len(t.normalized) for t in tokens) / len(tokens)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark tokenizer backends.")
    parser.add_argument(
        "--iterations", type=int, default=10, help="Number of timing iterations"
    )
    args = parser.parse_args()

    corpus_text = "\n".join(_CORPUS_LINES)

    # --- Rule-based ---
    rule_tok = CreativeTokenizer(segment_clitics=False)
    rule_seg_tok = CreativeTokenizer(segment_clitics=True)

    # --- BPE ---
    bpe_merges = BpeTrainer(vocab_size=50).train(_CORPUS_LINES * 5)
    bpe_tok = BpeTokenizer(bpe_merges)

    # --- Unigram ---
    unigram_model = UnigramTrainer(vocab_size=50).train(_CORPUS_LINES * 5)
    uni_tok = UnigramTokenizer(unigram_model)

    backends: list[tuple[str, object]] = [
        ("Rule-based (no clitics)", rule_tok.tokenize),
        ("Rule-based (clitics)", rule_seg_tok.tokenize),
        ("BPE (vocab=50)", bpe_tok.tokenize),
        ("Unigram (vocab=50)", uni_tok.tokenize),
    ]

    header = f"{'Backend':<30} {'Tok/s':>10} {'Tokens':>8} {'AvgLen':>8} {'Coverage':>10}"
    print(header)
    print("-" * len(header))

    for name, fn in backends:
        tps, tokens = _measure_throughput(fn, corpus_text, args.iterations)
        coverage = _vocab_coverage(tokens, corpus_text)
        avg_len = _avg_token_len(tokens)
        print(
            f"{name:<30} {tps:>10.0f} {len(tokens):>8} {avg_len:>8.2f} {coverage:>9.1%}"
        )

    print(f"\nCorpus: {len(corpus_text)} chars, {len(_CORPUS_LINES)} lines")
    print(f"Iterations: {args.iterations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
