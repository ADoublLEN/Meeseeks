from utils import clean_up_text
import re

# 1
import re

def has_double_consonants(texts, times):
    """Check if contains exactly specified number of Korean double consonants (된소리)"""
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # Korean characters containing double consonants (ㄲ, ㄸ, ㅃ, ㅆ, ㅉ)
    double_consonant_chars = ['ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ']
    
    # Complete syllable ranges containing double consonants
    double_consonant_pattern = r'[까-낗따-띻빠-삫싸-앃짜-찧]'
    
    total_count = 0
    found_consonants = []
    
    # Count double consonants in each text
    for text in cleaned_up_texts:
        text_consonants = []
        
        # Check double consonant characters
        for char in double_consonant_chars:
            count = text.count(char)
            if count > 0:
                text_consonants.extend([char] * count)
                total_count += count
        
        # Check complete syllables containing double consonants
        matches = re.findall(double_consonant_pattern, text)
        if matches:
            text_consonants.extend(matches)
            total_count += len(matches)
        
        if text_consonants:
            found_consonants.append(text_consonants)
        else:
            found_consonants.append([])
    
    # Format double consonant list display
    consonant_display = []
    for i, consonants in enumerate(found_consonants):
        if consonants:
            consonant_display.append(f"Text {i+1}: {', '.join(consonants)}")
        else:
            consonant_display.append(f"Text {i+1}: None")
    
    consonant_info = " | ".join(consonant_display)
    
    # Check if exactly equals specified times
    if total_count == times:
        return 1, f"✅ ({consonant_info}) perfectly matches the expected count of {times}"
    else:
        return 0, f"❌ ({consonant_info}) does NOT match the expected count of {times} (found {total_count})"
    
def each_has_double_consonants(texts, times):
    """Check if each text contains exactly specified number of Korean double consonants (된소리)"""
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # Korean characters containing double consonants (ㄲ, ㄸ, ㅃ, ㅆ, ㅉ)
    double_consonant_chars = ['ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ']
    
    # Complete syllable ranges containing double consonants
    double_consonant_pattern = r'[까-낗따-띻빠-삫싸-앃짜-찧]'
    
    text_results = []
    all_match = True
    
    # Check double consonants in each text
    for i, text in enumerate(cleaned_up_texts):
        text_consonants = []
        text_count = 0
        
        # Check double consonant characters
        for char in double_consonant_chars:
            count = text.count(char)
            if count > 0:
                text_consonants.extend([char] * count)
                text_count += count
        
        # Check complete syllables containing double consonants
        matches = re.findall(double_consonant_pattern, text)
        if matches:
            text_consonants.extend(matches)
            text_count += len(matches)
        
        # Check if current text matches
        text_matches = text_count == times
        if not text_matches:
            all_match = False
        
        # Format current text result
        consonant_str = ', '.join(text_consonants) if text_consonants else 'None'
        status = "✅" if text_matches else "❌"
        text_results.append(f"Text {i+1}: {status} ({consonant_str}) - found {text_count}")
    
    # Generate final result information
    result_info = " | ".join(text_results)
    
    if all_match:
        return 1, f"✅ All texts match the expected count of {times}: {result_info}"
    else:
        return 0, f"❌ Not all texts match the expected count of {times}: {result_info}"

def has_korean_abbreviation(texts, abbreviation):
    """Check if each text conforms to specified Korean abbreviation pattern"""
    
    cleaned_up_texts = [clean_up_text(text) for text in texts]
    
    # Convert abbreviation to regex pattern
    # e.g. "ㅇㅂ" -> each character corresponds to initial consonant of Korean syllable
    consonant_map = {
        'ㄱ': '[가-깋]', 'ㄴ': '[나-닣]', 'ㄷ': '[다-딯]', 'ㄹ': '[라-맇]',
        'ㅁ': '[마-밓]', 'ㅂ': '[바-빟]', 'ㅅ': '[사-싷]', 'ㅇ': '[아-잏]',
        'ㅈ': '[자-짛]', 'ㅊ': '[차-칳]', 'ㅋ': '[카-킿]', 'ㅌ': '[타-팋]',
        'ㅍ': '[파-핗]', 'ㅎ': '[하-힣]',
        # Double consonants
        'ㄲ': '[까-낗]', 'ㄸ': '[따-띻]', 'ㅃ': '[빠-삫]', 'ㅆ': '[싸-앃]', 'ㅉ': '[짜-찧]'
    }
    
    # Build regex pattern
    pattern_parts = []
    for char in abbreviation:
        if char in consonant_map:
            pattern_parts.append(consonant_map[char])
        else:
            return 0, f"❌ Invalid Korean consonant: {char}"
    
    # Create complete regex pattern
    full_pattern = ''.join(pattern_parts)
    
    results = []
    all_match = True
    
    # Check each text
    for i, text in enumerate(cleaned_up_texts):
        if re.fullmatch(full_pattern, text):
            results.append(f"Text {i+1}: '{text}' ✅")
        else:
            results.append(f"Text {i+1}: '{text}' ❌")
            all_match = False
    
    result_info = " | ".join(results)
    
    if all_match:
        return 1, f"✅ ({result_info}) All texts conform to abbreviation '{abbreviation}'"
    else:
        return 0, f"❌ ({result_info}) Not all texts conform to abbreviation '{abbreviation}'"
