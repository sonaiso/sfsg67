"""Arabic Engine — executive kernel for Arabic computational semantics.

Pipeline:  Normalize → Signifier → Lexical Closure → Ontology → Dalāla → Judgment → Evaluation

Design principles:
  1. Cognition requires reality + sense + prior knowledge + linkage + judgment.
  2. Words express mental content (not external reality directly) via
     predicative (إسنادية), restrictive (تقييدية), and additive (إضافية) relations.

Consequently the kernel separates:
  signifier  — the linguistic sign (دالّ)
  signified  — the mental concept (مدلول)
  linkage    — the semantic bond (دلالة)
  evaluation — truth / guidance judgment (تقييم)
"""

from .cognition.evaluation import (
    EvalResult,
    GuidanceState,
    Judgment,
    TruthState,
    build_evaluation,
    build_judgment,
)
from .core.enums import (
    DalalType,
    SemanticType,
)
from .core.enums import (
    GuidanceState as GuidanceStateEnum,
)
from .core.enums import (
    TruthState as TruthStateEnum,
)
from .core.types import Concept, DalalLink, Token
from .inference.inference_rules import InferenceEngine, InferenceResult, RuleKind
from .inference.world_model import Fact, WorldModel
from .linkage.dalala import validate_dalala
from .pipeline import run_pipeline
from .signified.ontology import map_to_ontology
from .signifier.phonology import analyze_phonology
from .signifier.root_pattern import extract_root_pattern
from .signifier.unicode_norm import normalize_arabic
from .syntax.syntax import SyntaxNode, SyntaxRole, build_syntax_tree
from .syntax.time_space import TimeAnchor, TimeSpace, build_time_space

__all__ = [
    # core
    "DalalType",
    "GuidanceState",
    "GuidanceStateEnum",
    "SemanticType",
    "TruthState",
    "TruthStateEnum",
    # types
    "Concept",
    "DalalLink",
    "Token",
    # signifier
    "analyze_phonology",
    "extract_root_pattern",
    "normalize_arabic",
    # signified
    "map_to_ontology",
    # linkage
    "validate_dalala",
    # cognition
    "EvalResult",
    "Judgment",
    "build_evaluation",
    "build_judgment",
    # syntax (v2)
    "SyntaxNode",
    "SyntaxRole",
    "build_syntax_tree",
    # time_space (v2)
    "TimeAnchor",
    "TimeSpace",
    "build_time_space",
    # inference (v2)
    "Fact",
    "InferenceEngine",
    "InferenceResult",
    "RuleKind",
    "WorldModel",
    # pipeline
    "run_pipeline",
]
