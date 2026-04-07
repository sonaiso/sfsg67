import json

import pytest

from creative_tokenizer.trainer.unigram import UnigramModel, UnigramTrainer
from creative_tokenizer.unigram_tokenizer import UnigramTokenizer


def _trained(vocab_size: int = 20) -> UnigramModel:
    return UnigramTrainer(vocab_size=vocab_size).train(["كتاب"] * 10)


# ------------------------------------------------------------------
# to_dict / from_dict
# ------------------------------------------------------------------


def test_to_dict_has_required_schema_fields() -> None:
    data = _trained().to_dict()
    assert data["format_version"] == 1
    assert data["model_type"] == "unigram"
    assert isinstance(data["vocab"], dict)


def test_to_dict_from_dict_roundtrip() -> None:
    model = _trained()
    restored = UnigramModel.from_dict(model.to_dict())
    assert restored.vocab == model.vocab


def test_from_dict_rejects_wrong_format_version() -> None:
    data = _trained().to_dict()
    data["format_version"] = 99
    with pytest.raises(ValueError, match="format_version"):
        UnigramModel.from_dict(data)


def test_from_dict_rejects_wrong_model_type() -> None:
    data = _trained().to_dict()
    data["model_type"] = "bpe"
    with pytest.raises(ValueError, match="model_type"):
        UnigramModel.from_dict(data)


def test_from_dict_rejects_non_dict_vocab() -> None:
    data = _trained().to_dict()
    data["vocab"] = [1, 2, 3]
    with pytest.raises(ValueError, match="'vocab' must be a dict"):
        UnigramModel.from_dict(data)


def test_from_dict_rejects_non_numeric_vocab_values() -> None:
    data = _trained().to_dict()
    data["vocab"] = {"a": "bad"}
    with pytest.raises(ValueError, match="Vocab values must be numeric"):
        UnigramModel.from_dict(data)


# ------------------------------------------------------------------
# save_json / load_json
# ------------------------------------------------------------------


def test_save_load_json_roundtrip(tmp_path: pytest.TempPathFactory) -> None:
    model = _trained()
    path = tmp_path / "model.json"  # type: ignore[operator]
    model.save_json(path)
    restored = UnigramModel.load_json(path)
    assert restored.vocab == model.vocab


def test_saved_json_is_human_readable(tmp_path: pytest.TempPathFactory) -> None:
    path = tmp_path / "model.json"  # type: ignore[operator]
    _trained().save_json(path)
    raw = path.read_text(encoding="utf-8")  # type: ignore[union-attr]
    parsed = json.loads(raw)
    assert parsed["model_type"] == "unigram"
    assert "\n" in raw


def test_load_json_rejects_invalid_json(tmp_path: pytest.TempPathFactory) -> None:
    path = tmp_path / "bad.json"  # type: ignore[operator]
    path.write_text("not json {{{", encoding="utf-8")  # type: ignore[union-attr]
    with pytest.raises(Exception):
        UnigramModel.load_json(path)


def test_load_json_rejects_non_object_root(tmp_path: pytest.TempPathFactory) -> None:
    path = tmp_path / "list.json"  # type: ignore[operator]
    path.write_text("[1, 2, 3]", encoding="utf-8")  # type: ignore[union-attr]
    with pytest.raises(ValueError, match="JSON root must be an object"):
        UnigramModel.load_json(path)


# ------------------------------------------------------------------
# Behavioral stability after load
# ------------------------------------------------------------------


def test_encode_stable_after_save_load(tmp_path: pytest.TempPathFactory) -> None:
    model = _trained()
    ids_before = UnigramTokenizer(model).encode("كتاب")
    path = tmp_path / "model.json"  # type: ignore[operator]
    model.save_json(path)
    ids_after = UnigramTokenizer(UnigramModel.load_json(path)).encode("كتاب")
    assert ids_before == ids_after


def test_decode_stable_after_save_load(tmp_path: pytest.TempPathFactory) -> None:
    model = _trained()
    tokenizer = UnigramTokenizer(model)
    ids = tokenizer.encode("كتاب")
    path = tmp_path / "model.json"  # type: ignore[operator]
    model.save_json(path)
    assert (
        UnigramTokenizer(UnigramModel.load_json(path)).decode(ids)
        == tokenizer.decode(ids)
    )


def test_spans_stable_after_save_load(tmp_path: pytest.TempPathFactory) -> None:
    model = _trained()
    path = tmp_path / "model.json"  # type: ignore[operator]
    model.save_json(path)
    restored = UnigramModel.load_json(path)
    text = "كتاب جديد"
    for token in UnigramTokenizer(restored).tokenize(text):
        assert token.text == text[token.start : token.end]
