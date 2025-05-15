import re
from .utils import txt_to_json
from .rule_utils.keywords import model_keywords, model_non_keywords, model_keywords_any, model_word_freq, model_non_word_freq
from .rule_utils.chinese_eng_ratio import chinese_english_ratio, count_mixed_language_words
from .rule_utils.len_and_numbers import model_each_length, model_total_length, model_item_count, model_repeat_each, model_no_word_repeat, model_non_very_similar
from .rule_utils.regex import model_non_regex, model_regex
from .rule_utils.end_start_with import model_no_end_with_punctuation, model_endswith_each, model_startswith_each
from .rule_utils.chinese_poem import model_jielong, yayun, pingze, lvshi_yayun, fanti
from .rule_utils.schema import model_schema


def rule_based_evaluate(item, rule, model_response):
    try: 
        # 0. 是否出现所有["关键词", "关键词2", ...]
        if rule.startswith("keyword"):
            return model_keywords(txt_to_json(rule), model_response)
        
        # 1. 是否出现["关键词", "关键词2", ...]中的任意n个，比如: model_any_keywords2的意思是必须出现两个关键词
        if rule.startswith("any_keywords"):
            match = re.search(r'any_keywords(\d+)', rule)  # 匹配'any_keywords'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_keywords_any(num, txt_to_json(rule), model_response)
        
        # 2. 是否不出现["关键词", "关键词2", ...]
        elif rule.startswith("non_keyword") or rule.startswith("non_keyword"):
            return model_non_keywords(txt_to_json(rule), model_response)
        
        # 3. 统计["xxxx", "ccccc", "aaaaa", ...]每个信息的长度是否满足rule的要求
        elif rule.startswith("each_length"):
            return model_each_length(txt_to_json(rule), model_response)

        # 4. 统计["xxxx", "ccccc", "aaaaa", ...]的总长度是否满足rule的要求
        elif rule.startswith("total_length"):
            return model_total_length(txt_to_json(rule), model_response)
        
        # 5. 统计len(["xxxx", "ccccc", "aaaaa", ...])，看提供数量是否满足rule的要求
        elif rule.startswith("item_count"):
            return model_item_count(txt_to_json(rule), model_response)
        
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
            return model_endswith_each(txt_to_json(rule), model_response)

        # 9. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息开头
        elif rule.startswith("startswith_each"):
            return model_startswith_each(txt_to_json(rule), model_response)
        
        # 10. ["xxxx", "ccccc", "aaaaa", ...]每个element是否满足成语接龙，前一个结尾字=后一个开头字
        elif rule.startswith("jielong"):
            return model_jielong(model_response)
        
        # 11. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足押韵，押韵比例是否超过60%
        elif rule.startswith("yayun"):
            return yayun(model_response)
        
        # 12. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以标点结尾
        elif rule.startswith("no_end_with_punctuation"):
            return model_no_end_with_punctuation(model_response)
        
        # 13. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足中英比例
        elif rule.startswith("Chinese_English_ratio"):
            return chinese_english_ratio(txt_to_json(rule), model_response)
        
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
        
        elif rule.startswith("count_mixed_language_words"):
            return count_mixed_language_words(txt_to_json(rule), model_response)
        
        elif rule.startswith("word_freq"):
            match = re.search(r'word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_word_freq(num, txt_to_json(rule), model_response)
        
        elif rule.startswith("non_word_freq"):
            match = re.search(r'non_word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_non_word_freq(num, txt_to_json(rule), model_response)

        elif rule.startswith("fanti"):
            return fanti(model_response)
    except Exception as e:
        return 0, f"❌ RULE BASED EVAL ERROR: {e}"
    
    

    
