"""Extended span-contract tests — Sprint 1.1.

Every test asserts the core invariant:
    token.text == source_text[token.start : token.end]
across a variety of Arabic edge cases: full tashkeel, waqf marks,
tatweel stretching, Arabic-Indic digits, mixed-script text, multi-clitic
words, independent particles, empty input, whitespace-only input, and
orphaned diacritics.
"""

from creative_tokenizer import CreativeTokenizer


def _assert_span_contract(text: str, tokens: list) -> None:  # type: ignore[type-arg]
    """Every token's .text must equal the original slice."""
    for token in tokens:
        assert text[token.start : token.end] == token.text, (
            f"span contract violated: text[{token.start}:{token.end}]="
            f"{text[token.start:token.end]!r} != token.text={token.text!r}"
        )


# ── 1. Fully-vowelled Quranic text ──────────────────────────────────


def test_span_full_tashkeel() -> None:
    text = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
    tokens = CreativeTokenizer().tokenize(text)
    assert len(tokens) >= 1
    _assert_span_contract(text, tokens)


# ── 2. Waqf (end-of-ayah) mark ──────────────────────────────────────


def test_span_waqf_mark() -> None:
    text = "مَالِكِ يَوْمِ الدِّينِ ۝"
    tokens = CreativeTokenizer().tokenize(text)
    _assert_span_contract(text, tokens)
    # The waqf sign ۝ should appear as a standalone token
    waqf_tokens = [t for t in tokens if "۝" in t.text]
    assert len(waqf_tokens) == 1


# ── 3. Tatweel (kashida stretching) ─────────────────────────────────


def test_span_tatweel() -> None:
    text = "كـــتاب"
    tokens = CreativeTokenizer().tokenize(text)
    _assert_span_contract(text, tokens)
    assert len(tokens) >= 1
    # Tatweel is removed from normalized form but span covers original
    assert tokens[0].text == text


# ── 4. Arabic-Indic + Western digits ────────────────────────────────


def test_span_mixed_digits() -> None:
    text = "عام ٢٠٢٤ ومبلغ 500"
    tokens = CreativeTokenizer().tokenize(text)
    _assert_span_contract(text, tokens)
    normalized = [t.normalized for t in tokens]
    assert "عام" in normalized


# ── 5. Mixed Arabic / Latin script ──────────────────────────────────


def test_span_mixed_script() -> None:
    text = "قال: Hello World قالت"
    tokens = CreativeTokenizer().tokenize(text)
    _assert_span_contract(text, tokens)
    normalized = [t.normalized for t in tokens]
    assert "Hello" in normalized
    assert "World" in normalized
    assert "قال" in normalized


# ── 6. Multi-prefix clitic segmentation ─────────────────────────────


def test_span_multi_clitic() -> None:
    text = "فبالكتابِ"
    tokenizer = CreativeTokenizer(segment_clitics=True)
    tokens = tokenizer.tokenize(text)
    _assert_span_contract(text, tokens)
    # Should produce at least prefix pieces + stem
    assert len(tokens) >= 2


# ── 7. Independent particles (no root) ──────────────────────────────


def test_span_particles() -> None:
    text = "إلى على في من"
    tokens = CreativeTokenizer().tokenize(text)
    _assert_span_contract(text, tokens)
    assert len(tokens) == 4


# ── 8. Empty input ──────────────────────────────────────────────────


def test_span_empty_input() -> None:
    tokens = CreativeTokenizer().tokenize("")
    assert tokens == []


# ── 9. Whitespace-only input ────────────────────────────────────────


def test_span_whitespace_only() -> None:
    tokens = CreativeTokenizer().tokenize(" ")
    assert tokens == []


# ── 10. Orphaned diacritics (no base characters) ────────────────────


def test_span_orphaned_diacritics() -> None:
    text = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652"
    tokens = CreativeTokenizer().tokenize(text)
    # Diacritics alone are stripped during normalization; may yield nothing
    # Key: no span-contract crash
    _assert_span_contract(text, tokens)
