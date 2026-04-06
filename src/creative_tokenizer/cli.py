from __future__ import annotations

import argparse
import json
import sys

from .tokenizer import CreativeTokenizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tokenize Arabic text with stable spans.")
    parser.add_argument("--text", help="Text to tokenize. If omitted, stdin is used.")
    parser.add_argument(
        "--segment-clitics",
        action="store_true",
        help="Split a small baseline set of Arabic prefixes and suffixes.",
    )
    parser.add_argument("--json", action="store_true", help="Print tokens as JSON.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    text = args.text if args.text is not None else sys.stdin.read()

    tokenizer = CreativeTokenizer(segment_clitics=args.segment_clitics)
    tokens = tokenizer.tokenize(text)

    if args.json:
        print(json.dumps([token.to_dict() for token in tokens], ensure_ascii=False, indent=2))
        return 0

    for token in tokens:
        print(f"{token.normalized}\t{token.start}:{token.end}\t{token.text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
