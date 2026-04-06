from creative_tokenizer.bpe_tokenizer import BpeTokenizer
from creative_tokenizer.trainer.bpe import BpeTrainer


def _train_on(corpus: list[str], vocab_size: int = 20) -> BpeTokenizer:
    merges = BpeTrainer(vocab_size=vocab_size).train(corpus)
    return BpeTokenizer(merges)


def test_bpe_tokenizer_encode_decode_roundtrip() -> None:
    tokenizer = _train_on(["كتاب"] * 10)
    ids = tokenizer.encode("كتاب")
    assert tokenizer.decode(ids) == "كتاب"


def test_bpe_tokenizer_preserves_span_contract() -> None:
    tokenizer = _train_on(["كتاب"] * 10)
    text = "كتاب جديد"
    for token in tokenizer.tokenize(text):
        assert token.text == text[token.start : token.end]


def test_bpe_tokenizer_handles_diacritics_spans() -> None:
    tokenizer = _train_on(["كتاب"] * 10)
    text = "كِتَاب"
    tokens = tokenizer.tokenize(text)
    assert len(tokens) >= 1
    for token in tokens:
        assert token.text == text[token.start : token.end]


def test_bpe_tokenizer_skips_unknown_pieces_in_encode() -> None:
    tokenizer = _train_on(["كتاب"] * 10)
    ids = tokenizer.encode("جديد")
    assert ids == []
