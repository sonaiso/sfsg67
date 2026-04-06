from creative_tokenizer.morphology.grapheme_atoms import (
    consonantal_skeleton,
    consonantal_skeleton_id,
    grapheme_atom_id,
    grapheme_clusters,
    grapheme_surface_id,
)

_FATHA = "\u064e"
_KASRA = "\u0650"
_TANWIN_DAMM = "\u064c"


def test_grapheme_clusters_plain_word() -> None:
    assert grapheme_clusters("كتب") == [("ك", ()), ("ت", ()), ("ب", ())]


def test_grapheme_clusters_with_diacritics() -> None:
    clusters = grapheme_clusters("كَتَبَ")
    assert len(clusters) == 3
    assert clusters[0][0] == "ك"
    assert _FATHA in clusters[0][1]


def test_grapheme_clusters_skips_tatweel() -> None:
    assert [c for c, _ in grapheme_clusters("كـتب")] == ["ك", "ت", "ب"]


def test_consonantal_skeleton_plain_word_unchanged() -> None:
    assert consonantal_skeleton("كتاب") == ("ك", "ت", "ا", "ب")


def test_consonantal_skeleton_strips_diacritics() -> None:
    assert consonantal_skeleton("كِتَابٌ") == ("ك", "ت", "ا", "ب")


def test_consonantal_skeleton_id_is_deterministic() -> None:
    assert consonantal_skeleton_id("كتاب") == consonantal_skeleton_id("كتاب")


def test_consonantal_skeleton_id_diacritics_do_not_change_id() -> None:
    assert consonantal_skeleton_id("كتاب") == consonantal_skeleton_id("كِتَابٌ")


def test_consonantal_skeleton_id_distinct_for_different_skeletons() -> None:
    assert consonantal_skeleton_id("كتب") != consonantal_skeleton_id("ذهب")


def test_grapheme_atom_id_same_base_different_marks() -> None:
    assert grapheme_atom_id("ك", (_FATHA,)) != grapheme_atom_id("ك", (_KASRA,))


def test_grapheme_atom_id_no_marks_vs_with_marks() -> None:
    assert grapheme_atom_id("ك", ()) != grapheme_atom_id("ك", (_FATHA,))


def test_grapheme_surface_id_is_deterministic() -> None:
    assert grapheme_surface_id("شمس") == grapheme_surface_id("شمس")


def test_grapheme_surface_id_sensitive_to_diacritics() -> None:
    assert grapheme_surface_id("كَ") != grapheme_surface_id("ك")


def test_consonantal_skeleton_id_ignores_diacritics_grapheme_surface_does_not() -> None:
    assert consonantal_skeleton_id("كَ") == consonantal_skeleton_id("ك")
    assert grapheme_surface_id("كَ") != grapheme_surface_id("ك")
