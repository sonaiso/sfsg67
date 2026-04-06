from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair
from .grapheme_atoms import consonantal_skeleton_id
from .lexical_containers import LexicalType
from .relation_frame import RoleTag, relation_frame
from .semantic_envelope import FeatureTag, semantic_envelope
from .unicode_identity import unicode_surface


@dataclass(frozen=True, slots=True)
class WordIdentity:
    """Unified fractal identity of a single Arabic word form.

    Computed as 𝕃++(w) = π(U, π(Q, π(S, π(Λ, π(Ξ, π(Ω, π(Θ, Γ))))))) where::

        U  — raw Unicode surface (no code point discarded)
        Q  — structural shell  (skeleton + lexical type + independence grade)
        S  — central semantic carrier (jamid / root / masdar / operator …)
        Λ  — morph family identity (SIMPLE_NOUN, FIVE_VERBS, DUAL, …)
        Ξ  — constraint envelope (diptote, tanween, definiteness, …)
        Ω  — relational container (pronoun / demonstrative / relative / copular)
        Θ  — morpho-semantic feature envelope
        Γ  — relational argument frame

    Layers Λ, Ξ, Ω default to 0 (absent) so existing two-call sites remain
    valid without change.  All intermediate IDs are stored for inspection.
    The ``identity`` field is the single canonical integer for this word form.
    """

    word: str
    surface_id: int     # U(w)
    skeleton_id: int    # C(w)
    lexical_type: LexicalType
    independence: int   # Independence or IndependenceGrade (both are int)
    carrier_id: int     # S(w)
    family_id: int      # Λ(w)
    constraint_id: int  # Ξ(w)
    relational_id: int  # Ω(w)
    envelope_id: int    # Θ(w)
    frame_id: int       # Γ(w)
    identity: int       # 𝕃++(w)


def compute_word_identity(
    word: str,
    lexical_type: LexicalType,
    independence: int,
    carrier_id: int,
    family: int = 0,
    constraints: int = 0,
    relational: int = 0,
    features: dict[FeatureTag, int] | None = None,
    roles: dict[RoleTag, int] | None = None,
) -> WordIdentity:
    """Compute 𝕃++(w) = π(U, π(Q, π(S, π(Λ, π(Ξ, π(Ω, π(Θ, Γ))))))).

    Args:
        word:         source text of the word form
        lexical_type: LexicalType carrier class
        independence: Independence or IndependenceGrade value
        carrier_id:   pre-computed base semantic carrier S(w)
        family:       morph_family_id Λ(w) — defaults to 0 (unspecified)
        constraints:  constraint_envelope Ξ(w) — defaults to 0 (none)
        relational:   relational_container Ω(w) — defaults to 0 (not relational)
        features:     semantic feature dict for envelope Θ
        roles:        argument role dict for frame Γ
    """
    u = unicode_surface(word)
    c = consonantal_skeleton_id(word)
    q = cantor_pair(cantor_pair(c, int(lexical_type)), independence)
    theta = semantic_envelope(features or {})
    gamma = relation_frame(roles or {})
    identity = cantor_pair(
        u,
        cantor_pair(
            q,
            cantor_pair(
                carrier_id,
                cantor_pair(
                    family,
                    cantor_pair(constraints, cantor_pair(relational, cantor_pair(theta, gamma))),
                ),
            ),
        ),
    )
    return WordIdentity(
        word=word,
        surface_id=u,
        skeleton_id=c,
        lexical_type=lexical_type,
        independence=independence,
        carrier_id=carrier_id,
        family_id=family,
        constraint_id=constraints,
        relational_id=relational,
        envelope_id=theta,
        frame_id=gamma,
        identity=identity,
    )
