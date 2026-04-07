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


# ---- Punctuation & mixed-script coverage ----


def test_pretokenize_arabic_question_mark() -> None:
    pretokens = pretokenize("ماذا؟")
    words = [pt.word for pt in pretokens]
    assert words == ["ماذا", "؟"]


def test_pretokenize_arabic_semicolon() -> None:
    pretokens = pretokenize("قال؛ ذهب")
    words = [pt.word for pt in pretokens]
    assert words == ["قال", "؛", "ذهب"]


def test_pretokenize_sequential_punctuation() -> None:
    pretokens = pretokenize("!!؟")
    words = [pt.word for pt in pretokens]
    assert words == ["!", "!", "؟"]


def test_pretokenize_arabic_indic_digits() -> None:
    pretokens = pretokenize("عام ٢٠٢٤")
    words = [pt.word for pt in pretokens]
    assert words == ["عام", "٢٠٢٤"]


def test_pretokenize_mixed_arabic_latin_sentence() -> None:
    pretokens = pretokenize("لغة Python جميلة")
    words = [pt.word for pt in pretokens]
    assert words == ["لغه", "Python", "جميله"]


def test_pretokenize_latin_with_numbers() -> None:
    pretokens = pretokenize("Python3")
    assert len(pretokens) == 1
    assert pretokens[0].word == "Python3"


def test_pretokenize_arabic_comma_between_words() -> None:
    pretokens = pretokenize("أحمد، علي")
    words = [pt.word for pt in pretokens]
    assert words == ["احمد", "،", "علي"]


def test_pretokenize_mixed_digits_western_and_indic() -> None:
    pretokens = pretokenize("2024 و ٢٠٢٤")
    words = [pt.word for pt in pretokens]
    assert words == ["2024", "و", "٢٠٢٤"]


def test_pretokenize_empty_string() -> None:
    assert pretokenize("") == []


def test_pretokenize_only_whitespace() -> None:
    assert pretokenize("   ") == []


def test_pretokenize_tatweel_removed_from_word() -> None:
    pretokens = pretokenize("كـتـاب")
    assert len(pretokens) == 1
    assert pretokens[0].word == "كتاب"
