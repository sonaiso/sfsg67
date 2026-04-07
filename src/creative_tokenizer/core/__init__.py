"""Core sub-package — re-exports of stable tokenizer API.

Usage::

    from creative_tokenizer.core import CreativeTokenizer, Token
    from creative_tokenizer.core import normalize_text, NormalizationProfile
    from creative_tokenizer.core import BpeTokenizer, BpeTrainer, BpeMerges
    from creative_tokenizer.core import CliticRules
"""

from ..bpe_tokenizer import BpeTokenizer
from ..normalization import NormalizationProfile, NormalizedText, normalize_text
from ..pretokenizer import PreToken, pretokenize
from ..tokenizer import CliticRules, CreativeTokenizer, Token
from ..trainer.bpe import BpeMerges, BpeTrainer

__all__ = [
    "BpeMerges",
    "BpeTokenizer",
    "BpeTrainer",
    "CliticRules",
    "CreativeTokenizer",
    "NormalizationProfile",
    "NormalizedText",
    "PreToken",
    "Token",
    "normalize_text",
    "pretokenize",
]
