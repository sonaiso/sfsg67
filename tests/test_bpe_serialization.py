import json

import pytest

from creative_tokenizer.bpe_tokenizer import BpeTokenizer
from creative_tokenizer.trainer.bpe import BpeMerges, BpeTrainer


def _trained(vocab_size: int = 20) -> BpeMerges:
    return BpeTrainer(vocab_size=vocab_size).train(["كتاب"] * 10)


# ------------------------------------------------------------------
# to_dict / from_dict
# ------------------------------------------------------------------


def test_to_dict_has_required_schema_fields() -> None:
    data = _trained().to_dict()
    assert data["format_version"] == 1
    assert data["model_type"] == "bpe"
    assert isinstance(data["merges"], list)
    assert isinstance(data["vocab"], dict)


def test_merges_serialized_as_two_element_lists() -> None:
    data = _trained().to_dict()
    for item in data["merges"]:
        assert isinstance(item, list)
        assert len(item) == 2
        assert all(isinstance(s, str) for s in item)


def test_to_dict_from_dict_roundtrip() -> None:
    merges = _trained()
    restored = BpeMerges.from_dict(merges.to_dict())
    assert restored.merges == merges.merges
    assert restored.vocab == merges.vocab


def test_from_dict_rejects_wrong_format_version() -> None:
    data = _trained().to_dict()
    data["format_version"] = 99
    with pytest.raises(ValueError, match="format_version"):
        BpeMerges.from_dict(data)


def test_from_dict_rejects_wrong_model_type() -> None:
    data = _trained().to_dict()
    data["model_type"] = "unigram"
    with pytest.raises(ValueError, match="model_type"):
        BpeMerges.from_dict(data)


def test_from_dict_rejects_merge_with_wrong_length() -> None:
    data = _trained().to_dict()
    data["merges"] = [["only_one"]]
    with pytest.raises(ValueError):
        BpeMerges.from_dict(data)


def test_from_dict_rejects_non_string_merge_elements() -> None:
    data = _trained().to_dict()
    data["merges"] = [[1, 2]]
    with pytest.raises(ValueError):
        BpeMerges.from_dict(data)


def test_from_dict_rejects_non_list_merges() -> None:
    data = _trained().to_dict()
    data["merges"] = "bad"
    with pytest.raises(ValueError, match="'merges' must be a list"):
        BpeMerges.from_dict(data)


def test_from_dict_rejects_non_dict_vocab() -> None:
    data = _trained().to_dict()
    data["vocab"] = [1, 2, 3]
    with pytest.raises(ValueError, match="'vocab' must be a dict"):
        BpeMerges.from_dict(data)


# ------------------------------------------------------------------
# save_json / load_json
# ------------------------------------------------------------------


def test_save_load_json_roundtrip(tmp_path: pytest.TempPathFactory) -> None:
    merges = _trained()
    path = tmp_path / "model.json"  # type: ignore[operator]
    merges.save_json(path)
    restored = BpeMerges.load_json(path)
    assert restored.merges == merges.merges
    assert restored.vocab == merges.vocab


def test_saved_json_is_human_readable(tmp_path: pytest.TempPathFactory) -> None:
    path = tmp_path / "model.json"  # type: ignore[operator]
    _trained().save_json(path)
    raw = path.read_text(encoding="utf-8")  # type: ignore[union-attr]
    parsed = json.loads(raw)
    assert parsed["model_type"] == "bpe"
    assert "\n" in raw


def test_load_json_rejects_invalid_json(tmp_path: pytest.TempPathFactory) -> None:
    path = tmp_path / "bad.json"  # type: ignore[operator]
    path.write_text("not json {{{", encoding="utf-8")  # type: ignore[union-attr]
    with pytest.raises(Exception):
        BpeMerges.load_json(path)


def test_load_json_rejects_non_object_root(tmp_path: pytest.TempPathFactory) -> None:
    path = tmp_path / "list.json"  # type: ignore[operator]
    path.write_text("[1, 2, 3]", encoding="utf-8")  # type: ignore[union-attr]
    with pytest.raises(ValueError, match="JSON root must be an object"):
        BpeMerges.load_json(path)


# ------------------------------------------------------------------
# Behavioral stability after load
# ------------------------------------------------------------------


def test_encode_stable_after_save_load(tmp_path: pytest.TempPathFactory) -> None:
    merges = _trained()
    ids_before = BpeTokenizer(merges).encode("كتاب")
    path = tmp_path / "model.json"  # type: ignore[operator]
    merges.save_json(path)
    ids_after = BpeTokenizer(BpeMerges.load_json(path)).encode("كتاب")
    assert ids_before == ids_after


def test_decode_stable_after_save_load(tmp_path: pytest.TempPathFactory) -> None:
    merges = _trained()
    tokenizer = BpeTokenizer(merges)
    ids = tokenizer.encode("كتاب")
    path = tmp_path / "model.json"  # type: ignore[operator]
    merges.save_json(path)
    assert BpeTokenizer(BpeMerges.load_json(path)).decode(ids) == tokenizer.decode(ids)


def test_spans_stable_after_save_load(tmp_path: pytest.TempPathFactory) -> None:
    merges = _trained()
    path = tmp_path / "model.json"  # type: ignore[operator]
    merges.save_json(path)
    restored = BpeMerges.load_json(path)
    text = "كتاب جديد"
    for token in BpeTokenizer(restored).tokenize(text):
        assert token.text == text[token.start : token.end]
