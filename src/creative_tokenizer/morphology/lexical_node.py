"""Full lexical node — primary atom of the lexical store.

LexicalNode bundles all semantic / structural layer IDs into a single
economy-conscious node.  No content is stored here directly; every sub-field
is a *foreign-key* referencing an entry in another hub or store.

  lexeme_id  = F(π(1,sign_id), π(2,raw_unicode_id), π(3,skeleton_id),
                  π(4,root_id), π(5,pattern_id))
  meaning_id = F(π(1,signified_id), π(2,mutabaqa_id),
                  π(3,tadammun_id), π(4,iltizam_id))
  node_id    = π(lexeme_id, π(meaning_id, concept_class_id))

transfer_state_id = 0 means original lexical sense only (وضع أصلي).
metaphor_state_id = 0 means no metaphor currently active.
"""

from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair, fractal_fold


@dataclass(frozen=True, slots=True)
class LexicalNode:
    # --- identity layer ---
    sign_id: int
    raw_unicode_id: int
    skeleton_id: int
    lexeme_id: int        # F(sign, unicode, skeleton, root, pattern)
    root_id: int
    pattern_id: int
    # --- meaning layer ---
    signified_id: int
    mutabaqa_id: int
    tadammun_id: int
    iltizam_id: int
    meaning_id: int       # F(signified, mutabaqa, tadammun, iltizam)
    # --- classification ---
    concept_class_id: int
    transfer_state_id: int  # 0 = original only
    metaphor_state_id: int  # 0 = no metaphor
    # --- composite ---
    node_id: int            # π(lexeme_id, π(meaning_id, concept_class_id))


def make_lexical_node(
    sign_id: int,
    raw_unicode_id: int,
    skeleton_id: int,
    root_id: int,
    pattern_id: int,
    signified_id: int,
    mutabaqa_id: int,
    tadammun_id: int,
    iltizam_id: int,
    concept_class_id: int,
    transfer_state_id: int = 0,
    metaphor_state_id: int = 0,
) -> LexicalNode:
    """Build a LexicalNode; absent IDs should be passed as 0."""
    lexeme_id = fractal_fold(
        [
            cantor_pair(1, sign_id),
            cantor_pair(2, raw_unicode_id),
            cantor_pair(3, skeleton_id),
            cantor_pair(4, root_id),
            cantor_pair(5, pattern_id),
        ]
    )
    meaning_id = fractal_fold(
        [
            cantor_pair(1, signified_id),
            cantor_pair(2, mutabaqa_id),
            cantor_pair(3, tadammun_id),
            cantor_pair(4, iltizam_id),
        ]
    )
    node_id = cantor_pair(lexeme_id, cantor_pair(meaning_id, concept_class_id))
    return LexicalNode(
        sign_id=sign_id,
        raw_unicode_id=raw_unicode_id,
        skeleton_id=skeleton_id,
        lexeme_id=lexeme_id,
        root_id=root_id,
        pattern_id=pattern_id,
        signified_id=signified_id,
        mutabaqa_id=mutabaqa_id,
        tadammun_id=tadammun_id,
        iltizam_id=iltizam_id,
        meaning_id=meaning_id,
        concept_class_id=concept_class_id,
        transfer_state_id=transfer_state_id,
        metaphor_state_id=metaphor_state_id,
        node_id=node_id,
    )
