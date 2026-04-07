"""Formal consonant (𝒞), vowel (𝒱), and diacritic (𝒟) sets — §2 of the
formal hierarchical specification.

Each Arabic letter receives a classification along two orthogonal axes:

1. **Morphological role** — root consonant, augmentation letter, or
   functional particle letter.
2. **Phonological place** — labial, dental, alveolar, velar, guttural, …

Vowels are split into short (ḥarakāt), long (ا و ي when vocalic),
null (sukūn), and tanwīn.  A role function maps each vowel to the set
of linguistic functions it *can* carry.

Diacritics beyond vowels (shadda, hamza, madda, waṣla, …) form the set 𝒟.

All sets are frozen; identities are computed via fractal fold so that
higher layers can embed them by value.
"""

from __future__ import annotations

from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold

# ---------------------------------------------------------------------------
# §2.1  Consonant sets  (𝒞)
# ---------------------------------------------------------------------------


class ConsonantRole(IntEnum):
    """Morphological role of a consonant — §2.1."""

    ROOT = 1  # 𝒞_root — potential root consonants
    AUGMENT = 2  # 𝒞_aug  — حروف الزيادة (سألتمونيها)
    FUNC = 3  # 𝒞_func — functional / particle-only letters


class PlaceOfArticulation(IntEnum):
    """Phonological place of articulation — §2.1 phonetic partition."""

    LABIAL = 1  # شفوي      (ب م و ف)
    DENTAL = 2  # أسناني    (ث ذ ظ)
    ALVEOLAR = 3  # لثوي      (ت د ط ض ن ل ر س ز ص)
    PALATAL = 4  # غاري      (ش ج ي)
    VELAR = 5  # طبقي      (ك غ خ)
    UVULAR = 6  # لهوي      (ق)
    PHARYNGEAL = 7  # حلقي      (ح ع)
    GLOTTAL = 8  # حنجري     (ء هـ)


# Canonical code-point sets for each morphological role.

#: Root consonants — every Arabic letter that may participate in a trilateral
#: or quadrilateral root.  Practically every Arabic letter qualifies, but the
#: augmentation letters get *dual* classification.
CONSONANT_ROOT: frozenset[int] = frozenset(range(0x0621, 0x064B)) - {
    0x0627,  # alif — long vowel / hamza seat, not a root consonant on its own
    0x0629,  # tā marbūṭa — not a root letter
    0x0649,  # alif maqṣūra — not a root letter
}

#: The ten augmentation letters سألتمونيها (traditional mnemonic).
CONSONANT_AUGMENT: frozenset[int] = frozenset(
    {
        0x0633,  # س
        0x0623,  # أ (hamza on alif)
        0x0644,  # ل
        0x062A,  # ت
        0x0645,  # م
        0x0648,  # و
        0x0646,  # ن
        0x064A,  # ي
        0x0647,  # هـ
        0x0627,  # ا (alif)
    }
)

#: Functional / particle-only letters (overlap with augmentation is normal).
CONSONANT_FUNC: frozenset[int] = frozenset(
    {
        0x0648,  # و (conjunction / oath)
        0x0641,  # ف (conjunction / causal)
        0x0628,  # ب (preposition)
        0x0644,  # ل (preposition / lam al-taʿlīl)
        0x0643,  # ك (preposition / comparison)
    }
)

# Phonological place map:  code-point → PlaceOfArticulation
_PLACE_MAP: dict[int, PlaceOfArticulation] = {}
for _cp in (0x0628, 0x0645, 0x0648, 0x0641):
    _PLACE_MAP[_cp] = PlaceOfArticulation.LABIAL
for _cp in (0x062B, 0x0630, 0x0638):
    _PLACE_MAP[_cp] = PlaceOfArticulation.DENTAL
for _cp in (0x062A, 0x062F, 0x0637, 0x0636, 0x0646, 0x0644, 0x0631, 0x0633, 0x0632, 0x0635):
    _PLACE_MAP[_cp] = PlaceOfArticulation.ALVEOLAR
for _cp in (0x0634, 0x062C, 0x064A):
    _PLACE_MAP[_cp] = PlaceOfArticulation.PALATAL
for _cp in (0x0643, 0x063A, 0x062E):
    _PLACE_MAP[_cp] = PlaceOfArticulation.VELAR
_PLACE_MAP[0x0642] = PlaceOfArticulation.UVULAR
for _cp in (0x062D, 0x0639):
    _PLACE_MAP[_cp] = PlaceOfArticulation.PHARYNGEAL
for _cp in (0x0621, 0x0623, 0x0625, 0x0624, 0x0626, 0x0647):
    _PLACE_MAP[_cp] = PlaceOfArticulation.GLOTTAL


def consonant_role(cp: int) -> frozenset[ConsonantRole]:
    """Return the set of morphological roles a consonant code-point holds."""
    roles: set[ConsonantRole] = set()
    if cp in CONSONANT_ROOT:
        roles.add(ConsonantRole.ROOT)
    if cp in CONSONANT_AUGMENT:
        roles.add(ConsonantRole.AUGMENT)
    if cp in CONSONANT_FUNC:
        roles.add(ConsonantRole.FUNC)
    return frozenset(roles)


def place_of_articulation(cp: int) -> PlaceOfArticulation | None:
    """Return the phonological place, or *None* for non-consonantal code points."""
    return _PLACE_MAP.get(cp)


# ---------------------------------------------------------------------------
# §2.2  Vowel / ḥaraka sets  (𝒱)
# ---------------------------------------------------------------------------


class VowelKind(IntEnum):
    """Sub-classification of vowels and vocalic marks — §2.2."""

    SHORT = 1  # 𝒱_short   — فتحة، ضمة، كسرة
    LONG = 2  # 𝒱_long    — ا و ي (when vocalic)
    NULL = 3  # 𝒱_null    — سكون
    TANWEEN = 4  # 𝒱_tanween — ً ٌ ٍ


VOWEL_SHORT: frozenset[int] = frozenset({0x064E, 0x064F, 0x0650})
VOWEL_LONG: frozenset[int] = frozenset({0x0627, 0x0648, 0x064A})
VOWEL_NULL: frozenset[int] = frozenset({0x0652})
VOWEL_TANWEEN: frozenset[int] = frozenset({0x064B, 0x064C, 0x064D})

ALL_VOWELS: frozenset[int] = VOWEL_SHORT | VOWEL_LONG | VOWEL_NULL | VOWEL_TANWEEN


class VowelRole(IntEnum):
    """Linguistic functions a vowel *can* serve — §2.2 𝒮_V."""

    PHONETIC = 1  # صوتية
    DERIVATIONAL = 2  # اشتقاقية
    INFLECTIONAL = 3  # إعرابية
    TEMPORAL = 4  # زمنية
    NUMERIC = 5  # عددية
    GENDER = 6  # جنسية
    DEFINITE = 7  # تعريفية
    INDEFINITE = 8  # تنكيرية
    MASCULINE = 9  # تذكيرية
    FEMININE = 10  # تأنيثية


def vowel_kind(cp: int) -> VowelKind | None:
    """Classify a code-point into its vowel sub-set, or *None*."""
    if cp in VOWEL_SHORT:
        return VowelKind.SHORT
    if cp in VOWEL_LONG:
        return VowelKind.LONG
    if cp in VOWEL_NULL:
        return VowelKind.NULL
    if cp in VOWEL_TANWEEN:
        return VowelKind.TANWEEN
    return None


def vowel_roles(cp: int) -> frozenset[VowelRole]:
    """Return the potential linguistic roles a vowel code-point can carry.

    Every vowel is at least phonetic.  Short vowels and tanwīn can also be
    inflectional.  Short vowels can additionally be derivational.
    """
    kind = vowel_kind(cp)
    if kind is None:
        return frozenset()
    roles: set[VowelRole] = {VowelRole.PHONETIC}
    if kind in (VowelKind.SHORT, VowelKind.TANWEEN):
        roles.add(VowelRole.INFLECTIONAL)
    if kind == VowelKind.SHORT:
        roles.add(VowelRole.DERIVATIONAL)
    if kind == VowelKind.TANWEEN:
        roles.add(VowelRole.INDEFINITE)
    if kind == VowelKind.LONG:
        roles.add(VowelRole.DERIVATIONAL)
    return frozenset(roles)


# ---------------------------------------------------------------------------
# §2.3  Extra diacritical marks  (𝒟)
# ---------------------------------------------------------------------------


class DiacriticKind(IntEnum):
    """Non-vowel diacritical marks — §2.3."""

    SHADDA = 1  # شدة
    HAMZA = 2  # همزة
    MADDA = 3  # مد
    WASLA = 4  # وصلة
    SUKUN = 5  # سكون (overlap with vowel-null is intentional)
    STOP = 6  # علامات وقف


DIACRITIC_MARKS: frozenset[int] = frozenset(
    {
        0x0651,  # shadda
        0x0621,  # hamza (standalone)
        0x0653,  # madda above
        0x0671,  # alef wasla (ٱ) — special letter
        0x0652,  # sukun
        0x06D6,  # Quran stop mark (example)
    }
)


def diacritic_kind(cp: int) -> DiacriticKind | None:
    """Classify a code-point into its diacritic sub-set, or *None*."""
    _MAP: dict[int, DiacriticKind] = {
        0x0651: DiacriticKind.SHADDA,
        0x0621: DiacriticKind.HAMZA,
        0x0653: DiacriticKind.MADDA,
        0x0671: DiacriticKind.WASLA,
        0x0652: DiacriticKind.SUKUN,
        0x06D6: DiacriticKind.STOP,
    }
    return _MAP.get(cp)


class DiacriticRole(IntEnum):
    """Functional roles a diacritical mark can carry — §2.3 ℛ_D."""

    PHONOLOGICAL = 1  # صوتي
    MORPHOLOGICAL = 2  # صرفي
    ORTHOGRAPHIC = 3  # كتابي
    RECITATION = 4  # تجويدي


def diacritic_roles(cp: int) -> frozenset[DiacriticRole]:
    """Return the set of functional roles for a diacritical mark."""
    kind = diacritic_kind(cp)
    if kind is None:
        return frozenset()
    roles: set[DiacriticRole] = set()
    if kind in (DiacriticKind.SHADDA, DiacriticKind.SUKUN):
        roles.update({DiacriticRole.PHONOLOGICAL, DiacriticRole.MORPHOLOGICAL})
    if kind in (DiacriticKind.HAMZA, DiacriticKind.MADDA, DiacriticKind.WASLA):
        roles.update({DiacriticRole.PHONOLOGICAL, DiacriticRole.ORTHOGRAPHIC})
    if kind == DiacriticKind.STOP:
        roles.add(DiacriticRole.RECITATION)
    return frozenset(roles)


# ---------------------------------------------------------------------------
# Fractal identities
# ---------------------------------------------------------------------------


def consonant_set_id(cps: frozenset[int]) -> int:
    """Compute a stable identity for a consonant sub-set via sorted fold."""
    if not cps:
        return 0
    return fractal_fold(sorted(cps))


def vowel_set_id(cps: frozenset[int]) -> int:
    """Compute a stable identity for a vowel sub-set via sorted fold."""
    if not cps:
        return 0
    return fractal_fold(sorted(cps))


def phonological_layer_id(ch: str) -> int:
    """Return a single fractal identity encoding consonant role + place + vowel kind.

    Combines all §2 classifications for a single character.
    Returns 0 for characters outside the Arabic phonological system.
    """
    cp = ord(ch)
    roles = consonant_role(cp)
    place = place_of_articulation(cp)
    vkind = vowel_kind(cp)
    dkind = diacritic_kind(cp)

    parts: list[int] = [cp]

    if roles:
        parts.append(cantor_pair(1, fractal_fold(sorted(int(r) for r in roles))))
    if place is not None:
        parts.append(cantor_pair(2, int(place)))
    if vkind is not None:
        parts.append(cantor_pair(3, int(vkind)))
    if dkind is not None:
        parts.append(cantor_pair(4, int(dkind)))

    if len(parts) == 1:
        return 0  # outside Arabic phonological system
    return fractal_fold(parts)
