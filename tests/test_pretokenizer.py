from creative_tokenizer.pretokenizer import pretokenize


def test_pretokenize_splits_arabic_words() -> None:
    pretokens = pretokenize("مرحبا يا عالم")
    assert [pt.word for pt in pretokens] == ["مرحبا", "يا", "عالم"]


def test_pretokenize_preserves_word_mapping() -> None:
    pretokens = pretokenize("مرحبا")
    assert len(pretokens) == 1
    assert pretokens[0].mapping == (0, 1, 2, 3, 4)


def test_pretokenize_strips_diacritics_in_word() -> None:
    pretokens = pretokenize("قُرْآن")
    assert len(pretokens) == 1
    assert pretokens[0].word == "قران"


def test_pretokenize_arabic_punctuation_is_separate_token() -> None:
    pretokens = pretokenize("مرحبا، عالم")
    assert [pt.word for pt in pretokens] == ["مرحبا", "،", "عالم"]


def test_pretokenize_mapping_skips_diacritic_positions() -> None:
    pretokens = pretokenize("كِتَاب")
    assert len(pretokens) == 1
    assert pretokens[0].word == "كتاب"
    assert pretokens[0].mapping == (0, 2, 4, 5)
