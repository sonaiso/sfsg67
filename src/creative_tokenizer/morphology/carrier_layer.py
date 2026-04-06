from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class CarrierTag(IntEnum):
    """Case/mood carrier marker tags.  Values are stable across versions.

    Encodes *what* carries the grammatical information, not the information
    itself.  Distinct from diacritics stored in grapheme clusters.
    """

    SHORT_VOWEL = 1       # short vowel carries the marking (standard declension)
    ALIF = 2              # alif carrier (e.g. nominative of five nouns: أبوه)
    WAW = 3               # waw carrier  (e.g. genitive of sound masc plural)
    YA = 4                # ya carrier   (e.g. genitive of five nouns: أبيه)
    NUN = 5               # nun carrier  (thabot of five verbs)
    DELETED_NUN = 6       # deletion of nun as marker (جزم/نصب in five verbs)
    FATHA_AS_GENITIVE = 7 # fatha standing for kasra (diptote genitive)
    SUKUN = 8             # sukun as marker (jazm of sound verbs)
    SHADDA = 9            # shadda with vowel as marker


def carrier_layer_id(carriers: dict[CarrierTag, int]) -> int:
    """Carrier layer identity: F(π(tag, value), …) sorted by tag.

    Returns 0 for an empty carrier set.
    """
    if not carriers:
        return 0
    pairs = sorted(carriers.items())
    return fractal_fold([cantor_pair(int(tag), value) for tag, value in pairs])
