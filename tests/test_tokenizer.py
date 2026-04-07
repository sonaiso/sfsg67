from creative_tokenizer import CreativeTokenizer


def test_tokenize_preserves_original_spans() -> None:
    text = "مرحبًا، يا عالم!"
    tokenizer = CreativeTokenizer()

    tokens = tokenizer.tokenize(text)

    assert [token.normalized for token in tokens] == ["مرحبا", "،", "يا", "عالم", "!"]
    assert [(token.start, token.end) for token in tokens] == [
        (0, 6),
        (6, 7),
        (8, 10),
        (11, 15),
        (15, 16),
    ]
    assert [text[token.start : token.end] for token in tokens] == [token.text for token in tokens]


def test_tokenize_segments_clitics_when_enabled() -> None:
    text = "وبالكتاب ذهبنا"
    tokenizer = CreativeTokenizer(segment_clitics=True)

    tokens = tokenizer.tokenize(text)

    assert [token.normalized for token in tokens] == ["و", "ب", "الكتاب", "ذهب", "نا"]
    assert [(token.start, token.end) for token in tokens] == [
        (0, 1),
        (1, 2),
        (2, 8),
        (9, 12),
        (12, 14),
    ]


def test_tokenize_keeps_whole_word_without_clitic_segmentation() -> None:
    text = "وبالكتاب"
    tokenizer = CreativeTokenizer(segment_clitics=False)

    tokens = tokenizer.tokenize(text)

    assert [token.normalized for token in tokens] == ["وبالكتاب"]
    assert [(token.start, token.end) for token in tokens] == [(0, 8)]


def test_normalization_maps_removed_diacritics_to_original_slice() -> None:
    text = "قُرْآن"
    tokenizer = CreativeTokenizer()

    tokens = tokenizer.tokenize(text)

    assert len(tokens) == 1
    assert tokens[0].normalized == "قران"
    assert tokens[0].text == text
    assert (tokens[0].start, tokens[0].end) == (0, len(text))


# ---- Punctuation & mixed-script span tests ----


def test_tokenize_arabic_question_mark_preserves_spans() -> None:
    text = "ماذا؟"
    tokens = CreativeTokenizer().tokenize(text)
    assert [t.normalized for t in tokens] == ["ماذا", "؟"]
    for t in tokens:
        assert t.text == text[t.start : t.end]


def test_tokenize_sequential_punctuation_preserves_spans() -> None:
    text = "!!؟"
    tokens = CreativeTokenizer().tokenize(text)
    for t in tokens:
        assert t.text == text[t.start : t.end]
    assert [t.normalized for t in tokens] == ["!", "!", "؟"]


def test_tokenize_arabic_indic_digits_span() -> None:
    text = "عام ٢٠٢٤"
    tokens = CreativeTokenizer().tokenize(text)
    assert [t.normalized for t in tokens] == ["عام", "٢٠٢٤"]
    for t in tokens:
        assert t.text == text[t.start : t.end]


def test_tokenize_mixed_arabic_latin_spans() -> None:
    text = "لغة Python جميلة"
    tokens = CreativeTokenizer().tokenize(text)
    for t in tokens:
        assert t.text == text[t.start : t.end]


def test_tokenize_arabic_semicolon_preserves_spans() -> None:
    text = "قال؛ ذهب"
    tokens = CreativeTokenizer().tokenize(text)
    assert [t.normalized for t in tokens] == ["قال", "؛", "ذهب"]
    for t in tokens:
        assert t.text == text[t.start : t.end]
