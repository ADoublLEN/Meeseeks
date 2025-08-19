# Rule Utils Package - Rule utilities package
# Refactored modular structure, organized by functionality

# Text analysis module
from .text_analysis import (
    model_each_length,
    model_total_length,
    model_item_count,
    model_repeat_each,
    model_no_word_repeat,
    model_non_very_similar
)

# Keyword matching module
from .keyword_matching import (
    model_keywords,
    model_non_keywords,
    model_keywords_any,
    model_word_freq,
    model_non_word_freq,
    model_word_freq_any,
    model_non_word_freq_any
)

# Text formatting module
from .text_formatting import (
    model_no_end_with_punctuation,
    model_endswith_each,
    endswithany_each,
    model_startswith_each,
    model_non_regex,
    model_regex
)

# Language ratio analysis module
from .language_ratio import (
    chinese_english_ratio,
    count_mixed_chinese_english_words,
    korean_english_ratio,
    count_mixed_korean_english_words,
    japanese_english_ratio,
    count_mixed_japanese_english_words
)

# Rhyme analysis module
from .rhyme_analysis import (
    yayun,
    pingze,
    lvshi_yayun,
    fanti,
    has_heteronym,
    jpn_yayun,
    kor_yayun
)

# Special patterns module
from .special_patterns import (
    model_jielong,
    model_jielong2,
    model_jielong3,
    model_jielong4,
    word_structure,
    jpn_mixed_ratio,
    has_small_kana,
    has_furigana_pattern,
    has_kanji_okurigana_pattern,
    has_double_consonants,
    has_korean_abbreviation,
    each_has_double_consonants
)

# Schema validation module
from .schema_validation import model_schema

__all__ = [
    # Text analysis
    'model_each_length', 'model_total_length', 'model_item_count',
    'model_repeat_each', 'model_no_word_repeat', 'model_non_very_similar',

    # Keyword matching
    'model_keywords', 'model_non_keywords', 'model_keywords_any',
    'model_word_freq', 'model_non_word_freq', 'model_word_freq_any', 'model_non_word_freq_any',

    # Text formatting
    'model_no_end_with_punctuation', 'model_endswith_each', 'endswithany_each',
    'model_startswith_each', 'model_non_regex', 'model_regex',

    # Language ratio
    'chinese_english_ratio', 'count_mixed_chinese_english_words',
    'korean_english_ratio', 'count_mixed_korean_english_words',
    'japanese_english_ratio', 'count_mixed_japanese_english_words',

    # Rhyme analysis
    'yayun', 'pingze', 'lvshi_yayun', 'fanti', 'has_heteronym',
    'jpn_yayun', 'kor_yayun',

    # Special patterns
    'model_jielong', 'model_jielong2', 'model_jielong3', 'model_jielong4', 'word_structure',
    'jpn_mixed_ratio', 'has_small_kana', 'has_furigana_pattern', 'has_kanji_okurigana_pattern',
    'has_double_consonants', 'has_korean_abbreviation', 'each_has_double_consonants',

    # Schema validation
    'model_schema'
]
