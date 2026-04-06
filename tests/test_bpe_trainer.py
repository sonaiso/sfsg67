from creative_tokenizer.trainer.bpe import BpeMerges, BpeTrainer


def test_trainer_produces_bpe_merges() -> None:
    trainer = BpeTrainer(vocab_size=20)
    merges = trainer.train(["كتاب"] * 10)
    assert isinstance(merges, BpeMerges)
    assert len(merges.merges) > 0
    assert merges.size > 0


def test_trainer_merges_most_frequent_pair_first() -> None:
    trainer = BpeTrainer(vocab_size=10)
    merges = trainer.train(["كتكت"] * 20)
    assert ("ك", "ت") in merges.merges
    assert merges.merges[0] == ("ك", "ت")


def test_trainer_vocab_size_is_respected() -> None:
    trainer = BpeTrainer(vocab_size=6)
    merges = trainer.train(["أبجد"] * 5)
    assert merges.size <= trainer.vocab_size


def test_trainer_empty_corpus_returns_empty_merges() -> None:
    trainer = BpeTrainer(vocab_size=10)
    merges = trainer.train([])
    assert merges.merges == []
    assert merges.vocab == {}
