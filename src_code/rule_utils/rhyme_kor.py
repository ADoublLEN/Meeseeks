import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import Counter
from utils import clean_up_text

try:
    import hgtk
    hgtk_AVAILABLE = True
except ImportError:
    hgtk_AVAILABLE = False
    print("hgtk library not installed, installing automatically...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "hgtk"])
        print("hgtk library installed successfully, importing...")
        import hgtk
        hgtk_AVAILABLE = True
        print("✅ hgtk library imported successfully")
    except Exception as e:
        print(f"❌ Automatic installation failed: {e}")
        print("Please run manually: pip install hgtk")
        hgtk_AVAILABLE = False

import hgtk  # Korean toolkit for Korean text processing


def extract_korean_rhyme(words):
    """Extract Korean word's rhyme (based on vowel and final consonant of last syllable)"""
    rhyme_elements = []
    
    for word in words:
        if word:  # Ensure not empty string
            # Get last character
            last_char = word[-1]
            
            # Check if it's Korean character
            if hgtk.checker.is_hangul(last_char):
                try:
                    # Decompose Korean character into initial, medial, final consonants
                    decomposed = hgtk.letter.decompose(last_char)
                    
                    # Extract medial (vowel) and final (consonant) as rhyme
                    vowel = decomposed[1] if len(decomposed) > 1 else ''
                    final = decomposed[2] if len(decomposed) > 2 else ''
                    
                    # Combine vowel and final consonant as rhyme feature
                    rhyme = vowel + final
                    rhyme_elements.append(rhyme)
                except:
                    # If decomposition fails, skip this character
                    continue
    
    return rhyme_elements


def calculate_rhyme_proportion(rhyme_vowels):
    # Count occurrences of each rhyme
    rhyme_count = Counter(rhyme_vowels)
    total_rhymes = sum(rhyme_count.values())
    
    # Calculate proportion of each rhyme
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    return rhyme_proportion


def kor_yayun(text):
    """Korean rhyme detection function"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    rhyme_elements = extract_korean_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ No Korean characters detected or unable to extract rhymes"
    
    rhyme_proportion = calculate_rhyme_proportion(rhyme_elements)
    
    if max(rhyme_proportion.values()) > 0.5:
        return 1, f"✅ Match, rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ Not match, rhyme proportion details: {str(rhyme_proportion)}, none of the rhyme proportions exceed 50%, rhyme proportion over 50% considered as rhyming"


def extract_korean_even_rhyme(text):
    """Extract Korean even sentence's rhyme"""
    rhyme_elements = []
    
    # Traverse even sentences
    for i in range(1, len(text), 2):  # From second sentence, step size of 2
        word = text[i]
        if word:  # Ensure not empty string
            # Get last character
            last_char = word[-1]
            
            # Check if it's Korean character
            if hgtk.checker.is_hangul(last_char):
                try:
                    # Decompose Korean character into initial, medial, final consonants
                    decomposed = hgtk.letter.decompose(last_char)
                    
                    # Extract medial (vowel) and final (consonant) as rhyme
                    vowel = decomposed[1] if len(decomposed) > 1 else ''
                    final = decomposed[2] if len(decomposed) > 2 else ''
                    
                    # Combine vowel and final consonant as rhyme feature
                    rhyme = vowel + final
                    rhyme_elements.append(rhyme)
                except:
                    # If decomposition fails, skip this character
                    continue
    
    return rhyme_elements


def kor_sijo_yayun(text):
    """Korean sijo rhyme detection (even sentence rhymes)"""
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    # Extract even sentence's rhyme
    rhyme_elements = extract_korean_even_rhyme(text)
    
    if not rhyme_elements:
        return 0, "❌ No Korean characters detected or unable to extract rhymes"
    
    # Judge even sentence's rhyme is consistent
    if len(set(rhyme_elements)) == 1:  # If set length is 1, meaning rhymes are consistent
        return 1, f"✅ Even sentence rhymes are consistent, even sentence rhymes: {rhyme_elements}"
    else:
        return 0, f"❌ Even sentence rhymes are inconsistent, even sentence rhymes: {rhyme_elements}"


def kor_jielong(text_list):
    """Korean rhyme chain (like idiom chain)"""
    for i in range(len(text_list)):
        text_list[i] = clean_up_text(text_list[i])
    
    for i in range(len(text_list) - 1):
        last_char = text_list[i][-1]
        next_first_char = text_list[i + 1][0]
        if last_char != next_first_char:
            return 0, f"❌ Not match, sentence: {str(text_list[i])}'s last character and sentence: {str(text_list[i + 1])}'s first character are not the same"
    return 1, f"✅ Match, sentence: {str(text_list)}"
    
    
if __name__ == "__main__":
    # Test case 1: Basic rhyme - same vowel ending
    print("=== Test case 1: Basic rhyme ===")
    test1 = ["사랑", "희망", "꿈", "행복"]  # All ends with same vowel
    result1, msg1 = kor_yayun(test1)
    print(f"Test 1 result: {result1}, message: {msg1}")
    
    # Test case 2: Not rhyme - different vowel ending
    print("\n=== Test case 2: Not rhyme ===")
    test2 = ["봄", "여름", "가을", "겨울"]  # Different vowel ending
    result2, msg2 = kor_yayun(test2)
    print(f"Test 2 result: {result2}, message: {msg2}")
    
    # Test case 3: Sijo rhyme - even sentence rhymes
    print("\n=== Test case 3: Sijo even sentence rhymes ===")
    test3 = ["봄이 오면", "꽃이 핀다", "새가 울고", "바람 분다"]  # Even sentence rhymes
    result3, msg3 = kor_sijo_yayun(test3)
    print(f"Test 3 result: {result3}, message: {msg3}")
    
    # Test case 4: Sijo not rhyme - even sentence not rhymes
    print("\n=== Test case 4: Sijo even sentence not rhymes ===")
    test4 = ["하늘은 푸르고", "바다는 깊고", "산은 높고", "강은 길다"]  # Even sentence not rhymes
    result4, msg4 = kor_sijo_yayun(test4)
    print(f"Test 4 result: {result4}, message: {msg4}")
    
    # Test case 5: Rhyme chain
    print("\n=== Test case 5: Rhyme chain ===")
    test5 = ["사랑", "랑만", "만족", "족보"]  # Rhyme chain
    result5, msg5 = kor_jielong(test5)
    print(f"Test 5 result: {result5}, message: {msg5}")
    
    print("\n=== Korean rhyme test complete ===")
