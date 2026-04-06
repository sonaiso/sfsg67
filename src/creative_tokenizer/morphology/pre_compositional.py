"""Pre-Compositional Fractal Value  ℙ(w).

𝕡(w) = π( 𝕃++(w),
           π( 𝕹(w),
              π( 𝔹(w),
                 π( 𝕶(w),
                    π( ℂ(w),
                       π( 𝔸(w),
                          π( 𝔻(w),
                             𝕁(w) )))))))

This is the top-level value that every word carries before entering
compositional syntax.  Every layer is stored explicitly in the dataclass
for inspection and testing.
"""
from __future__ import annotations

from dataclasses import dataclass

from .fractal_storage import cantor_pair
from .word_identity import WordIdentity


@dataclass(frozen=True, slots=True)
class PreCompositionalValue:
    """Numerically closed pre-compositional node for one Arabic word form.

    Fields (all are stable fractal integers unless noted)::

        word_identity   𝕃++(w)  — result of compute_word_identity()
        base_class_id   𝕹(w)    — ISM / FI'L / HARF
        infl_state_id   𝔹(w)    — MABNI / MU'RAB / MIXED + carrier + mode
        lex_nature_id   𝕶(w)    — JAMID / MUSHTAQ / … etc.
        contract_id     ℂ(w)    — value-slot contract function
        factor_id       𝔸(w)    — factor / governance system
        semantic_id     𝔻(w)    — mutabaqa + tadammun + iltizam
        readiness_id    𝕁(w)    — composition readiness envelope
        value           ℙ(w)    — the single canonical pre-compositional integer
    """

    word_identity:  WordIdentity
    base_class_id:  int  # 𝕹
    infl_state_id:  int  # 𝔹
    lex_nature_id:  int  # 𝕶
    contract_id:    int  # ℂ
    factor_id:      int  # 𝔸
    semantic_id:    int  # 𝔻
    readiness_id:   int  # 𝕁
    value:          int  # ℙ


def compute_pre_compositional(
    word_identity: WordIdentity,
    base_class_id: int,
    infl_state_id: int,
    lex_nature_id: int,
    contract_id: int,
    factor_id: int,
    semantic_id: int,
    readiness_id: int,
) -> PreCompositionalValue:
    """Assemble  ℙ(w) from pre-computed layer ids.

    All layer ids should come from the dedicated compute functions::

        base_class_id  ← base_class.base_class_id()
        infl_state_id  ← inflectional_state.inflectional_state_id()
        lex_nature_id  ← lexical_nature.lexical_nature_id()
        contract_id    ← contract_function.contract_function()
        factor_id      ← factor_system.factor_system()
        semantic_id    ← triple_semantic.triple_semantic_envelope()
        readiness_id   ← readiness.readiness_envelope()
    """
    # ℙ(w) = π(L, π(N, π(B, π(K, π(C, π(A, π(D, J)))))))
    value = cantor_pair(
        word_identity.identity,
        cantor_pair(
            base_class_id,
            cantor_pair(
                infl_state_id,
                cantor_pair(
                    lex_nature_id,
                    cantor_pair(
                        contract_id,
                        cantor_pair(
                            factor_id,
                            cantor_pair(semantic_id, readiness_id),
                        ),
                    ),
                ),
            ),
        ),
    )
    return PreCompositionalValue(
        word_identity=word_identity,
        base_class_id=base_class_id,
        infl_state_id=infl_state_id,
        lex_nature_id=lex_nature_id,
        contract_id=contract_id,
        factor_id=factor_id,
        semantic_id=semantic_id,
        readiness_id=readiness_id,
        value=value,
    )
