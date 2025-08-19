# Special patterns module - integrates idiom chains and special language features

# Import special pattern functions from original files
from .special_chn import model_jielong, model_jielong2, model_jielong3, model_jielong4, word_structure
from .special_jp import jpn_mixed_ratio, has_small_kana, has_furigana_pattern, has_kanji_okurigana_pattern
from .special_kor import has_double_consonants, has_korean_abbreviation, each_has_double_consonants

# Re-export all special pattern related functions for unified management
__all__ = [
    # Chinese special patterns
    'model_jielong',        # Idiom chain 1
    'model_jielong2',       # Idiom chain 2 (number prefix)
    'model_jielong3',       # Idiom chain 3 (reverse chain)
    'model_jielong4',       # Idiom chain 4 (positional character)
    'word_structure',       # Word structure pattern

    # Japanese special patterns
    'jpn_mixed_ratio',              # Japanese mixed ratio
    'has_small_kana',               # Small kana check
    'has_furigana_pattern',         # Furigana pattern
    'has_kanji_okurigana_pattern',  # Kanji okurigana pattern

    # Korean special patterns
    'has_double_consonants',        # Double consonant check
    'has_korean_abbreviation',      # Korean abbreviation
    'each_has_double_consonants'    # Each has double consonants
]
