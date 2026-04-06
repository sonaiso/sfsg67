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
