"""Syntactic structure layer (V2).

Builds a constituency/dependency tree for Arabic clauses.  Roles encode
the predicative (إسنادية), restrictive (تقييدية), and additive (إضافية)
relations that the problem statement requires.

Each SyntaxNode carries a SyntaxRole and is linked to a Token identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from creative_tokenizer.morphology.fractal_storage import cantor_pair, fractal_fold

__all__ = ["SyntaxNode", "SyntaxRole", "build_syntax_tree"]


class SyntaxRole(IntEnum):
    """Syntactic role of a word in a clause."""

    VERB = 1  # فعل
    SUBJECT = 2  # فاعل
    OBJECT = 3  # مفعول به
    ADJUNCT = 4  # ظرف / حال / تمييز
    PREDICATE = 5  # خبر
    TOPIC = 6  # مبتدأ
    IDAFA_HEAD = 7  # مضاف
    IDAFA_COMP = 8  # مضاف إليه
    ADJECTIVE = 9  # نعت
    CONJUNCTION = 10  # عاطف
    PARTICLE = 11  # حرف


@dataclass(frozen=True, slots=True)
class SyntaxNode:
    """A node in the syntactic tree.

    Attributes
    ----------
    token_id:   identity of the associated Token
    role:       syntactic role
    head_index: index of the head node (-1 for root)
    position:   word position in the clause (0-based)
    node_id:    stable fractal identity
    """

    token_id: int
    role: SyntaxRole
    head_index: int
    position: int
    node_id: int


def _make_syntax_node(
    token_id: int,
    role: SyntaxRole,
    head_index: int,
    position: int,
) -> SyntaxNode:
    nid = fractal_fold([
        cantor_pair(1, token_id),
        cantor_pair(2, int(role)),
        cantor_pair(3, head_index + 1),  # shift to non-negative
        cantor_pair(4, position),
    ])
    return SyntaxNode(
        token_id=token_id,
        role=role,
        head_index=head_index,
        position=position,
        node_id=nid,
    )


_NOMINAL_POS: frozenset[str] = frozenset({"noun", "unknown"})


def _assign_roles(pos_tags: list[str]) -> list[SyntaxRole]:
    """Heuristic role assignment from POS sequence.

    Handles the basic Arabic clause: verb–subject–object.
    """
    roles: list[SyntaxRole] = []
    verb_seen = False
    subject_seen = False
    for pos in pos_tags:
        if pos == "verb" and not verb_seen:
            roles.append(SyntaxRole.VERB)
            verb_seen = True
        elif pos in _NOMINAL_POS and verb_seen and not subject_seen:
            roles.append(SyntaxRole.SUBJECT)
            subject_seen = True
        elif pos in _NOMINAL_POS and verb_seen and subject_seen:
            roles.append(SyntaxRole.OBJECT)
        elif pos in _NOMINAL_POS:
            roles.append(SyntaxRole.TOPIC)
        elif pos == "adj":
            roles.append(SyntaxRole.ADJECTIVE)
        elif pos == "particle":
            roles.append(SyntaxRole.PARTICLE)
        else:
            roles.append(SyntaxRole.ADJUNCT)
    return roles


def build_syntax_tree(
    token_ids: list[int],
    pos_tags: list[str],
) -> tuple[SyntaxNode, ...]:
    """Build a flat dependency-style syntax tree from token IDs and POS tags.

    Returns a tuple of SyntaxNodes with head indices set by heuristic rules.
    """
    if len(token_ids) != len(pos_tags):
        raise ValueError("token_ids and pos_tags must have the same length")

    roles = _assign_roles(pos_tags)

    # Find verb index as head; fallback to first token
    head_idx = -1
    for i, role in enumerate(roles):
        if role == SyntaxRole.VERB:
            head_idx = i
            break
    if head_idx == -1:
        head_idx = 0

    nodes: list[SyntaxNode] = []
    for i, (tid, role) in enumerate(zip(token_ids, roles)):
        h = -1 if i == head_idx else head_idx
        nodes.append(_make_syntax_node(tid, role, h, i))

    return tuple(nodes)
