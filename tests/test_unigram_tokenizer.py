from creative_tokenizer.trainer.unigram import UnigramTrainer
from creative_tokenizer.unigram_tokenizer import UnigramTokenizer


def _train_on(corpus: list[str], vocab_size: int = 20) -> UnigramTokenizer:
    model = UnigramTrainer(vocab_size=vocab_size).train(corpus)
    return UnigramTokenizer(model)


def test_unigram_tokenizer_encode_decode_roundtrip() -> None:
    tokenizer = _train_on(["كتاب"] * 10)
    ids = tokenizer.encode("كتاب")
    assert tokenizer.decode(ids) == "كتاب"


def test_unigram_tokenizer_preserves_span_contract() -> None:
    tokenizer = _train_on(["كتاب"] * 10)
    text = "كتاب جديد"
    for token in tokenizer.tokenize(text):
        assert token.text == text[token.start : token.end]


def test_unigram_tokenizer_handles_diacritics_spans() -> None:
    tokenizer = _train_on(["كتاب"] * 10)
    text = "كِتَاب"
    tokens = tokenizer.tokenize(text)
    assert len(tokens) >= 1
    for token in tokens:
        assert token.text == text[token.start : token.end]


def test_unigram_tokenizer_unknown_word_falls_back_to_chars() -> None:
    tokenizer = _train_on(["كتاب"] * 10, vocab_size=5)
    text = "كتاب"
    tokens = tokenizer.tokenize(text)
    for token in tokens:
        assert token.text == text[token.start : token.end]


def test_unigram_tokenizer_multi_word() -> None:
    tokenizer = _train_on(["مرحبا عالم"] * 10, vocab_size=30)
    text = "مرحبا عالم"
    tokens = tokenizer.tokenize(text)
    reconstructed = "".join(t.normalized for t in tokens)
    assert reconstructed == "مرحباعالم"
    for token in tokens:
        assert token.text == text[token.start : token.end]
