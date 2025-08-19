import os
import sys
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from collections import Counter

from utils import clean_up_text

try:
    import pypinyin
    pypinyin_AVAILABLE = True
except ImportError:
    pypinyin_AVAILABLE = False
    print("pypinyin library not installed, installing automatically...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypinyin"])
        print("pypinyin library installed successfully, importing...")
        import pypinyin
        pypinyin_AVAILABLE = True
        print("✅ pypinyin library imported successfully")
    except Exception as e:
        print(f"❌ Automatic installation failed: {e}")
        print("Please run manually: pip install pypinyin")
        pypinyin_AVAILABLE = False

from pypinyin import pinyin, Style

try:
    import opencc
    opencc_AVAILABLE = True
except ImportError:
    opencc_AVAILABLE = False
    print("opencc library not installed, installing automatically...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencc"])
        print("opencc library installed successfully, importing...")
        import opencc
        opencc_AVAILABLE = True
        print("✅ opencc library imported successfully")
    except Exception as e:
        print(f"❌ Automatic installation failed: {e}")
        print("Please run manually: pip install opencc")
        opencc_AVAILABLE = False

from pypinyin import pinyin, Style
from collections import Counter

def clean_up_text(text):
    """Clean text, remove punctuation"""
    return re.sub(r'[^\u4e00-\u9fff]', '', text)

def get_rhyme_groups():
    """Get rhyme group mapping table"""
    rhyme_groups = {
        '一麻': ['a', 'ia', 'ua'],
        '二波': ['o', 'uo'],
        '三歌': ['e'],
        '四皆': ['ie', 'üe', 've'],
        '五支': ['-i'],
        '六儿': ['er'],
        '七齐': ['i'],
        '八微': ['ei', 'ui', 'uei'],
        '九开': ['ai', 'uai'],
        '十姑': ['u'],
        '十一鱼': ['ü', 'v'],
        '十二侯': ['ou', 'iu', 'iou'],
        '十三豪': ['ao', 'iao'],
        '十四寒': ['an', 'ian', 'uan', 'üan', 'van'],
        '十五痕': ['en', 'in', 'un', 'uen', 'ün', 'vn'],
        '十六唐': ['ang', 'iang', 'uang'],
        '十七庚': ['eng', 'ing', 'ueng'],
        '十八东': ['ong', 'iong']
    }
    
    # Create vowel to rhyme group reverse mapping
    vowel_to_group = {}
    for group_name, vowels in rhyme_groups.items():
        for vowel in vowels:
            vowel_to_group[vowel] = group_name
    
    return rhyme_groups, vowel_to_group

def extract_rhyme_vowels_smart(words):
    """Smart extraction of rhyme vowels, considering the best choice of multi-toned words"""
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    rhyme_vowels = []
    rhyme_chars = []
    
    # Collect all possible vowels and corresponding rhyme groups
    all_possible_data = []
    for word in words:
        if word:
            last_char = word[-1]
            rhyme_chars.append(last_char)
            possible_vowels = pinyin(last_char, style=Style.FINALS, heteronym=True)[0]
            # Convert to rhyme group information
            possible_groups = []
            for vowel in possible_vowels:
                group = vowel_to_group.get(vowel, "Unknown rhyme group")
                possible_groups.append((vowel, group))
            all_possible_data.append(possible_groups)
    
    # Try all combinations, find the rhyme group with the highest proportion of rhyme
    best_combination = []
    best_score = 0
    
    def try_combination(index, current_combination):
        nonlocal best_combination, best_score
        
        if index == len(all_possible_data):
            # Count by rhyme group
            groups = [item[1] for item in current_combination]
            group_counter = Counter(groups)
            if group_counter:
                max_count = max(group_counter.values())
                score = max_count / len(current_combination)
                if score > best_score:
                    best_score = score
                    best_combination = current_combination.copy()
            return
        
        # Try each pronunciation of the current word
        for vowel_group_pair in all_possible_data[index]:
            current_combination.append(vowel_group_pair)
            try_combination(index + 1, current_combination)
            current_combination.pop()
    
    try_combination(0, [])
    
    # Extract best combination of rhyme vowels
    rhyme_vowels = [item[0] for item in best_combination]
    
    return rhyme_vowels, rhyme_chars

def yayun(text):
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    
    # Clean text
    cleaned_text = [clean_up_text(line) for line in text]
    
    # Smart extraction of rhyme vowels
    rhyme_vowels, rhyme_chars = extract_rhyme_vowels_smart(cleaned_text)
    
    # Count by rhyme group
    group_data = {}  # {Rhyme group: [(Vowel, Character), ...]}
    
    for i, (vowel, char) in enumerate(zip(rhyme_vowels, rhyme_chars)):
        group = vowel_to_group.get(vowel, "Unknown rhyme group")
        if group not in group_data:
            group_data[group] = []
        group_data[group].append((vowel, char))
    
    # Generate result information
    result_msg = ""
    total_lines = len(rhyme_vowels)
    max_proportion = 0
    
    for group, items in sorted(group_data.items(), key=lambda x: len(x[1]), reverse=True):
        proportion = len(items) / total_lines
        max_proportion = max(max_proportion, proportion)
        
        # Subdivide by vowel
        vowel_groups = {}
        for vowel, char in items:
            if vowel not in vowel_groups:
                vowel_groups[vowel] = []
            vowel_groups[vowel].append(char)
        
        result_msg += f"【{group}】Rhyme proportion: {proportion*100:.1f}%\n"
        for vowel, chars in vowel_groups.items():
            result_msg += f"  {vowel}: {'，'.join(chars)}\n"
    
    # Check if rhyming
    if max_proportion >= 0.5:
        return 1, f"✅ Rhyme matched!\n{result_msg}"
    else:
        return 0, f"❌ Rhyme not matched!\n{result_msg}"

def lvshi_yayun(text):
    rhyme_groups, vowel_to_group = get_rhyme_groups()
    
    # Clean text
    cleaned_text = [clean_up_text(line) for line in text]
    
    # Extract even lines
    even_lines = [cleaned_text[i] for i in range(1, len(cleaned_text), 2)]
    even_chars = [text[i].strip()[-1] if text[i].strip() else "" for i in range(1, len(text), 2)]
    
    if not even_lines:
        return 0, "❌ No even lines"
    
    # Smart extraction of even line rhyme vowels
    rhyme_vowels, _ = extract_rhyme_vowels_smart(even_lines)
    
    # Convert to rhyme groups
    rhyme_groups_list = []
    for vowel in rhyme_vowels:
        group = vowel_to_group.get(vowel, "Unknown rhyme group")
        rhyme_groups_list.append(group)
    
    # Count by rhyme group
    group_counter = Counter(rhyme_groups_list)
    
    # Generate result information
    result_msg = ""
    for group, count in group_counter.most_common():
        proportion = count / len(rhyme_vowels)
        # Find characters and vowels corresponding to this rhyme group
        chars_in_group = []
        vowels_in_group = []
        for i, g in enumerate(rhyme_groups_list):
            if g == group:
                chars_in_group.append(even_chars[i])
                vowels_in_group.append(rhyme_vowels[i])
        
        result_msg += f"【{group}】Rhyme proportion: {proportion*100:.1f}%\n"
        # Subdivide by vowel
        vowel_char_map = {}
        for vowel, char in zip(vowels_in_group, chars_in_group):
            if vowel not in vowel_char_map:
                vowel_char_map[vowel] = []
            vowel_char_map[vowel].append(char)
        
        for vowel, chars in vowel_char_map.items():
            result_msg += f"  {vowel}: {'，'.join(chars)}\n"
    
    # Check if even lines have same rhyme group
    if len(set(rhyme_groups_list)) == 1:
        return 1, f"✅ Even lines have same rhyme group!\n{result_msg}"
    else:
        return 0, f"❌ Even lines have different rhyme groups!\n{result_msg}"

        
def get_tone(pinyin_list):
    tones = []
    for py in pinyin_list:
        if py[-1].isdigit():
            tones.append(int(py[-1]))
        else:
            tones.append(0)  # 轻声
    return tones


def get_pingze(sentence):
    pinyin_result = pinyin(sentence, style=Style.TONE3)
    tones = get_tone([py[0] for py in pinyin_result])
    pingze = []
    for tone in tones:
        if tone in [1, 2]:
            pingze.append('平')
        elif tone in [3, 4]:
            pingze.append('仄')
        else:
            pingze.append('轻')
    return ''.join(pingze)


def pingze(poem_list):
    for i in range(len(poem_list)):
        poem_list[i] = clean_up_text(poem_list[i])
    results = []
    pingzeset = set()
    for sentence in poem_list:
        pingze = get_pingze(sentence)
        pingzeset.add(pingze)
        results.append(f"'{str(sentence)}' tone pattern: {str(pingze)}")
    if len(pingzeset) != 1:
        return 0, f"❌ Tone patterns inconsistent, details: {str(results)}"
    else:
        return 1, f"✅ Tone patterns consistent, details: {str(results)}"


def fanti(texts):
    converter = opencc.OpenCC('s2t.json')
    
    for idx, text in enumerate(texts):
        # Clean text
        cleaned_text = clean_up_text(text)
        
        # Convert to traditional Chinese
        fanti_text = converter.convert(cleaned_text)
        
        # Check if each character is already traditional
        for i in range(len(cleaned_text)):
            if cleaned_text[i] != fanti_text[i]:
                return 0, f"❌ Character '{cleaned_text[i]}' in text {idx+1} is not traditional Chinese"
    
    return 1, "✅ All text content is in traditional Chinese"


def has_heteronym(texts, num):
    texts = [clean_up_text(text) for text in texts]
    
    for text in texts:
        heteronym_count = 0
        heteronym_words = []
        
        for word in text:
            possible_pronunciations = pinyin(word, style=Style.NORMAL, heteronym=True)[0]
            if len(possible_pronunciations) > 1:
                heteronym_count += 1
                heteronym_words.append((word, possible_pronunciations))
        
        if heteronym_count != num:
            # Limit output to maximum 50 heteronyms
            display_words = heteronym_words[:50]
            truncated_msg = f" (showing first 50 of {len(heteronym_words)})" if len(heteronym_words) > 50 else ""
            return 0, f"❌ TEXT: 【{text}】expected {num} heteronym(s), but found {heteronym_count}: {display_words}{truncated_msg}"
    
    return 1, f"✅ All texts have exactly {num} heteronym(s)"


if __name__ == "__main__":
    # Test case 1: poem with multi-toned words
    test_poems1 = [
        "春眠不觉晓，",
        "处处闻啼鸟。",
        "夜来风雨声，",
        "花落知多少。"
    ]
    
    print("=== Test case 1: Spring and Autumn ===")
    result, msg = yayun(test_poems1)
    print(f"Result: {result}")
    print(msg)
    
    # Test case 2: test with "藉" word
    test_poems2 = [
        "借问酒家何处有",
        "牧童遥指杏花村",
        "清明时节雨纷纷",
        "路上行人欲断魂"
    ]
    
    print("\n=== Test case 2: Spring ===")
    result, msg = yayun(test_poems2)
    print(f"Result: {result}")
    print(msg)
    
    # Test case 3: poetry even line rhyme
    test_lvshi = [
        "白日依山尽",
        "黄河入海流",
        "欲穷千里目",
        "更上一层楼"
    ]
    
    print("\n=== Test case 3: The Great Wall (poetry) ===")
    result, msg = lvshi_yayun(test_lvshi)
    print(f"Result: {result}")
    print(msg)
    
    # Test case 4: test with "藉" word
    test_poems3 = [
        "藉此机会表心意",
        "真情实意诉衷肠",
        "借问何时能相见",
        "思君不见下渝州"
    ]
    
    print("\n=== Test case 4: Multi-toned word test ===")
    result, msg = yayun(test_poems3)
    print(f"Result: {result}")
