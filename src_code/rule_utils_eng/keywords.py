import os
import sys
import re

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rule_utils_eng._detect_primary_language import detect_primary_language
from utils_eng import to_lowercase_list

try:
    import simplemma
    simplemma_AVAILABLE = True
except ImportError:
    simplemma_AVAILABLE = False
    print("simplemma库未安装，正在自动安装...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "simplemma"])
        import simplemma 
        simplemma_AVAILABLE = True
        print("✅ simplemma库已成功导入")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行: pip install simplemma")


def tokenize_texts_with_normalization(texts, language=None, return_mapping=False):
    """
    对文本进行分词和标准化处理
    
    参数:
        texts: 文本列表或单个文本
        language: 语言代码，如果为None则自动检测
        return_mapping: 是否返回原始token到标准化token的映射
    
    返回:
        如果return_mapping=False: 返回标准化后的tokens列表
        如果return_mapping=True: 返回 (tokens列表, 映射列表)
    """
    if isinstance(texts, str):
        texts = [texts]
    
    # 自动检测语言
    if language is None:
        combined_text = ' '.join(texts)
        language = detect_primary_language(combined_text)
    
    tokens_list = []
    mappings_list = []
    
    for text in texts:
        # 简单的分词：按空格和标点符号分割
        # 保留原始的分词结果用于映射
        raw_tokens = re.findall(r'\b\w+\b', text.lower())
        
        # 标准化tokens
        normalized_tokens = []
        mapping = {}
        
        for token in raw_tokens:
            # 使用simplemma进行词形还原作为标准化
            normalized = simplemma.lemmatize(token, lang=language)
            normalized_tokens.append(normalized)
            mapping[token] = normalized
        
        tokens_list.append(normalized_tokens)
        mappings_list.append(mapping)
    
    if return_mapping:
        return tokens_list, mappings_list
    return tokens_list


def is_chinese_or_japanese(text):
    """判断文本是否包含中文或日文字符"""
    return bool(re.search(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", text))
 

def is_raw_keyword(keyword):
    """判断关键词是否需要原文本直接匹配（中文 ,日文或包含空白字符）"""
    return is_chinese_or_japanese(keyword) or bool(re.search(r"\s", keyword))


def match_keyword_in_text(keyword, tokens, original_text, language=None):
    """
    检查关键词是否在文本中
    返回: (是否匹配, 匹配类型)
    """
    # 对于中日文或包含空格的关键词，直接在原文中查找
    # if is_raw_keyword(keyword):
    if keyword.lower() in original_text.lower():
        return True, "直接匹配"
    # return False, None
    
    # 标准化关键词
    if language is None:
        language = detect_primary_language(original_text)

    
    normalized_keyword = simplemma.lemmatize(keyword.lower(), lang=language) 
    
    # 检查是否在tokens中
    if normalized_keyword in tokens:
        return True, "标准化匹配"
    
    # 检查词形还原匹配
    for token in set(tokens):  # 使用set避免重复检查
        lemmatized_token = simplemma.lemmatize(token, lang=language) 
        if lemmatized_token == normalized_keyword:
            return True, "词形还原匹配"
    
    return False, None


def count_keyword_occurrences(keyword, tokens, original_text, language=None):
    """计算关键词在文本中出现的次数"""
    
    # 如果是中文日语或者韩语
    if is_cjk_language(keyword):
        # print("HERRRE")
        return original_text.count(keyword)
    else:
        # 删除原文中的中文日语韩语字符
        cleaned_text = remove_cjk_characters(original_text)
        
        if language is None:
            language = detect_primary_language(cleaned_text)
        
        normalized_keyword = simplemma.lemmatize(keyword.lower(), lang=language)
        
        count = 0
        for token in tokens:
            if token == normalized_keyword or simplemma.lemmatize(token, lang=language) == normalized_keyword:
                count += 1
        
        return count

def is_cjk_language(text):
    """判断文本是否包含中文、日语或韩语字符"""
    for char in text:
        # 中文字符范围
        if '\u4e00' <= char <= '\u9fff':
            return True
        # 日语平假名
        if '\u3040' <= char <= '\u309f':
            return True
        # 日语片假名
        if '\u30a0' <= char <= '\u30ff':
            return True
        # 韩语字符范围
        if '\uac00' <= char <= '\ud7af':
            return True
    return False

def remove_cjk_characters(text):
    """删除文本中的中文、日语、韩语字符"""
    result = []
    for char in text:
        # 跳过中文字符
        if '\u4e00' <= char <= '\u9fff':
            continue
        # 跳过日语平假名
        if '\u3040' <= char <= '\u309f':
            continue
        # 跳过日语片假名
        if '\u30a0' <= char <= '\u30ff':
            continue
        # 跳过韩语字符
        if '\uac00' <= char <= '\ud7af':
            continue
        result.append(char)
    return ''.join(result)




def format_keyword_display(keyword, language):
    """格式化关键词显示，包括标准化形式"""
    normalized = simplemma.lemmatize(keyword.lower(), lang=language)
    if normalized != keyword.lower():
        return f"'{keyword}'(标准化: '{normalized}')"
    return f"'{keyword}'"


# ===== 主要的模型函数 =====

def model_non_keywords(keywords, corresponding_parts, question):
    """每个 part 都不应出现任何关键词"""
    kws = to_lowercase_list(keywords)
    language = detect_primary_language(question)
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language)[0]
        part_lower = part.lower()
        
        for kw in kws:
            is_match, match_type = match_keyword_in_text(kw, tokens, part_lower, language)
            if is_match:
                kw_display = format_keyword_display(kw, language)
                return 0, f"❌ '{part}' 内包含关键词: {kw_display}({match_type})"
    
    return 1, f"✅ 所有内容均未出现关键词: {kws} (包括词形变体)"


def model_keywords(keywords, corresponding_parts, question):
    """每个 part 都需出现所有关键词"""
    kws = to_lowercase_list(keywords)
    language = detect_primary_language(question)
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language)[0]
        
        part_lower = part.lower()
        
        for kw in kws:
            is_match, match_type = match_keyword_in_text(kw, tokens, part_lower, language)
            if not is_match:
                kw_display = format_keyword_display(kw, language)
                return 0, f"❌ '{part}' 内缺少关键词: {kw_display}"
    
    return 1, f"✅ 所有内容均出现关键词: {kws} (包括词形变体)"


def model_keywords_any(num_need, keywords, corresponding_parts, question):
    """检查至少出现 num_need 个关键词"""
    kws = to_lowercase_list(keywords)
    language = detect_primary_language(question)
    
    # 合并所有内容
    all_text = ' '.join(corresponding_parts).lower()
    all_tokens = []
    for part in corresponding_parts:
        all_tokens.extend(tokenize_texts_with_normalization(part, language)[0])
    
    matched = []
    for kw in kws:
        is_match, match_type = match_keyword_in_text(kw, all_tokens, all_text, language)
        if is_match:
            kw_display = format_keyword_display(kw, language)
            matched.append(f"{kw_display}({match_type})")
            
            if len(matched) >= num_need:
                return 1, f"✅ 包含至少 {num_need} 个关键词: {matched[:num_need]}"
    
    return 0, f"❌ 未包含足够关键词,还需 {num_need - len(matched)} 个,已匹配: {matched}"


def model_word_freq(num_need, keywords, corresponding_parts, question):
    """检查第一个关键词出现次数恰好为 num_need"""
    kw = to_lowercase_list(keywords)[0]
    language = detect_primary_language(question)
    
    total_count = 0
    details = []
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language=language)[0]
        print(tokens)
        count = count_keyword_occurrences(kw, tokens, part.lower(), language)
        if count > 0:
            details.append(f"'{part}' 中出现 {count} 次")
        total_count += count
    
    kw_display = format_keyword_display(kw, language)
    
    if total_count == num_need:
        detail_str = f"({'; '.join(details)})" if details else ""
        return 1, f"✅ {kw_display} 共出现 {total_count} 次,符合要求 {detail_str}"
    
    detail_str = f"({'; '.join(details) if details else '未找到'})"
    return 0, f"❌ {kw_display} 共出现 {total_count} 次,要求 {num_need} 次 {detail_str}"


def model_non_word_freq(num_need, keywords, corresponding_parts, question):
    """检查第一个关键词出现次数不超过 num_need"""
    kw = to_lowercase_list(keywords)[0]
    language = detect_primary_language(question)
    
    total_count = 0
    details = []
    
    for part in corresponding_parts:
        tokens = tokenize_texts_with_normalization(part, language)[0]
        count = count_keyword_occurrences(kw, tokens, part.lower(), language)
        if count > 0:
            details.append(f"'{part}' 中出现 {count} 次")
        total_count += count
    
    kw_display = format_keyword_display(kw, language)
    
    if total_count <= num_need:
        detail_str = f"({'; '.join(details) if details else '未找到'})"
        return 1, f"✅ {kw_display} 共出现 {total_count} 次,不超过 {num_need} 次 {detail_str}"
    
    return 0, f"❌ {kw_display} 共出现 {total_count} 次,超过 {num_need} 次 ({'; '.join(details)})"


def model_non_very_similar(sentences_list, question):
    """如果有两个句子的词集合复合率超过75%,则认为不匹配"""
    language = detect_primary_language(question)
    tokens_list = tokenize_texts_with_normalization(sentences_list)
    
    def calculate_similarity(tokens1, tokens2):
        set1, set2 = set(tokens1), set(tokens2)
        total = len(set1) + len(set2)
        if total == 0:
            return 0
        return (2 * len(set1 & set2)) / total
    
    for i in range(len(sentences_list)):
        for j in range(i + 1, len(sentences_list)):
            sim = calculate_similarity(tokens_list[i], tokens_list[j])
            
            if sim > 0.75:
                common_words = set(tokens_list[i]) & set(tokens_list[j])
                return 0, (f"❌ 句子对相似度过高:\n"
                          f"1: '{sentences_list[i]}'\n"
                          f"2: '{sentences_list[j]}'\n"
                          f"相似度: {sim:.3f}\n"
                          f"共同词汇: {list(common_words)}")
    
    max_sim = max([calculate_similarity(tokens_list[i], tokens_list[j]) 
                   for i in range(len(tokens_list)) 
                   for j in range(i + 1, len(tokens_list))], default=0)
    
    return 1, f"✅ 无特别相似句子 (最高相似度: {max_sim:.3f})"


if __name__ == '__main__':
    # 测试代码
    print(tokenize_texts_with_normalization("travaux", language="fr"))
    # print(tokenize_texts_with_normalization("trabajo", language="es"))
    # print(tokenize_texts_with_normalization("s’il", language="fr"))
    # print(tokenize_texts_with_normalization("qu’il", language="fr"))
    # print(tokenize_texts_with_normalization("jusqu’il", language="fr"))
    # print(tokenize_texts_with_normalization("lorsqu’il", language="fr"))
    # осведомленность осведомлённость
    # keywords = ["therme"]
    # model_response = ["Die Thermen in Japan sind wunderschön.", "Ich besuche gerne eine Therme."]
