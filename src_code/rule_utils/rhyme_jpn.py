import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from collections import Counter

from utils import clean_up_text

import hanziconv
from hanziconv import HanziConv

# Try to import pykakasi library (for Japanese processing)
try:
    import pykakasi
    pykakasi_AVAILABLE = True
except ImportError:
    pykakasi_AVAILABLE = False
    print("pykakasi library not installed, installing automatically...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pykakasi"])
        print("pykakasi library installed successfully, importing...")
        import pykakasi
        pykakasi_AVAILABLE = True
        print("✅ pykakasi library imported successfully")
    except Exception as e:
        print(f"❌ Automatic installation failed: {e}")
        print("Please run manually: pip install pykakasi")
        pykakasi_AVAILABLE = False

# Try to import jaconv library (for kana conversion)
try:
    import jaconv
    jaconv_AVAILABLE = True
except ImportError:
    jaconv_AVAILABLE = False
    print("jaconv library not installed, installing automatically...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jaconv"])
        print("jaconv library installed successfully, importing...")
        import jaconv
        jaconv_AVAILABLE = True
        print("✅ jaconv library imported successfully")
    except Exception as e:
        print(f"❌ Automatic installation failed: {e}")
        print("Please run manually: pip install jaconv")
        jaconv_AVAILABLE = False


def convert_to_hiragana(text):
    """Convert text to hiragana (including kanji conversion)"""
    if not pykakasi_AVAILABLE:
        print("❌ pykakasi library not available, cannot convert kanji")
        return text
    
    # Use pykakasi to convert kanji to hiragana
    kks = pykakasi.kakasi()
    result = kks.convert(text)
    
    # Extract hiragana reading
    hiragana_text = ''.join([item['hira'] for item in result])
    
    # If there's katakana, convert to hiragana
    if jaconv_AVAILABLE:
        hiragana_text = jaconv.kata2hira(hiragana_text)
    
    return hiragana_text


def extract_japanese_rhyme(words):
    """Extract Japanese word's rhyme (based on last syllable's vowel) - improved version supports kanji"""
    rhyme_elements = []
    
    # Japanese vowel mapping
    vowel_map = {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'a', 'き': 'i', 'く': 'u', 'け': 'e', 'こ': 'o',
        'が': 'a', 'ぎ': 'i', 'ぐ': 'u', 'げ': 'e', 'ご': 'o',
        'さ': 'a', 'し': 'i', 'す': 'u', 'せ': 'e', 'そ': 'o',
        'ざ': 'a', 'じ': 'i', 'ず': 'u', 'ぜ': 'e', 'ぞ': 'o',
        'た': 'a', 'ち': 'i', 'つ': 'u', 'て': 'e', 'と': 'o',
        'だ': 'a', 'ぢ': 'i', 'づ': 'u', 'で': 'e', 'ど': 'o',
        'な': 'a', 'に': 'i', 'ぬ': 'u', 'ね': 'e', 'の': 'o',
        'は': 'a', 'ひ': 'i', 'ふ': 'u', 'へ': 'e', 'ほ': 'o',
        'ば': 'a', 'び': 'i', 'ぶ': 'u', 'べ': 'e', 'ぼ': 'o',
        'ぱ': 'a', 'ぴ': 'i', 'ぷ': 'u', 'ぺ': 'e', 'ぽ': 'o',
        'ま': 'a', 'み': 'i', 'む': 'u', 'め': 'e', 'も': 'o',
        'や': 'a', 'ゆ': 'u', 'よ': 'o',
        'ら': 'a', 'り': 'i', 'る': 'u', 'れ': 'e', 'ろ': 'o',
        'わ': 'a', 'を': 'o', 'ん': 'n',
        # Long and special characters
        'ー': '-', 'っ': 'tsu'
    }
    
    for word in words:
        if word:  # Ensure not empty string
            # First convert to hiragana (including kanji)
            hiragana = convert_to_hiragana(word)
            # print(f"原文: {word} -> 平假名: {hiragana}")  # 调试信息
            
            # Get last syllable
            last_chars = []
            if len(hiragana) >= 2 and hiragana[-1] == 'ー':  # Long sound symbol
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 2 and hiragana[-1] in ['ゃ', 'ゅ', 'ょ']:  # Diphthong
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 1 and hiragana[-1] == 'ん':  # Nasalization
                # If ends with ん, take previous syllable
                if len(hiragana) >= 2:
                    last_chars = [hiragana[-2], hiragana[-1]]
                else:
                    last_chars = [hiragana[-1]]
            else:
                last_chars = [hiragana[-1]]
            
            # Extract rhyme vowel
            rhyme = ''
            for char in last_chars:
                if char in vowel_map:
                    rhyme += vowel_map[char]
                else:
                    # If character not in mapping table, try directly use
                    rhyme += char
            
            if rhyme:
                rhyme_elements.append(rhyme)
                # print(f"韵脚: {rhyme}")  # 调试信息
    
    return rhyme_elements


def calculate_rhyme_proportion(rhyme_elements):
    """Calculate rhyme proportion"""
    rhyme_count = Counter(rhyme_elements)
    total_rhymes = sum(rhyme_count.values())
    
    if total_rhymes == 0:
        return {}
    
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    return rhyme_proportion


def jpn_yayun(text):
    """Japanese rhyme detection function - improved version supports kanji"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    rhyme_elements = extract_japanese_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ No Japanese characters detected or unable to extract rhymes"
    
    rhyme_proportion = calculate_rhyme_proportion(rhyme_elements)
    
    if max(rhyme_proportion.values()) > 0.5:
        return 1, f"✅ Match, rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ Not match, rhyme proportion details: {str(rhyme_proportion)}, none of the rhyme proportions exceed 50%, rhyme proportion over 50% considered as rhyming"


def extract_japanese_even_rhyme(text):
    """Extract Japanese even sentence's rhyme (for poetry, haiku, etc.) - improved version supports kanji"""
    rhyme_elements = []
    
    # Japanese vowel mapping
    vowel_map = {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'a', 'き': 'i', 'く': 'u', 'け': 'e', 'こ': 'o',
        'が': 'a', 'ぎ': 'i', 'ぐ': 'u', 'げ': 'e', 'ご': 'o',
        'さ': 'a', 'し': 'i', 'す': 'u', 'せ': 'e', 'そ': 'o',
        'ざ': 'a', 'じ': 'i', 'ず': 'u', 'ぜ': 'e', 'ぞ': 'o',
        'た': 'a', 'ち': 'i', 'つ': 'u', 'て': 'e', 'と': 'o',
        'だ': 'a', 'ぢ': 'i', 'づ': 'u', 'で': 'e', 'ど': 'o',
        'な': 'a', 'に': 'i', 'ぬ': 'u', 'ね': 'e', 'の': 'o',
        'は': 'a', 'ひ': 'i', 'ふ': 'u', 'へ': 'e', 'ほ': 'o',
        'ば': 'a', 'び': 'i', 'ぶ': 'u', 'べ': 'e', 'ぼ': 'o',
        'ぱ': 'a', 'ぴ': 'i', 'ぷ': 'u', 'ぺ': 'e', 'ぽ': 'o',
        'ま': 'a', 'み': 'i', 'む': 'u', 'め': 'e', 'も': 'o',
        'や': 'a', 'ゆ': 'u', 'よ': 'o',
        'ら': 'a', 'り': 'i', 'る': 'u', 'れ': 'e', 'ろ': 'o',
        'わ': 'a', 'を': 'o', 'ん': 'n',
        'ー': '-', 'っ': 'tsu'
    }
    
    # Traverse even sentences
    for i in range(1, len(text), 2):  # From second sentence, step size of 2
        word = text[i]
        if word:  # Ensure not empty string
            # Convert to hiragana (including kanji)
            hiragana = convert_to_hiragana(word)
            
            # Get last syllable
            last_chars = []
            if len(hiragana) >= 2 and hiragana[-1] == 'ー':  # Long sound symbol
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 2 and hiragana[-1] in ['ゃ', 'ゅ', 'ょ']:  # Diphthong
                last_chars = [hiragana[-2], hiragana[-1]]
            elif len(hiragana) >= 1 and hiragana[-1] == 'ん':  # Nasalization
                if len(hiragana) >= 2:
                    last_chars = [hiragana[-2], hiragana[-1]]
                else:
                    last_chars = [hiragana[-1]]
            else:
                last_chars = [hiragana[-1]]
            
            # Extract rhyme vowel
            rhyme = ''
            for char in last_chars:
                if char in vowel_map:
                    rhyme += vowel_map[char]
                else:
                    rhyme += char
            
            if rhyme:
                rhyme_elements.append(rhyme)
    
    return rhyme_elements


def jpn_waka_yayun(text):
    """Japanese poetry rhyme detection (even sentence rhymes) - improved version supports kanji"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    # Extract even sentence's rhyme
    rhyme_elements = extract_japanese_even_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ No Japanese characters detected or unable to extract rhymes"
    
    # Judge even sentence's rhyme is consistent
    if len(set(rhyme_elements)) == 1:  # If set length is 1, meaning rhymes are consistent
        return 1, f"✅ Even sentence rhymes are consistent, even sentence rhymes: {rhyme_elements}"
    else:
        return 0, f"❌ Even sentence rhymes are inconsistent, even sentence rhymes: {rhyme_elements}"


def jpn_shigin_jielong(text_list):
    """Japanese poetry rhyme chain (like idiom chain) - improved version supports kanji"""
    for i in range(len(text_list)):
        text_list[i] = clean_up_text(text_list[i])

    for i in range(len(text_list) - 1):
        # Convert to hiragana after comparison
        current_hiragana = convert_to_hiragana(text_list[i])
        next_hiragana = convert_to_hiragana(text_list[i + 1])
        
        # Convert last character to hiragana
        last_char = current_hiragana[-1]
        next_first_char = next_hiragana[0]
        
        if last_char != next_first_char:
            return 0, f"❌ Not match, sentence: {str(text_list[i])}({current_hiragana})'s last character and sentence: {str(text_list[i + 1])}({next_hiragana})'s first character are not the same"
    return 1, f"✅ Match, sentence: {str(text_list)}"


def jpn_kana_type(text):
    """Detect Japanese type (single kana type - all hiragana or all katakana)"""
    text = clean_up_text(text[0])
    
    has_hiragana = False
    has_katakana = False
    has_kanji = False
    
    for char in text:
        if '\u3040' <= char <= '\u309F':  # Hiragana range
            has_hiragana = True
        elif '\u30A0' <= char <= '\u30FF':  # Katakana range
            has_katakana = True
        elif '\u4E00' <= char <= '\u9FAF':  # Kanji range
            has_kanji = True
    
    if has_hiragana and not has_katakana and not has_kanji:
        return 1, "✅ Content is all hiragana"
    elif has_katakana and not has_hiragana and not has_kanji:
        return 1, "✅ Content is all katakana"
    elif has_kanji and not has_hiragana and not has_katakana:
        return 1, "✅ Content is all kanji"
    else:
        types = []
        if has_hiragana:
            types.append("hiragana")
        if has_katakana:
            types.append("katakana")
        if has_kanji:
            types.append("kanji")
        return 0, f"❌ Content contains mixed text types: {', '.join(types)}"


if __name__ == "__main__":
    # Test case 1: Basic rhyme - same vowel ending
    print("=== Test case 1: Basic rhyme ===")
    test1 = ["さくら", "あした", "ゆめ", "そら"]  # All ends with 'a' vowel
    result1, msg1 = jpn_yayun(test1)
    print(f"Test 1 result: {result1}, message: {msg1}")
    
    # Test case 2: Not rhyme - different vowel ending
    print("\n=== Test case 2: Not rhyme ===")
    test2 = ["はる", "なつ", "あき", "ふゆ"]  # Different vowel ending
    result2, msg2 = jpn_yayun(test2)
    print(f"Test 2 result: {result2}, message: {msg2}")
    
    # Test case 3: Poetry rhyme - even sentence rhymes
    print("\n=== Test case 3: Poetry even sentence rhymes ===")
    test3 = ["春が来て", "花が咲く", "鳥が鳴き", "風が吹く"]  # Even sentence rhymes
    result3, msg3 = jpn_waka_yayun(test3)
    print(f"Test 3 result: {result3}, message: {msg3}")
    
    # Test case 4: Poetry not rhyme - even sentence not rhymes
    print("\n=== Test case 4: Poetry even sentence not rhymes ===")
    test4 = ["空は青い", "海は深い", "山は高い", "川は長い"]  # Even sentence not rhymes
    result4, msg4 = jpn_waka_yayun(test4)
    print(f"Test 4 result: {result4}, message: {msg4}")
    
    # Test case 5: Same vowel rhyme (u segment)
    print("\n=== Test case 5: Same vowel rhyme (u segment) ===")
    test5 = ["つき", "ゆき", "かぜ", "あめ"]  # All ends with 'i' vowel
    result5, msg5 = jpn_yayun(test5)
    print(f"Test 5 result: {result5}, message: {msg5}")
    
    # Test case 6: Poetry rhyme chain
    print("\n=== Test case 6: Poetry rhyme chain ===")
    test6 = ["さくら", "らくだ", "だいこん", "こんにちは"]  # Rhyme chain
    result6, msg6 = jpn_shigin_jielong(test6)
    print(f"Test 6 result: {result6}, message: {msg6}")
    
    # Test case 7: Katakana rhyme
    print("\n=== Test case 7: Katakana rhyme ===")
    test7 = ["コーヒー", "ケーキ", "クッキー", "キャンディー"]  # Long sound rhyme
    result7, msg7 = jpn_yayun(test7)
    print(f"Test 7 result: {result7}, message: {msg7}")
    
    # Test case 8: Kana type detection - hiragana
    print("\n=== Test case 8: Kana type detection (hiragana) ===")
    test8 = ["ひらがなのぶんしょう"]  # All hiragana
    result8, msg8 = jpn_kana_type(test8)
    print(f"Test 8 result: {result8}, message: {msg8}")
    
    # Test case 9: Kana type detection - katakana
    print("\n=== Test case 9: Kana type detection (katakana) ===")
    test9 = ["カタカナノブンショウ"]  # All katakana
    result9, msg9 = jpn_kana_type(test9)
    print(f"Test 9 result: {result9}, message: {msg9}")
    
    # Test case 10: Haiku example
    print("\n=== Test case 10: Haiku example ===")
    test10 = ["古池や", "蛙飛び込む", "水の音"]  # Famous haiku
    result10, msg10 = jpn_yayun(test10)
    print(f"Test 10 result: {result10}, message: {msg10}")
    
    # Add new test case 11: Kanji rhyme test
    print("\n=== Test case 11: Kanji rhyme test ===")
    test11 = ["学校", "友達", "先生", "教室"]  # Kanji ending
    result11, msg11 = jpn_yayun(test11)
    print(f"Test 11 result: {result11}, message: {msg11}")
    
    # Add new test case 12: Mixed text rhyme test
    print("\n=== Test case 12: Mixed text rhyme test ===")
    test12 = ["桜", "さくら", "サクラ", "花見"]  # Mixed text
    result12, msg12 = jpn_yayun(test12)
    print(f"Test 12 result: {result12}, message: {msg12}")
    
    # Add new test case 13: Kanji rhyme chain test
    print("\n=== Test case 13: Kanji rhyme chain test ===")
    test13 = ["学校", "海", "雨", "雪"]  # Kanji rhyme chain
    result13, msg13 = jpn_shigin_jielong(test13)
    print(f"Test 13 result: {result13}, message: {msg13}")
    
    print("\n=== Japanese rhyme test complete ===")
