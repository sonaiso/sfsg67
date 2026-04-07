"""Linguistics sub-package — bridges core tokenizer with morphology.

Provides :func:`analyze_word`, :class:`WordAnalysis`, :class:`LayerResult`,
and the :class:`RootExtractor` protocol for pluggable root extraction.
"""

from .analyze import (
    LexiconRootExtractor,
    RootExtractor,
    WordAnalysis,
    analyze_word,
)
from .layer_result import LayerResult

__all__ = [
    "LayerResult",
    "LexiconRootExtractor",
    "RootExtractor",
    "WordAnalysis",
    "analyze_word",
]
