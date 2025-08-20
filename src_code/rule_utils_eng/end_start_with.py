import re
import os
import sys

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_eng import clean_up_text, to_lowercase_list

def model_no_end_with_punctuation(model_responses):
    def check_punctuation(s):
        if re.match(r'.*[.,!?:;]$', s):
            return 0
        else:
            return 1
    for item in model_responses:
        if check_punctuation(item) == 0:
            return 0, f"❌ Found sentence ending with punctuation: {str(item)}"
    return 1, f"✅ No sentences ending with punctuation found"


def model_endswith_each(rule, model_response):
    rule = to_lowercase_list(rule)[0]
    model_response = to_lowercase_list(model_response)
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.endswith(temp_rule):
            return 0, f"❌ No match, sentence: {str(item)} does not end with {str(rule)}"
    return 1, f"✅ Match, sentences: {str(model_response)} all end with {str(rule)}"

def model_startswith_each(rule, model_response):
    rule = to_lowercase_list(rule)[0]
    model_response = to_lowercase_list(model_response)
    for item in model_response:
        temp_item = clean_up_text(item)
        temp_rule = clean_up_text(rule)
        if not temp_item.startswith(temp_rule):
            return 0, f"❌ Not Match, Sentence：{str(item)} does not start with {str(rule)}"
    return 1, f"✅ Match, Sentence {str(model_response)} does start with {str(rule)}"

