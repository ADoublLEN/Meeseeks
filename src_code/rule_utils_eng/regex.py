import re

def model_non_regex(rule, model_response):
    pattern = r"\|(.*?)\|"
    regex = re.search(pattern, rule).group(1)
    for item in model_response:
        if re.match(regex, item):
            return 0, f"✅ This item matches: {str(item)}, regex: {str(regex)}"
    return 1, "❌ No regex match found"

def model_regex(rule, model_response):
    pattern = r"\|(.*?)\|"
    regex = re.search(pattern, rule).group(1)
    for item in model_response:
        if re.fullmatch(regex, item):  # 使用 re.fullmatch 确保整个字符串匹配
            return 1, f"✅ This item matches: {str(item)}, regex: {str(regex)}"
    return 0, "❌ No regex match found"
