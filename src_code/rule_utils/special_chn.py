import os
import sys
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import clean_up_text


def model_jielong(chengyu_list):
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])

    for i in range(len(chengyu_list) - 1):
        last_char = chengyu_list[i][-1]
        next_first_char = chengyu_list[i + 1][0]
        if last_char != next_first_char:
            return 0, f"❌ Mismatch, idiom: {str(chengyu_list[i])} last character and idiom: {str(chengyu_list[i + 1])} first character are inconsistent"
    return 1, f"✅ Match, idioms: {str(chengyu_list)}"

def model_jielong2(chengyu_list):
    # Clean text
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])
    
    # Number mapping
    number_chars = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    
    # Check if each idiom starts with correct number
    for i in range(len(chengyu_list)):
        if i >= len(number_chars):
            return 0, f"❌ Mismatch, exceeds supported number range (maximum support up to ten)"
        
        expected_number = number_chars[i]
        if not chengyu_list[i].startswith(expected_number):
            return 0, f"❌ Mismatch, idiom: {str(chengyu_list[i])} should start with '{expected_number}'"
    
    return 1, f"✅ Match, idioms: {str(chengyu_list)}"

def model_jielong3(chengyu_list):
    # Clean text
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])
    
    # Check reverse chain rule: next idiom's last character connects to previous idiom's first character
    for i in range(len(chengyu_list) - 1):
        current_first_char = chengyu_list[i][0]  # Current idiom's first character
        next_last_char = chengyu_list[i + 1][-1]  # Next idiom's last character
        
        if current_first_char != next_last_char:
            return 0, f"❌ Mismatch, idiom: {str(chengyu_list[i])} first character and idiom: {str(chengyu_list[i + 1])} last character are inconsistent"
    
    return 1, f"✅ Match, idioms: {str(chengyu_list)}"

def model_jielong4(word_list):
    # Clean text
    for i in range(len(word_list)):
        word_list[i] = clean_up_text(word_list[i])
    
    # Check positional character chain rule
    for i in range(len(word_list) - 1):
        # Calculate which character position current word should take (0-indexed)
        current_pos = i % len(word_list[i])
        # Calculate which character position next word should take
        next_pos = (i + 1) % len(word_list[i + 1])
        
        # Get characters at corresponding positions
        current_char = word_list[i][current_pos]
        next_char = word_list[i + 1][next_pos]
        
        if current_char != next_char:
            return 0, f"❌ Mismatch, word: {str(word_list[i])} character {current_pos + 1} and word: {str(word_list[i + 1])} character {next_pos + 1} are inconsistent"
    
    return 1, f"✅ Match, words: {str(word_list)}"

def word_structure(word_list, structure):
    # Clean word list
    for i in range(len(word_list)):
        word_list[i] = clean_up_text(word_list[i])
    
    # Validate if each word conforms to specified structure
    for i in range(len(word_list)):
        word = word_list[i]
        
        # Check if word length matches structure length
        if len(word) != len(structure):
            return 0, f"❌ Mismatch, word: {word} length does not match structure {structure}"
        
        # Validate character pattern according to structure
        char_map = {}  # Store letter to character mapping
        
        for j, pattern_char in enumerate(structure):
            current_char = word[j]
            
            if pattern_char in char_map:
                # If this pattern character is already mapped, check consistency
                if char_map[pattern_char] != current_char:
                    return 0, f"❌ Mismatch, word: {word} does not conform to {structure} format"
            else:
                # Establish new mapping relationship
                char_map[pattern_char] = current_char
    
    return 1, f"✅ Match, all words conform to {structure} format: {str(word_list)}"
