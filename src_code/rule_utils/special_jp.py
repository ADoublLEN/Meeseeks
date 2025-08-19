from utils import clean_up_text
import re

# 1
def jpn_mixed_ratio(texts, hiragana_ratio=None, katakana_ratio=None, kanji_ratio=None, tolerance=0.1):
    """Check if hiragana, katakana and kanji meet specified ratios"""
    
    # cleaned_up_texts = [clean_up_text(text) for text in texts]
    error_messages = []
    
    # Evaluate each text separately
    for i, text in enumerate(texts):
        if not text:
            continue
            
        hiragana_count = len(re.findall(r'[\u3040-\u309F]', text))
        katakana_count = len(re.findall(r'[\u30A0-\u30FF]', text))
        kanji_count = len(re.findall(r'[\u4E00-\u9FAF]', text))
        
        total_chars = hiragana_count + katakana_count + kanji_count
        
        if total_chars == 0:
            continue
            
        actual_hiragana_ratio = hiragana_count / total_chars
        actual_katakana_ratio = katakana_count / total_chars
        actual_kanji_ratio = kanji_count / total_chars
        
        # Check if specified ratios are within tolerance range
        text_errors = []
        
        if hiragana_ratio is not None:
            if abs(actual_hiragana_ratio - hiragana_ratio) > tolerance:
                text_errors.append(f"Hiragana ratio: actual {actual_hiragana_ratio:.3f}({hiragana_count} chars), expected {hiragana_ratio:.3f}, difference {abs(actual_hiragana_ratio - hiragana_ratio):.3f} > tolerance {tolerance}")
        
        if katakana_ratio is not None:
            if abs(actual_katakana_ratio - katakana_ratio) > tolerance:
                text_errors.append(f"Katakana ratio: actual {actual_katakana_ratio:.3f}({katakana_count} chars), expected {katakana_ratio:.3f}, difference {abs(actual_katakana_ratio - katakana_ratio):.3f} > tolerance {tolerance}")
        
        if kanji_ratio is not None:
            if abs(actual_kanji_ratio - kanji_ratio) > tolerance:
                text_errors.append(f"Kanji ratio: actual {actual_kanji_ratio:.3f}({kanji_count} chars), expected {kanji_ratio:.3f}, difference {abs(actual_kanji_ratio - kanji_ratio):.3f} > tolerance {tolerance}")
        
        if text_errors:
            error_messages.append(f"Text {i+1}(total chars {total_chars}): {'; '.join(text_errors)}")
    
    is_valid = len(error_messages) == 0
    return is_valid, "; ".join(error_messages) if error_messages else "✅ No issues"

def has_small_kana(texts):
    """Check if contains small kana (sokuon, yoon, etc.)"""
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    combined_text = ''.join(cleaned_up_texts)
    
    # Small kana: っ、ゃ、ゅ、ょ、ァ、ィ、ゥ、ェ、ォ、ャ、ュ、ョ、ッ etc.
    small_kana = r'[っゃゅょァィゥェォャュョッ]'
    return bool(re.search(small_kana, combined_text))

def has_kanji_okurigana_pattern(texts, num):
    """Check if each text contains specified number of kanji+okurigana patterns"""
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # Pattern of kanji followed by hiragana
    kanji_hiragana_pattern = r'[\u4E00-\u9FAF][\u3040-\u309F]+'
    
    for text in cleaned_up_texts:
        matches = re.findall(kanji_hiragana_pattern, text)
        if len(matches) < num:
            return 0, f"❌ only detect {len(matches)} kanji+okurigana patterns, they are: {matches}"
    
    return 1, f"✅ Each text include {num} kanji+okurigana pattern"

def has_furigana_pattern(texts, num):
    """Check if each text contains specified number of furigana patterns (kanji followed by kana in parentheses)"""
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # Pattern of kanji+（kana）
    furigana_pattern = r'[\u4E00-\u9FAF]+（[\u3040-\u309F\u30A0-\u30FF]+）'
    
    for text in cleaned_up_texts:
        matches = re.findall(furigana_pattern, text)
        if len(matches) < num:
            return 0, f"❌ only detect {len(matches)} furigana patterns, they are: {matches}"
    
    return 1, f"✅ Each text include {num} furigana pattern"
