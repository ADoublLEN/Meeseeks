# Keyword matching related functions

def model_keywords(keywords, corresponding_parts):
    """Check if each corresponding part contains all keywords"""
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    keywords = [keyword.lower() for keyword in keywords]
    for corresponding_part in corresponding_parts:
        for keyword in keywords:
            if keyword not in corresponding_part:
                return 0, f"❌ {str(corresponding_part)} missing keyword: {str(keyword)}"
    return 1, f"✅ Keywords matched, all content contains keywords: {str(keywords)}"

def model_non_keywords(keywords, corresponding_parts):
    """Check if each corresponding part does not contain any keywords"""
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    keywords = [keyword.lower() for keyword in keywords]
    for corresponding_part in corresponding_parts:
        for keyword in keywords:
            if str(keyword) in str(corresponding_part):
                return 0, f"❌ {str(corresponding_part)} contains keyword: {str(keyword)}"
    return 1, f"✅ No keywords found, all content does not contain keywords: {str(keywords)}"

def model_keywords_any(num_need, keywords, corresponding_parts):
    """Check if contains specified number of keywords"""
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    keywords = [keyword.lower() for keyword in keywords]
    og_num_need = num_need
    keywords_matched = []
    for keyword in keywords:
        if str(keyword) in str(corresponding_parts):
            keywords_matched.append(keyword)
            num_need -= 1
            if num_need == 0:
                return 1, f"✅ Contains {og_num_need} keywords"
    return 0, f"❌ Does not contain/insufficient {og_num_need} keywords, missing {num_need} keywords"


def model_word_freq(num_need, keywords, corresponding_parts):
    """Count if each keyword appears exactly num_need times in corresponding_parts"""
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    corresponding_part = corresponding_parts[0]

    all_correct = True
    results = []

    for keyword in keywords:
        keyword_lower = keyword.lower()
        word_freq = corresponding_part.count(keyword_lower)
        results.append((keyword, word_freq))
        if word_freq != num_need:
            all_correct = False

    if all_correct:
        return 1, f"✅ Each keyword appears exactly {num_need} times"
    else:
        details = [f"{keyword}: {freq} times" for keyword, freq in results]
        return 0, f"❌ Actual occurrences: {', '.join(details)}, requirement: each keyword should appear {num_need} times"

def model_non_word_freq(num_need, keywords, corresponding_parts):
    """Count if each keyword appears no more than num_need times in corresponding_parts"""
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]
    corresponding_part = corresponding_parts[0]

    all_correct = True
    results = []

    for keyword in keywords:
        keyword_lower = keyword.lower()
        word_freq = corresponding_part.count(keyword_lower)
        results.append((keyword, word_freq))
        if word_freq > num_need:
            all_correct = False

    if all_correct:
        return 1, f"✅ Each keyword appears no more than {num_need} times"
    else:
        details = [f"{keyword}: {freq} times" for keyword, freq in results]
        return 0, f"❌ Actual occurrences: {', '.join(details)}, requirement: each keyword should appear at most {num_need} times"


def model_word_freq_any(num_need, keywords, corresponding_parts):
    """Count if any keyword appears exactly num_need times total in corresponding_parts"""
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]

    # Check each corresponding_part
    for part_idx, corresponding_part in enumerate(corresponding_parts):
        total_freq = 0
        all_keyword_details = []

        for keyword in keywords:
            keyword_lower = keyword.lower()
            word_freq = corresponding_part.count(keyword_lower)
            total_freq += word_freq
            all_keyword_details.append(f"'{keyword}': {word_freq} times")

        if total_freq != num_need:
            details_str = ' | '.join(all_keyword_details)
            return 0, f"❌ Part {part_idx+1} check failed\n   Keyword occurrences: [{details_str}]\n   Total: {total_freq} times, required: {num_need} times"

    # All parts meet the condition
    return 1, f"✅ All parts have keywords appearing exactly {num_need} times total"

def model_non_word_freq_any(num_need, keywords, corresponding_parts):
    """Count if any keyword appears no more than num_need times total in corresponding_parts"""
    corresponding_parts = [corresponding_part.lower() for corresponding_part in corresponding_parts]

    # Check each corresponding_part
    for part_idx, corresponding_part in enumerate(corresponding_parts):
        total_freq = 0
        all_keyword_details = []

        for keyword in keywords:
            keyword_lower = keyword.lower()
            word_freq = corresponding_part.count(keyword_lower)
            total_freq += word_freq
            all_keyword_details.append(f"'{keyword}': {word_freq} times")

        if total_freq > num_need:
            details_str = ' | '.join(all_keyword_details)
            return 0, f"❌ Part {part_idx+1} check failed\n   Keyword occurrences: [{details_str}]\n   Total: {total_freq} times, required: at most {num_need} times"

    # All parts meet the condition
    return 1, f"✅ All parts have keywords appearing no more than {num_need} times total"
