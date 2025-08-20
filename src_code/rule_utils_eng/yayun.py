import re
from collections import Counter

# 需要安装阿拉伯语处理库
try:
    import pyarabic.araby as araby
    PYARABIC_AVAILABLE = True
except ImportError:
    PYARABIC_AVAILABLE = False
    print("pyarabic库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyarabic"])
        print("pyarabic库安装成功，正在导入...")
        import pyarabic.araby as araby
        PYARABIC_AVAILABLE = True
        print("✅ pyarabic库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install pyarabic")
        PYARABIC_AVAILABLE = False

# 需要安装音节处理库
try:
    import pyphen
    PYPHEN_AVAILABLE = True
except ImportError:
    PYPHEN_AVAILABLE = False
    print("pyphen库未安装，正在自动安装...")
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyphen"])
        print("pyphen库安装成功，正在导入...")
        import pyphen
        PYPHEN_AVAILABLE = True
        print("✅ pyphen库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install pyphen")
        PYPHEN_AVAILABLE = False

# 多语言音节分割器
if PYPHEN_AVAILABLE:
    pt_dic = pyphen.Pyphen(lang='pt_PT')  # 葡萄牙语
    de_dic = pyphen.Pyphen(lang='de_DE')  # 德语
    es_dic = pyphen.Pyphen(lang='es_ES')  # 西班牙语
    fr_dic = pyphen.Pyphen(lang='fr_FR')  # 法语
    id_dic = pyphen.Pyphen(lang='id_ID')  # 印尼语
    ru_dic = pyphen.Pyphen(lang='ru_RU')  # 俄语

def clean_up_text(text):
    """
    清理文本，移除标点符号和非英文字符，只保留英文单词
    """
    # 移除标点符号和非英文字符，只保留字母和空格
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text)
    # 分割成单词并过滤空字符串
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return ' '.join(words)

def normalize_rhyme_keys(rhyme_keys):
    """
    标准化押韵键，合并包含关系的押韵
    例如：'mente' 和 'te' 应该被合并为 'te'
    """
    if not rhyme_keys:
        return []
    
    # 统计每个押韵键出现的次数
    rhyme_count = Counter(rhyme_keys)
    
    # 找出所有的押韵键
    unique_keys = list(set(rhyme_keys))
    
    # 创建一个映射，将较长的押韵键映射到较短的（如果存在包含关系）
    key_mapping = {}
    
    for i, key1 in enumerate(unique_keys):
        for j, key2 in enumerate(unique_keys):
            if i != j:
                # 检查是否存在包含关系
                if key1.endswith(key2):
                    # key1 包含 key2，将 key1 映射到 key2
                    key_mapping[key1] = key2
                elif key2.endswith(key1):
                    # key2 包含 key1，将 key2 映射到 key1
                    key_mapping[key2] = key1
    
    # 应用映射，标准化所有的押韵键
    normalized_keys = []
    for key in rhyme_keys:
        # 找到最短的包含此押韵的键
        current_key = key
        while current_key in key_mapping:
            mapped_key = key_mapping[current_key]
            if len(mapped_key) < len(current_key):
                current_key = mapped_key
            else:
                break
        normalized_keys.append(current_key)
    
    return normalized_keys

def get_rhyme_key_from_last_vowel(word, vowels):
    """
    统一的韵脚提取方法：从最后一个元音到单词尾部
    """
    if not word:
        return None
    
    word = word.lower().strip()
    
    # 找到最后一个元音的位置
    last_vowel_pos = -1
    for i in range(len(word) - 1, -1, -1):
        if word[i] in vowels:
            last_vowel_pos = i
            break
    
    if last_vowel_pos == -1:
        # 没有元音，返回最后2个字符
        return word[-2:] if len(word) >= 2 else word
    
    # 从最后一个元音到单词结尾
    return word[last_vowel_pos:]

def get_rhyme_key(word):
    """
    英文单词的押韵键值提取（使用统一逻辑）
    """
    vowels = 'aeiou'
    return get_rhyme_key_from_last_vowel(word, vowels)

def extract_rhyme_endings(sentences):
    """
    提取每个句子最后一个单词的押韵键值
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1].lower()
                rhyme_key = get_rhyme_key(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def calculate_rhyme_proportion(rhyme_keys):
    """
    计算每个押韵键值的比例
    """
    if not rhyme_keys:
        return {}
    
    rhyme_count = Counter(rhyme_keys)
    total_rhymes = sum(rhyme_count.values())
    
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    return rhyme_proportion

def yayun(text):
    """
    英文押韵检测主函数
    text: 包含多个句子的列表
    返回: (是否押韵, 详细信息)
    """
    # 清理每个句子
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_text(text[i]))
    
    # 提取押韵键值
    rhyme_keys = extract_rhyme_endings(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract rhyme information"
    
    # 计算押韵比例
    rhyme_proportion = calculate_rhyme_proportion(rhyme_keys)
    
    # 判断是否押韵（最高比例是否到达50%）
    if rhyme_proportion and max(rhyme_proportion.values()) > 0.499:
        return 1, f"✅ Match, rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ No match, rhyme proportion details: {str(rhyme_proportion)}, no rhyme pattern reaches 50%, 50% rhyme proportion is considered rhyming"

def model_jielong(chengyu_list):
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])

    for i in range(len(chengyu_list) - 1):
        last_char = chengyu_list[i][-1]
        next_first_char = chengyu_list[i + 1][0]
        if last_char != next_first_char:
            return 0, f"❌ No match, idiom: {str(chengyu_list[i])}'s last character and idiom: {str(chengyu_list[i + 1])}'s first character are inconsistent"
    return 1, f"✅ Match, idioms: {str(chengyu_list)}"

# ========== 阿拉伯语（保持原有逻辑）==========
def clean_up_arabic_text(text):
    """
    清理阿拉伯语文本，移除标点符号和非阿拉伯字符
    """
    try:
        import pyarabic.araby as araby
        # 移除塔什基尔（阿拉伯语音调符号）
        text = araby.strip_tashkeel(text)
        # 移除塔特维尔（延长符）
        text = araby.strip_tatweel(text)
    except ImportError:
        pass
    
    return text

def get_arabic_rhyme_key_improved(word):
    """
    改进的阿拉伯语单词押韵键值提取
    """
    if not word:
        return None
    
    word = word.strip()
    
    # 只保留阿拉伯字母（移除所有标点符号）
    word = re.sub(r'[^\u0621-\u064A\u0671-\u06D3]', '', word)
    
    if not word:
        return None
    
    try:
        import pyarabic.araby as araby
        # 移除音调符号
        word = araby.strip_tashkeel(word)
    except ImportError:
        pass
    
    # 移除定冠词和常见介词
    if word.startswith('بال') and len(word) > 3:
        word = word[3:]  # 移除 "بال"
    elif word.startswith('وال') and len(word) > 3:
        word = word[3:]  # 移除 "وال"  
    elif word.startswith('ال') and len(word) > 2:
        word = word[2:]  # 移除 "ال"
    
    # 特殊处理：ة (ta marbuta) 在押韵中等同于 ت
    if word.endswith('ة'):
        word = word[:-1] + 'ت'
    
    # 取最后两个字母作为押韵键，这对阿拉伯语更准确
    if len(word) >= 2:
        return word[-2:]
    else:
        return word

def extract_arabic_rhyme_endings_improved(sentences):
    """
    改进的阿拉伯语句子押韵键值提取
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1]
                # 只保留阿拉伯字母
                last_word = re.sub(r'[^\u0621-\u064A\u0671-\u06D3]', '', last_word)
                rhyme_key = get_arabic_rhyme_key_improved(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def arabic_yayun(text, threshold=0.5):
    """
    改进的阿拉伯语押韵检测主函数
    text: 包含多个句子的列表
    threshold: 押韵阈值，默认50%
    返回: (是否押韵, 详细信息)
    """
    # 清理每个句子
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_arabic_text(text[i]))
    
    # 提取押韵键值
    rhyme_keys = extract_arabic_rhyme_endings_improved(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract Arabic rhyme information"
    
    # 计算押韵比例
    rhyme_count = Counter(rhyme_keys)
    total_rhymes = sum(rhyme_count.values())
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    
    # 分析押韵模式
    max_proportion = max(rhyme_proportion.values())
    
    # 构建详细的押韵分析
    rhyme_analysis = []
    for rhyme, count in sorted(rhyme_count.items(), key=lambda x: x[1], reverse=True):
        proportion = rhyme_proportion[rhyme]
        rhyme_analysis.append(f"Rhyme '{rhyme}': {count} sentences ({proportion:.1%})")
    
    analysis_text = ", ".join(rhyme_analysis)
    
    # 判断是否押韵
    if max_proportion >= threshold:
        return 1, f"✅ Match, Arabic rhyme analysis: {analysis_text}. Highest proportion {max_proportion:.1%} reaches threshold {threshold:.0%}, considered rhyming"
    else:
        return 0, f"❌ No match, Arabic rhyme analysis: {analysis_text}. Highest proportion {max_proportion:.1%} does not reach threshold {threshold:.0%}, not considered rhyming"

# ========== 葡萄牙语（使用统一逻辑）==========
def clean_up_portuguese_text(text):
    """
    清理葡萄牙语文本，移除标点符号
    """
    # 保留葡萄牙语字母（包括带重音的字母）和空格
    cleaned = re.sub(r'[^a-zA-ZàáâãçéêíóôõúÀÁÂÃÇÉÊÍÓÔÕÚ\s]', '', text)
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return ' '.join(words)

def get_portuguese_rhyme_key(word):
    """
    获取葡萄牙语单词的押韵键值（使用统一逻辑）
    """
    vowels = 'aeiouáéíóúâêôãõ'
    return get_rhyme_key_from_last_vowel(word, vowels)

def extract_portuguese_rhyme_endings(sentences):
    """
    提取每个葡萄牙语句子最后一个单词的押韵键值
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1].lower()
                rhyme_key = get_portuguese_rhyme_key(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def portuguese_yayun(text):
    """
    葡萄牙语押韵检测主函数
    text: 包含多个句子的列表
    返回: (是否押韵, 详细信息)
    """
    # 清理每个句子
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_portuguese_text(text[i]))
    
    # 提取押韵键值
    rhyme_keys = extract_portuguese_rhyme_endings(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract Portuguese rhyme information"
    
    # 计算押韵比例
    rhyme_count = Counter(rhyme_keys)
    total_rhymes = sum(rhyme_count.values())
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    
    # 判断是否押韵（最高比例是否到达50%）
    if rhyme_proportion and max(rhyme_proportion.values()) > 0.499:
        return 1, f"✅ Match, Portuguese rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ No match, Portuguese rhyme proportion details: {str(rhyme_proportion)}, no rhyme pattern reaches 50%, 50% rhyme proportion is considered rhyming"

# ========== 德语（使用统一逻辑）==========
def clean_up_german_text(text):
    """
    清理德语文本，移除标点符号
    """
    # 保留德语字母（包括变音字母）和空格
    cleaned = re.sub(r'[^a-zA-ZäöüßÄÖÜ\s]', '', text)
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return ' '.join(words)

def get_german_rhyme_key(word):
    """
    获取德语单词的押韵键值（使用统一逻辑）
    """
    vowels = 'aeiouäöü'
    return get_rhyme_key_from_last_vowel(word, vowels)

def extract_german_rhyme_endings(sentences):
    """
    提取每个德语句子最后一个单词的押韵键值
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1].lower()
                rhyme_key = get_german_rhyme_key(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def german_yayun(text):
    """
    德语押韵检测主函数
    """
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_german_text(text[i]))
    
    rhyme_keys = extract_german_rhyme_endings(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract German rhyme information"
    
    rhyme_count = Counter(rhyme_keys)
    total_rhymes = sum(rhyme_count.values())
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    
    if rhyme_proportion and max(rhyme_proportion.values()) > 0.499:
        return 1, f"✅ Match, German rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ No match, German rhyme proportion details: {str(rhyme_proportion)}, no rhyme pattern reaches 50%, 50% rhyme proportion is considered rhyming"

# ========== 西班牙语（使用统一逻辑）==========
def clean_up_spanish_text(text):
    """
    清理西班牙语文本，移除标点符号
    """
    # 保留西班牙语字母（包括带重音的字母和ñ）和空格
    cleaned = re.sub(r'[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s]', '', text)
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return ' '.join(words)

def get_spanish_rhyme_key(word):
    """
    获取西班牙语单词的押韵键值（使用统一逻辑）
    """
    vowels = 'aeiouáéíóú'
    return get_rhyme_key_from_last_vowel(word, vowels)

def extract_spanish_rhyme_endings(sentences):
    """
    提取每个西班牙语句子最后一个单词的押韵键值
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1].lower()
                rhyme_key = get_spanish_rhyme_key(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def spanish_yayun(text):
    """
    西班牙语押韵检测主函数
    """
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_spanish_text(text[i]))
    
    rhyme_keys = extract_spanish_rhyme_endings(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract Spanish rhyme information"
    
    rhyme_count = Counter(rhyme_keys)
    total_rhymes = sum(rhyme_count.values())
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    
    if rhyme_proportion and max(rhyme_proportion.values()) > 0.499:
        return 1, f"✅ Match, Spanish rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ No match, Spanish rhyme proportion details: {str(rhyme_proportion)}, no rhyme pattern reaches 50%, 50% rhyme proportion is considered rhyming"

# ========== 法语 ==========
def clean_up_french_text(text):
    """
    清理法语文本，移除标点符号
    """
    # 保留法语字母（包括带重音的字母和ç）和空格
    cleaned = re.sub(r'[^a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ\s]', '', text)
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return ' '.join(words)

def get_french_rhyme_key(word):
    """
    获取法语单词的押韵键值
    法语押韵通常基于词尾的音素
    """
    if not word:
        return None
    
    word = word.lower().strip()
    
    # 使用音节分割来找押韵部分
    if PYPHEN_AVAILABLE:
        try:
            syllables = fr_dic.inserted(word).split('-')
            if syllables:
                return syllables[-1]
        except:
            pass
    
    return extract_simple_french_rhyme(word)

def extract_simple_french_rhyme(word):
    """
    法语押韵模式提取
    """
    word = word.lower()
    
    # 法语元音
    vowels = 'aeiouàâäéèêëïîôöùûüÿ'
    
    # 常见法语押韵后缀
    common_endings = ['tion', 'sion', 'ment', 'able', 'ible', 'ique', 'eur', 'eux', 'euse', 'oir', 'oire']
    
    for ending in common_endings:
        if word.endswith(ending):
            return ending
    
    # 特殊处理法语的静音字母 - e, s, t, x 在词尾通常不发音
    silent_endings = ['e', 's', 't', 'x', 'es', 'ts', 'xs']
    original_word = word
    
    for ending in silent_endings:
        if word.endswith(ending):
            word = word[:-len(ending)]
            break
    
    # 如果去掉静音字母后单词太短，恢复原词
    if len(word) < 2:
        word = original_word
    
    # 找到最后一个元音的位置
    last_vowel_pos = -1
    for i in range(len(word) - 1, -1, -1):
        if word[i] in vowels:
            last_vowel_pos = i
            break
    
    if last_vowel_pos == -1:
        return word[-2:] if len(word) >= 2 else word
    
    # 从最后一个元音开始构建音节
    rhyme_start = last_vowel_pos
    if last_vowel_pos > 0 and word[last_vowel_pos - 1] not in vowels:
        rhyme_start = last_vowel_pos - 1
    
    return word[rhyme_start:]

def extract_french_rhyme_endings(sentences):
    """
    提取每个法语句子最后一个单词的押韵键值
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1].lower()
                rhyme_key = get_french_rhyme_key(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def french_yayun(text):
    """
    法语押韵检测主函数
    """
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_french_text(text[i]))
    
    rhyme_keys = extract_french_rhyme_endings(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract French rhyme information"
    
    normalized_keys = normalize_rhyme_keys(rhyme_keys)
    rhyme_count = Counter(normalized_keys)
    total_rhymes = sum(rhyme_count.values())
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    
    if rhyme_proportion and max(rhyme_proportion.values()) > 0.5:
        return 1, f"✅ Match, French rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ No match, French rhyme proportion details: {str(rhyme_proportion)}, no rhyme pattern exceeds 50%, rhyme proportion over 50% is considered rhyming"
    
# ========== 印尼语（使用统一逻辑）==========
def clean_up_indonesian_text(text):
    """
    清理印尼语文本，移除标点符号
    """
    # 印尼语主要使用基本拉丁字母
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text)
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return ' '.join(words)

def get_indonesian_rhyme_key(word):
    """
    获取印尼语单词的押韵键值（使用统一逻辑）
    """
    vowels = 'aeiou'
    return get_rhyme_key_from_last_vowel(word, vowels)

def extract_indonesian_rhyme_endings(sentences):
    """
    提取每个印尼语句子最后一个单词的押韵键值
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1].lower()
                rhyme_key = get_indonesian_rhyme_key(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def indonesian_yayun(text):
    """
    印尼语押韵检测主函数
    """
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_indonesian_text(text[i]))
    
    rhyme_keys = extract_indonesian_rhyme_endings(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract Indonesian rhyme information"
    
    rhyme_count = Counter(rhyme_keys)
    total_rhymes = sum(rhyme_count.values())
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    
    if rhyme_proportion and max(rhyme_proportion.values()) > 0.499:
        return 1, f"✅ Match, Indonesian rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ No match, Indonesian rhyme proportion details: {str(rhyme_proportion)}, no rhyme pattern reaches 50%, 50% rhyme proportion is considered rhyming"

# ========== 俄语（使用统一逻辑）==========
def clean_up_russian_text(text):
    """
    清理俄语文本，移除标点符号
    """
    # 保留俄语西里尔字母和空格
    cleaned = re.sub(r'[^а-яёА-ЯЁ\s]', '', text)
    words = [word.strip() for word in cleaned.split() if word.strip()]
    return ' '.join(words)

def get_russian_rhyme_key(word):
    """
    获取俄语单词的押韵键值（使用统一逻辑）
    """
    vowels = 'аеёиоуыэюя'
    return get_rhyme_key_from_last_vowel(word, vowels)

def extract_russian_rhyme_endings(sentences):
    """
    提取每个俄语句子最后一个单词的押韵键值
    """
    rhyme_keys = []
    
    for sentence in sentences:
        if sentence:
            words = sentence.split()
            if words:
                last_word = words[-1].lower()
                rhyme_key = get_russian_rhyme_key(last_word)
                if rhyme_key:
                    rhyme_keys.append(rhyme_key)
    
    return rhyme_keys

def russian_yayun(text):
    """
    俄语押韵检测主函数
    """
    cleaned_sentences = []
    for i in range(len(text)):
        cleaned_sentences.append(clean_up_russian_text(text[i]))
    
    rhyme_keys = extract_russian_rhyme_endings(cleaned_sentences)
    
    if not rhyme_keys:
        return 0, "❌ Unable to extract Russian rhyme information"
    
    rhyme_count = Counter(rhyme_keys)
    total_rhymes = sum(rhyme_count.values())
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    
    if rhyme_proportion and max(rhyme_proportion.values()) > 0.499:
        return 1, f"✅ Match, Russian rhyme proportion details: {str(rhyme_proportion)}"
    else:
        return 0, f"❌ No match, Russian rhyme proportion details: {str(rhyme_proportion)}, no rhyme pattern reaches 50%, 50% rhyme proportion is considered rhyming"

# ========== 测试代码 ==========
if __name__ == "__main__":
    print("=== 统一韵脚逻辑的多语言押韵检测测试 ===\n")
    
    # 英语测试
    print("英语测试:")
    english_lines = [
        "The cat sat on the mat",
        "The rat ran down the flat",
        "The bat flew around the hat",
        "The fat man looked at that"
    ]
    print(yayun(english_lines))
    print()
    
    # 德语测试
    print("德语测试:")
    german_lines = [
        "In einem weiten Universum, auf einem einsamen Planeten",
        "Ein alter Roboter wacht, ohne zu vergessen",
        "Sein Schöpfer ist verschwunden, zu fernen Galaxien gereist",
        "Hat ihn allein gelassen, im Schweigen unbeweist"
    ]
    print(german_yayun(german_lines))
    print()
    
    # 西班牙语测试
    print("西班牙语测试:")
    spanish_lines = [
        "En un universo vasto, en un planeta solitario",
        "Un robot anciano vigila, con corazón binario",
        "Su creador se ha ido, a galaxias lejanas",
        "Lo dejó solo, con memorias tan vanas"
    ]
    print(spanish_yayun(spanish_lines))
    print()
    
    # 法语测试
    print("法语测试:")
    french_lines = [
        "Dans un univers immense, sur une planète solitaire",
        "Un vieux robot veille, avec un cœur de fer",
        "Son créateur est parti, vers des galaxies lointaines",
        "L'a laissé seul, avec des souvenirs qui se traînent"
    ]
    print(french_yayun(french_lines))
    print()
    
    # 印尼语测试
    print("印尼语测试:")
    indonesian_lines = [
        "Di alam semesta yang luas, di planet yang sunyi",
        "Robot tua berjaga, dengan hati yang sepi",
        "Penciptanya telah pergi, ke galaksi yang jauh",
        "Meninggalkannya sendiri, dalam kesunyian yang lembut"
    ]
    print(indonesian_yayun(indonesian_lines))
    print()
    
    # 俄语测试
    print("俄语测试:")
    russian_lines = [
        "Во вселенной бескрайней, на планете одинокой",
        "Старый робот стережёт, с душою глубокой",
        "Создатель его ушёл, к далёким галактикам",
        "Оставил одного, с воспоминаниями практикам"
    ]
    print(russian_yayun(russian_lines))
    print()
    
    # 阿拉伯语测试（保持原有逻辑）
    print("阿拉伯语测试:")
    arabic_lines = [
        "في كوكبٍ بعيدٍ، حيث الصمتُ يطولُ",
        "روبوتٌ مسنٌ، وحيدٌ، لا يزولُ",
        "تلقى رسالةً، خالقه قد أفولُ",
        "يغلق الجهاز، ونحيبُهُ يصولُ"
    ]
    print(arabic_yayun(arabic_lines))
    print()
    
    # 葡萄牙语测试
    print("葡萄牙语测试:")
    portuguese_lines = [
        "Num universo vasto, num planeta solitário",
        "Um robô antigo vigia, com coração binário",
        "Seu criador partiu, para galáxias distantes",
        "Deixou-o sozinho, com memórias constantes"
    ]
    print(portuguese_yayun(portuguese_lines))