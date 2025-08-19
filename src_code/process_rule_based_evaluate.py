import re
from utils import txt_to_json_og

# 使用重构后的模块结构
from rule_utils.keyword_matching import (
    model_keywords, model_non_keywords, model_keywords_any,
    model_word_freq, model_non_word_freq, model_word_freq_any
)
from rule_utils.language_ratio import (
    chinese_english_ratio, count_mixed_chinese_english_words,
    korean_english_ratio, count_mixed_korean_english_words,
    japanese_english_ratio, count_mixed_japanese_english_words
)
from rule_utils.text_analysis import (
    model_each_length, model_total_length, model_item_count,
    model_repeat_each, model_no_word_repeat, model_non_very_similar
)
from rule_utils.text_formatting import (
    model_non_regex, model_regex, model_no_end_with_punctuation,
    model_endswith_each, model_startswith_each, endswithany_each
)
from rule_utils.rhyme_analysis import (
    yayun, pingze, lvshi_yayun, fanti, has_heteronym, jpn_yayun, kor_yayun
)
from rule_utils.schema_validation import model_schema
from rule_utils.special_patterns import (
    has_double_consonants, has_korean_abbreviation, each_has_double_consonants,
    jpn_mixed_ratio, has_small_kana, has_furigana_pattern, has_kanji_okurigana_pattern,
    model_jielong, model_jielong2, model_jielong3, model_jielong4, word_structure
)

def rule_based_evaluate(item, rule, model_response):
    try:
        # print(rule)
        # 0. 是否出现所有["关键词", "关键词2", ...]
        if rule.startswith("keyword"):
            return model_keywords(txt_to_json_og(rule), model_response)
        
        # 1. 是否出现["关键词", "关键词2", ...]中的任意n个，比如: model_any_keywords2的意思是必须出现两个关键词
        if rule.startswith("any_keywords"):
            match = re.search(r'any_keywords(\d+)', rule)  # 匹配'any_keywords'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_keywords_any(num, txt_to_json_og(rule), model_response)
        
        # 2. 是否不出现["关键词", "关键词2", ...]
        elif rule.startswith("non_keyword") or rule.startswith("non_keyword"):
            return model_non_keywords(txt_to_json_og(rule), model_response)
        
        # 3. 统计["xxxx", "ccccc", "aaaaa", ...]每个信息的长度是否满足rule的要求
        elif rule.startswith("each_length"):
            return model_each_length(txt_to_json_og(rule), model_response)

        # 4. 统计["xxxx", "ccccc", "aaaaa", ...]的总长度是否满足rule的要求
        elif rule.startswith("total_length"):
            return model_total_length(txt_to_json_og(rule), model_response)
        
        # 5. 统计len(["xxxx", "ccccc", "aaaaa", ...])，看提供数量是否满足rule的要求
        elif rule.startswith("item_count"):
            return model_item_count(txt_to_json_og(rule), model_response)
        
        # 6. 判断是否不存在此正则表达式匹配
        elif rule.startswith("non_regex"):
            return model_non_regex(rule, model_response)
        
        # 6.1. 判断是否满足此正则表达式匹配
        elif rule.startswith("regex"):
            return model_regex(rule, model_response)
        
        # 7. 统计["xxxx", "ccccc", "aaaaa", ...]看是否有element是重复的
        elif rule.startswith("repeat_each"):
            return model_repeat_each(model_response)
        
        # 8. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息结尾
        elif rule.startswith("endswith_each"):
            return model_endswith_each(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("endswithany_each"):
            return endswithany_each(txt_to_json_og(rule), model_response)

        # 9. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息开头
        elif rule.startswith("startswith_each"):
            return model_startswith_each(txt_to_json_og(rule), model_response)
        
        # 10. ["xxxx", "ccccc", "aaaaa", ...]每个element是否满足成语接龙，前一个结尾字=后一个开头字
        elif rule.startswith("jielong1"):
            return model_jielong(model_response)
        
        elif rule.startswith("jielong2"):
            return model_jielong2(model_response)
        
        elif rule.startswith("jielong3"):
            return model_jielong3(model_response)

        elif rule.startswith("jielong4"):
            return model_jielong4(model_response)
        
        # 11. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足押韵，押韵比例是否超过60%
        elif rule.startswith("yayun"):
            return yayun(model_response)
        
        elif rule.startswith("jpn_yayun"):
            return jpn_yayun(model_response)
        
        elif rule.startswith("kor_yayun"):
            return kor_yayun(model_response)
        
        # 12. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以标点结尾
        elif rule.startswith("no_end_with_punctuation"):
            return model_no_end_with_punctuation(model_response)
        
        # 13. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足中英比例
        elif rule.startswith("chinese_english_ratio"):
            return chinese_english_ratio(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("korean_english_ratio"):
            return korean_english_ratio(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("japanese_english_ratio"):
            return japanese_english_ratio(txt_to_json_og(rule), model_response)
        
        # 14. 判断是否是xxx schema
        elif rule.startswith("SCHEMA"):
            return model_schema(item, rule.split(":")[1], model_response)

        # 15. 判断平仄情况
        elif rule.startswith("pingze"):
            return pingze(model_response)
        
        # 16. 所有element内没有任何文字是一样的
        elif rule.startswith("no_word_repeat"):
            return model_no_word_repeat(model_response)
        
        # 是否有75%以上的字有重复
        elif rule.startswith("non_very_similar"):
            return model_non_very_similar(model_response)
        
        elif rule.startswith("lvshi_yayun"):
            return lvshi_yayun(model_response)
        
        elif rule.startswith("count_mixed_chinese_english_words"):
            return count_mixed_chinese_english_words(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("count_mixed_korean_english_words"):
            return count_mixed_korean_english_words(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("count_mixed_japanese_english_words"):
            return count_mixed_japanese_english_words(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("word_freq"):
            match = re.search(r'word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_word_freq(num, txt_to_json_og(rule), model_response)
        
        elif rule.startswith("any_word_freq"):
            match = re.search(r'any_word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_word_freq_any(num, txt_to_json_og(rule), model_response)
        

        elif rule.startswith("double_consonants"):
            match = re.search(r'double_consonants:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_double_consonants(model_response, num)

        elif rule.startswith("each_has_double_consonants"):
            match = re.search(r'each_has_double_consonants:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return each_has_double_consonants(model_response, num)

        elif rule.startswith("has_heteronym"):
            match = re.search(r'has_heteronym:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_heteronym(model_response, num)
        
        elif rule.startswith("non_word_freq"):
            match = re.search(r'non_word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_non_word_freq(num, txt_to_json_og(rule), model_response)

        elif rule.startswith("fanti"):
            return fanti(model_response)
        
        elif rule.startswith("non_special_notation"):
            _, _, notation = rule.partition(":")
            for i in model_response:
                if notation in i:
                    return 0, f"{notation} detected in model response: {i}"
            return 1, f"{notation} not detected in any of model responses"
        
        elif rule.startswith("notation_freq"):
            # print(rule)
            match = re.search(r'notation_freq(\d+)', rule)  # 匹配'notation_freq'后面的数字
            
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            # print("detected_nums: ", num)
            notations = txt_to_json_og(rule)
            
            # 检查每个model_response中的内容
            for response_idx, response in enumerate(model_response):
                # 检查每个notation是否都出现了num次
                all_correct = True
                actual_counts = []
                
                for notation in notations:
                    actual_count = response.count(notation)
                    actual_counts.append(actual_count)
                    if actual_count != num:
                        all_correct = False
                
                if not all_correct:
                    # 构建详细的错误信息
                    details = []
                    for i, notation in enumerate(notations):
                        details.append(f"{notation}: {actual_counts[i]}次")
                    return 0, f"❌ 第{response_idx+1}个回答中，{notations}中每个符号理应出现{num}次，实际出现次数: [{', '.join(details)}]"
            
            # 所有回答都满足条件
            return 1, f"✅ 所有回答中每个符号都出现{num}次"


        elif rule.startswith("has_korean_abbreviation"):
            _, _, abbreviation = rule.partition(":")
            return has_korean_abbreviation(model_response, abbreviation)
            
        elif rule.startswith("jpn_mixed_ratio"):
            ratio = txt_to_json_og(rule)
            hiragana_ratio = ratio[0]
            katakana_ratio = ratio[1]
            kanji_ratio = ratio[2]

            return jpn_mixed_ratio(model_response, hiragana_ratio, katakana_ratio, kanji_ratio)
    
        elif rule.startswith("has_small_kana"):
            match = re.search(r'has_small_kana(\d+)', rule) 
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_small_kana(model_response, num)
        
        elif rule.startswith("has_furigana_pattern"):
            match = re.search(r'has_furigana_pattern:(\d+)', rule) 
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_furigana_pattern(model_response, num)
        
        elif rule.startswith("has_kanji_okurigana_pattern"):
            match = re.search(r'has_kanji_okurigana_pattern:(\d+)', rule) 
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return has_kanji_okurigana_pattern(model_response, num)
        
        elif rule.startswith("word_structure"):
            match = re.search(r'word_structure:(\w+)', rule)
            result = match.group(1)
            return word_structure(model_response, result)

        
    except Exception as e:
        return 0, f"❌ RULE BASED EVAL ERROR: {e}"
    

    
