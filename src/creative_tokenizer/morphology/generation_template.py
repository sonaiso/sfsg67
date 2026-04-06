"""Generation template — structural recipe in the generative store.

Each template encodes the structural parameters that can produce new
examples.  Every generated example records which template produced it
so that any output can be traced back to its generation rule.

  template_id = F(π(1,root_id), π(2,pattern_id), π(3,family_id),
                   π(4,purpose), π(5,concept_class_id), π(6,vc_fold))
  where vc_fold = F(sorted value_constraints) or 0 if unconstrained.

GenerationPurpose labels what kind of example the template produces:
  MORPHOLOGICAL — tests a morphological form or inflection
  SYNTACTIC     — tests a syntactic structure (isnad, idafa …)
  SEMANTIC      — tests a semantic relation (mantuq, mafhum …)
  CONFLICT      — tests a semantic conflict / resolution scenario
  STYLISTIC     — tests a stylistic pattern (khabar / insha)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .fractal_storage import cantor_pair, fractal_fold


class GenerationPurpose(IntEnum):
    MORPHOLOGICAL = 1
    SYNTACTIC = 2
    SEMANTIC = 3
    CONFLICT = 4
    STYLISTIC = 5


@dataclass(frozen=True, slots=True)
class GenerationTemplate:
    template_id: int
    root_id: int
    pattern_id: int
    family_id: int
    value_constraints: tuple[int, ...]  # sorted constraint ids; empty = unconstrained
    concept_class_id: int
    generation_purpose: GenerationPurpose


def make_template(
    root_id: int,
    pattern_id: int,
    family_id: int,
    concept_class_id: int,
    generation_purpose: GenerationPurpose,
    value_constraints: list[int] | None = None,
) -> GenerationTemplate:
    vc: tuple[int, ...] = tuple(sorted(value_constraints)) if value_constraints else ()
    vc_fold = fractal_fold(list(vc)) if vc else 0
    template_id = fractal_fold(
        [
            cantor_pair(1, root_id),
            cantor_pair(2, pattern_id),
            cantor_pair(3, family_id),
            cantor_pair(4, int(generation_purpose)),
            cantor_pair(5, concept_class_id),
            cantor_pair(6, vc_fold),
        ]
    )
    return GenerationTemplate(
        template_id=template_id,
        root_id=root_id,
        pattern_id=pattern_id,
        family_id=family_id,
        value_constraints=vc,
        concept_class_id=concept_class_id,
        generation_purpose=generation_purpose,
    )
