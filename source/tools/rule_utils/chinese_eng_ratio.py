import re

def calculate_chinese_english_word_ratio(text):
    # 统计中文字数
    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    
    # 统计英文单词数
    english_words = re.findall(r'\b[a-zA-Z]+\b', text)
    english_word_count = len(english_words)
    
    return chinese_count, english_word_count

def chinese_english_ratio(ratio, model_responses):
    for model_response in model_responses:
        chinese_count, english_word_count = calculate_chinese_english_word_ratio(model_response)
        real_ratio = 1 if english_word_count == 0 else chinese_count / english_word_count
        if real_ratio != ratio[0] / ratio[1]:
            return 0, f"❌ 不匹配: 中文字符数：{str(chinese_count)}，英文单词数：{str(english_word_count)}，比例：{real_ratio}, 期望比例为：{str(ratio[0])} / {str(ratio[1])} = {str(ratio[0] / ratio[1])}"
    return 1, "✅ 匹配"

def count_mixed_language_words(range, model_responses):
    for model_response in model_responses:
        chinese_count, english_word_count = calculate_chinese_english_word_ratio(model_response)
        if not range[0] <= chinese_count + english_word_count <= range[1]:
            return 0, f"❌ 数量不匹配此范围{range}: 模型回答中的中文字符数是：{str(chinese_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(chinese_count + english_word_count)}"
    return 1, f"✅ 数量匹配：模型回答中的中文字符数是：{str(chinese_count)}，英文单词数是：{str(english_word_count)}，总数量是：{str(chinese_count + english_word_count)}"

