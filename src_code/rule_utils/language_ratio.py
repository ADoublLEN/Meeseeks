import re

def calculate_chinese_english_word_ratio(text):
    """Calculate Chinese character count and English word count"""
    # Count Chinese characters
    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')

    # Count English words
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_word_count = len(english_words)

    return chinese_count, english_word_count

def chinese_english_ratio(ratio, model_responses):
    """Check if Chinese-English ratio meets requirements"""
    for model_response in model_responses:
        chinese_count, english_word_count = calculate_chinese_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else chinese_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ Mismatch: Chinese characters: {str(chinese_count)}, English words: {str(english_word_count)}, ratio: {real_ratio}, expected ratio: {str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ Match"

def count_mixed_chinese_english_words(range, model_responses):
    """Count if Chinese-English mixed vocabulary is within specified range"""
    for model_response in model_responses:
        chinese_count, english_word_count = calculate_chinese_english_word_ratio(model_response)
        if not range[0] <= chinese_count + english_word_count <= range[1]:
            return 0, f"❌ Count does not match range {range}: Chinese characters in model response: {str(chinese_count)}, English words: {str(english_word_count)}, total count: {str(chinese_count + english_word_count)}"
    return 1, f"✅ Count matches: Chinese characters in model response: {str(chinese_count)}, English words: {str(english_word_count)}, total count: {str(chinese_count + english_word_count)}"


def calculate_korean_english_word_ratio(text):
    """Calculate Korean character count and English word count"""
    # Count Korean characters
    korean_count = sum(1 for char in text if '\uac00' <= char <= '\ud7af')

    # Count English words
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_word_count = len(english_words)

    return korean_count, english_word_count

def korean_english_ratio(ratio, model_responses):
    """Check if Korean-English ratio meets requirements"""
    for model_response in model_responses:
        korean_count, english_word_count = calculate_korean_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else korean_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ Mismatch: Korean characters: {str(korean_count)}, English words: {str(english_word_count)}, ratio: {real_ratio}, expected ratio: {str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ Match"

def count_mixed_korean_english_words(range, model_responses):
    """Count if Korean-English mixed vocabulary is within specified range"""
    for model_response in model_responses:
        korean_count, english_word_count = calculate_korean_english_word_ratio(model_response)
        if not range[0] <= korean_count + english_word_count <= range[1]:
            return 0, f"❌ Count does not match range {range}: Korean characters in model response: {str(korean_count)}, English words: {str(english_word_count)}, total count: {str(korean_count + english_word_count)}"
    return 1, f"✅ Count matches: Korean characters in model response: {str(korean_count)}, English words: {str(english_word_count)}, total count: {str(korean_count + english_word_count)}"

def calculate_japanese_english_word_ratio(text):
    """Calculate Japanese character count and English word count"""
    # Count Japanese characters (including hiragana, katakana, and kanji)
    japanese_count = sum(1 for char in text if
                        ('\u3040' <= char <= '\u309f') or  # Hiragana
                        ('\u30a0' <= char <= '\u30ff') or  # Katakana
                        ('\u4e00' <= char <= '\u9fff'))    # Kanji (CJK Unified Ideographs)

    # Count English words
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_word_count = len(english_words)

    return japanese_count, english_word_count

def japanese_english_ratio(ratio, model_responses):
    """Check if Japanese-English ratio meets requirements"""
    for model_response in model_responses:
        japanese_count, english_word_count = calculate_japanese_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else japanese_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ Mismatch: Japanese characters: {str(japanese_count)}, English words: {str(english_word_count)}, ratio: {real_ratio}, expected ratio: {str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ Match"

def count_mixed_japanese_english_words(range, model_responses):
    """Count if Japanese-English mixed vocabulary is within specified range"""
    for model_response in model_responses:
        japanese_count, english_word_count = calculate_japanese_english_word_ratio(model_response)
        if not range[0] <= japanese_count + english_word_count <= range[1]:
            return 0, f"❌ Count does not match range {range}: Japanese characters in model response: {str(japanese_count)}, English words: {str(english_word_count)}, total count: {str(japanese_count + english_word_count)}"
    return 1, f"✅ Count matches: Japanese characters in model response: {str(japanese_count)}, English words: {str(english_word_count)}, total count: {str(japanese_count + english_word_count)}"
