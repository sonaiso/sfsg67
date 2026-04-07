from creative_tokenizer.trainer.unigram import UnigramModel, UnigramTrainer


def test_trainer_produces_unigram_model() -> None:
    trainer = UnigramTrainer(vocab_size=20)
    model = trainer.train(["كتاب"] * 10)
    assert isinstance(model, UnigramModel)
    assert model.size > 0


def test_trainer_respects_vocab_size() -> None:
    trainer = UnigramTrainer(vocab_size=6)
    model = trainer.train(["كتاب"] * 10)
    assert model.size <= 6


def test_trainer_empty_corpus_returns_empty_model() -> None:
    trainer = UnigramTrainer(vocab_size=10)
    model = trainer.train([])
    assert model.vocab == {}
    assert model.size == 0


def test_trainer_single_char_words() -> None:
    trainer = UnigramTrainer(vocab_size=5)
    model = trainer.train(["ا"] * 10)
    assert "ا" in model.vocab


def test_trainer_preserves_all_base_characters() -> None:
    trainer = UnigramTrainer(vocab_size=10)
    model = trainer.train(["كتاب"] * 20)
    for ch in "كتاب":
        assert ch in model.vocab, f"base character {ch!r} missing"


def test_trainer_log_probs_are_negative() -> None:
    trainer = UnigramTrainer(vocab_size=15)
    model = trainer.train(["كتاب مدرسة"] * 10)
    for piece, score in model.vocab.items():
        assert score <= 0.0, f"{piece!r} has positive log-prob {score}"
