from utils_eng import to_lowercase_list

def count_cap_num_helper(strings):
    """统计包含全大写字母内容的字符串数量"""
    count = 0
    for s in strings:
        # 提取所有字母字符
        letters_only = ''.join(c for c in s if c.isalpha())
        # 检查是否有字母且全为大写
        if letters_only and letters_only.isupper():
            count += 1
    return count

def count_low_num_helper(strings):
    """统计包含全小写字母内容的字符串数量"""
    count = 0
    for s in strings:
        # 提取所有字母字符
        letters_only = ''.join(c for c in s if c.isalpha())
        # 检查是否有字母且全为小写
        if letters_only and letters_only.islower():
            count += 1
    return count


def count_cap_num(num, strings):
    # print("here: ", num)
    cap_num = count_cap_num_helper(strings)
    if num != cap_num:
        return 0, f"❌ Caps Num: {cap_num}; Required Caps Num: {num}"
    else:
        return 1, "✅ Caps Num Match"


def count_low_num(num, strings):
    # print("here: ", num)
    cap_num = count_low_num_helper(strings)
    if num != cap_num:
        return 0, f"❌ Lowers Num: {cap_num}, Required Lowers Num: {num}"
    else:
        return 1, "✅ Lowers Num Match"
    
def compound_word_num(range, strings):
    def is_compound_word(word):
        return '-' in word or "'" in word
    for item in strings:
        cnt = 0
        compound_words = []
        words = item.split()
        for word in words:
            if is_compound_word(word): 
                cnt += 1
                compound_words.append(word)
        if not range[0] <= cnt <= range[1]:
            return 0, f"❌ Count mismatch, number of compound words generated: {str(cnt)}, detected compound words: {compound_words}"

    return 1, f"✅ Count matches, number of compound words generated: {str(cnt)}, detected compound words: {compound_words}"

def no_character_repeat(strings):
    strings = to_lowercase_list(strings)
    for string in strings:
        char_count = {}
        for char in string:
            if char in char_count:
                return 0, f"❌ Character '{char}' appears repeatedly in {string}"
            char_count[char] = 1
    
    return 1, "✅ No repeated characters in all strings"

def character_freq(letter, range, strings):
    strings = to_lowercase_list(strings)
    cnt = 0
    for string in strings:
        for char in string:
            if char == letter:
                cnt += 1
    if range[0] <= cnt <= range[1]:
        return 1, f"✅，Letter ‘{letter}’ appears {cnt} times."
    else:
        return 0, f"❌，Letter ‘{letter}’ appears {cnt} times."