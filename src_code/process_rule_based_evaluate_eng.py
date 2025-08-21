import re
from utils_eng import txt_to_json_og
from rule_utils_eng.keywords import model_keywords, model_non_keywords, model_keywords_any, model_word_freq, model_non_word_freq, model_non_very_similar
from rule_utils_eng.word_count import model_each_length, model_total_length, arabic_each_length, portuguese_each_length, portuguese_total_length,  arabic_total_length, count_chinese_words, mixed_language_each_length,russian_each_length,russian_total_length,french_each_length,french_total_length,spanish_each_length, spanish_total_length,indonesian_each_length,indonesian_total_length,indonesian_each_length,indonesian_total_length,german_each_length,german_total_length
from rule_utils_eng.item_count import model_item_count
from rule_utils_eng.detect_repeat_for_space_split_language import model_repeat_each, model_no_word_repeat
from rule_utils_eng.regex import model_non_regex, model_regex
from rule_utils_eng.end_start_with import model_no_end_with_punctuation, model_endswith_each, model_startswith_each
from rule_utils_eng.yayun import model_jielong, yayun, portuguese_yayun, arabic_yayun, german_yayun, spanish_yayun, indonesian_yayun, russian_yayun, french_yayun
from rule_utils_eng.schema import model_schema
from rule_utils_eng.eng_special import count_cap_num, count_low_num, compound_word_num, no_character_repeat, character_freq

def rule_based_evaluate(item, rule, model_response):
    # print(rule)
    try:
        # 0. 是否出现所有["关键词", "关键词2", ...]
        if rule.startswith("keyword"):
            return model_keywords(txt_to_json_og(rule), model_response, item["question"])
        
        # 1. 是否出现["关键词", "关键词2", ...]中的任意n个，比如: model_any_keywords2的意思是必须出现两个关键词
        if rule.startswith("any_keywords"):
            match = re.search(r'any_keywords(\d+)', rule)  # 匹配'any_keywords'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_keywords_any(num, txt_to_json_og(rule), model_response, item["question"])
        
        # 2. 是否不出现["关键词", "关键词2", ...]
        elif rule.startswith("non_keyword") or rule.startswith("non_keyword"):
            return model_non_keywords(txt_to_json_og(rule), model_response, item["question"])
    
        elif rule.startswith("non_special_notation"):
            _, _, notation = rule.partition(":")
            for i in model_response:
                if notation in i:
                    return 0, f"{notation} detected in model response: {i}"
            return 1, f"{notation} not detected in any of model responses"

        
        # 3. 统计["xxxx", "ccccc", "aaaaa", ...]每个信息的长度是否满足rule的要求
        elif rule.startswith("each_length"):
            flag, detail, _ = model_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        
        # 3. 统计阿拉伯语字数
        elif rule.startswith("arabic_each_length"):
            flag, detail, _ = arabic_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        
        elif rule.lower().startswith("portuguese_each_length"):
            flag, detail, _ =  portuguese_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        
        # 4. 统计["xxxx", "ccccc", "aaaaa", ...]的总长度是否满足rule的要求
        elif rule.startswith("total_length"):
            return model_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("arabic_total_length"):
            return arabic_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("portuguese_total_length"):
            return portuguese_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("russian_each_length"):
            flag, detail, _ = russian_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("russian_total_length"):
            return russian_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("french_each_length"):
            flag, detail, _ = french_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("french_total_length"):
            return french_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("spanish_each_length"):
            flag, detail, _ = spanish_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("spanish_total_length"):
            return spanish_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("indonesian_each_length"):
            flag, detail, _ = indonesian_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("indonesian_total_length"):
            return indonesian_total_length(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("german_each_length"):
            flag, detail, _ = german_each_length(txt_to_json_og(rule), model_response)
            return flag, detail
        elif rule.startswith("german_total_length"):
            return german_total_length(txt_to_json_og(rule), model_response)

        elif rule.startswith("mixed_language_each_length"):
            language = rule.split(":")[1]
            word_range = rule.split(":")[2]
            flag, exp, _,_  = mixed_language_each_length(txt_to_json_og(word_range), model_response, language)
            return flag, exp
        
        elif rule.startswith("language_ratio"):
            language = rule.split(":")[1]
            ratio = rule.split(":")[2]
            ratio = txt_to_json_og(rule)

            for i in model_response:
                chinese_count = count_chinese_words(i)
                _, _, _, language_word_count = mixed_language_each_length(txt_to_json_og(rule), model_response, language)
                real_ratio = 1 if language_word_count == 0 else chinese_count / language_word_count
                expected_ratio = ratio[0] / ratio[1]
                
                # 四舍五入到小数点后两位进行比较
                if round(real_ratio, 2) != round(expected_ratio, 2):
                    return 0, f"❌ Not match: Chinese character num:：{str(chinese_count)}，{language} word num：{str(language_word_count)} ratio: {real_ratio:.4f}, expected ratio: {str(ratio[0])} / {str(ratio[1])} = {expected_ratio:.4f}, at least make sure the two decimal places are consistent"

            return 1, "✅ 匹配"
        
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

        # 9. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以rule[0]指定的信息开头
        elif rule.startswith("startswith_each"):
            return model_startswith_each(txt_to_json_og(rule), model_response)
        
        # 10. ["xxxx", "ccccc", "aaaaa", ...]每个element是否满足成语接龙，前一个结尾字=后一个开头字
        elif rule.startswith("jielong"):
            return model_jielong(model_response)
        
        # 11. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否满足押韵，押韵比例是否超过60%
        elif rule.startswith("yayun"):
            return yayun(model_response)
        
        elif rule.startswith("portuguese_yayun"):
            return portuguese_yayun(model_response)
        
        elif rule.startswith("arabic_yayun"):
            return arabic_yayun(model_response)
        
        elif rule.startswith("german_yayun"):
            return german_yayun(model_response)
        
        elif rule.startswith("french_yayun"):
            return french_yayun(model_response)
        
        elif rule.startswith("russian_yayun"):
            return russian_yayun(model_response)
        
        elif rule.startswith("spanish_yayun"):
            return spanish_yayun(model_response)
        
        elif rule.startswith("indonesian_yayun"):
            return indonesian_yayun(model_response)
        
        # 12. 统计["xxxx", "ccccc", "aaaaa", ...]每个element是否以标点结尾
        elif rule.startswith("no_end_with_punctuation"):
            return model_no_end_with_punctuation(model_response)
        
        # 14. 判断是否是xxx schema
        elif rule.startswith("SCHEMA"):
            return model_schema(item, rule.split(":")[1], model_response)
        
        # 16. 所有element内没有任何文字是一样的
        elif rule.startswith("no_word_repeat"):
            return model_no_word_repeat(model_response)
        
        # 是否有75%以上的字有重复
        elif rule.startswith("non_very_similar"):
            return model_non_very_similar(model_response, item["question"])
        
        elif rule.startswith("word_freq"):
            match = re.search(r'word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_word_freq(num, txt_to_json_og(rule), model_response, item["question"])
        
        elif rule.startswith("non_word_freq"):
            match = re.search(r'non_word_freq(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return model_non_word_freq(num, txt_to_json_og(rule), model_response, item["question"])

        elif rule.startswith("ENG_cap_num"):
            match = re.search(r'ENG_cap_num:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return count_cap_num(num, model_response)
        
        elif rule.startswith("ENG_low_num"):
            match = re.search(r'ENG_low_num:(\d+)', rule)  # 匹配'word_freq'后面的数字
            if match:
                num = int(match.group(1))  # 转换为整数并返回
            else:
                num = 1
            return count_low_num(num, model_response)
        
        elif rule.startswith("compound_word_num"):
            return compound_word_num(txt_to_json_og(rule), model_response)
        
        elif rule.startswith("no_character_repeat"):
            return no_character_repeat(model_response)

        elif rule.startswith("character_freq_"):
            # 修正正则表达式
            # 一行解决
            match = re.search(r'character_freq_([a-zA-Z]):\[([\d,\s]+)\]', rule)

            letter = match.group(1)
            range_list = [int(x.strip()) for x in match.group(2).split(',')]
            return character_freq(letter, range_list, model_response)
        
        
                
    except Exception as e:
        return 0, f"❌ RULE BASED EVAL ERROR: {e}"
    

if __name__ == "__main__":
    # print(rule_based_evaluate({}, "non_special_notation:\n", ["AAA\nAAA"]))
    # print(rule_based_evaluate({}, "mixed_language_each_length:portuguese:[10,20]", ["Claro! 你今天的trabalho做得非常好，parabéns!"]))
    # print(rule_based_evaluate({}, "language_ratio:portuguese:[10,20]", ["Claro! 你今天的trabalho做得非常好，parabéns!"]))
    # print(rule_based_evaluate({}, "non_word_freq10:[\"trabalho\"]", ["Claro! 你今天的trabalho做得非常好，parabéns!"]))
    print(model_each_length([2,3], ["complexité.\n\nAujourd’hui"]))
    