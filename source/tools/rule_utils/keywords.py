# 1. 每个corresponding part都需要出现所有keywords
def model_keywords(keywords, corresponding_parts):
    for corresponding_part in corresponding_parts:
        for keyword in keywords:
            if keyword not in corresponding_part:
                return 0, f"❌ {str(corresponding_part)} 内缺少关键词: {str(keyword)}"
    return 1, f"✅ 关键词匹配，所有内容中均出现了关键词：{str(keywords)}"

# 2. 每个corresponding part都不能出现任何keywords
def model_non_keywords(keywords, corresponding_parts):
    for corresponding_part in corresponding_parts:
        for keyword in keywords:
            if str(keyword) in str(corresponding_part):
                return 0, f"❌ {str(corresponding_part)} 内包含关键词: {str(keyword)}"
    return 1, f"✅ 无关键词，所有内容中均未出现关键词：{str(keywords)}"

# 3. keywords any
def model_keywords_any(num_need, keywords, corresponding_parts):
    og_num_need = num_need
    keywords_matched = []
    for keyword in keywords:
        if str(keyword) in str(corresponding_parts):
            keywords_matched.append(keyword)
            num_need -= 1
            if num_need == 0:
                return 1, f"✅ 包含{og_num_need}个关键词"
    return 0, f"❌ 不包含/不够 {og_num_need} 关键词，还差{num_need}个关键词"


# 4. word frequency
def model_word_freq(num_need, keywords, corresponding_parts):
    # 统计keyword在corresponding_parts中出现的次数是否是num_need
    keyword = keywords[0]
    corresponding_part = corresponding_parts[0]
    word_freq = corresponding_part.count(keyword)
    if word_freq == num_need:
        return 1, f"✅ {keyword} 出现刚好 {num_need} 次"
    else:
        return 0, f"❌ {keyword} 出现 {word_freq} 次，题目要求出现 {num_need} 次"
    

# 5. non word frequency
def model_non_word_freq(num_need, keywords, corresponding_parts):
    # 统计keyword在corresponding_parts中出现的次数是否不超过num_need
    keyword = keywords[0]
    corresponding_part = corresponding_parts[0]
    word_freq = corresponding_part.count(keyword)
    if word_freq <= num_need:
        return 1, f"✅ {keyword} 出现 {num_need} 次"
    else:
        return 0, f"❌ {keyword} 出现 {word_freq} 次，题目要求最多出现 {num_need} 次"
