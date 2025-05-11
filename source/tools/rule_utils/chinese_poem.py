import subprocess
import sys

# 尝试导入pinyin库，如果失败则安装
try:
    import pypinyin
    import hanziconv
except ImportError:
    # 使用pip安装pinyin
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypinyin"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "hanziconv"])
    # 再次导入pinyin
    import pypinyin
    import hanziconv

from collections import Counter
from pypinyin import pinyin, Style
from ..utils import clean_up_text
from hanziconv import HanziConv

def extract_rhyme_vowels(words):
    rhyme_vowels = []
    
    for word in words:
        if word:  # 确保不是空字符串
            # 获取最后一个字的拼音
            last_char = word[-1]
            pinyin_result = pinyin(last_char, style=Style.FINALS)
            if pinyin_result:
                rhyme_vowels.append(pinyin_result[0][0])  # 提取韵母
    
    return rhyme_vowels

def calculate_rhyme_proportion(rhyme_vowels):
    # 统计每个韵母出现的次数
    rhyme_count = Counter(rhyme_vowels)
    total_rhymes = sum(rhyme_count.values())
    
    # 计算每个韵母的比例
    rhyme_proportion = {rhyme: count / total_rhymes for rhyme, count in rhyme_count.items()}
    return rhyme_proportion

def yayun(text):
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    rhyme_vowels = extract_rhyme_vowels(text)
    rhyme_proportion = calculate_rhyme_proportion(rhyme_vowels)
    if max(rhyme_proportion.values()) > 0.5:
        return 1, f"✅ 匹配，韵脚比例详情为：{str(rhyme_proportion)}"
    else:
        return 0, f"❌ 不匹配，韵脚比例详情为：{str(rhyme_proportion)}，没有一个韵脚比例超过50%，韵脚比例超过50%视为押韵"

def extract_even_rhyme_vowels(text):
    rhyme_vowels = []
    
    # 遍历偶数句
    for i in range(1, len(text), 2):  # 从第二句开始，步长为2
        word = text[i]
        if word:  # 确保不是空字符串
            # 获取最后一个字的拼音
            last_char = word[-1]
            pinyin_result = pinyin(last_char, style=Style.FINALS)
            if pinyin_result:
                rhyme_vowels.append(pinyin_result[0][0])  # 提取韵母
    
    return rhyme_vowels

def lvshi_yayun(text):
    for i in range(len(text)):
        text[i] = clean_up_text(text[i])

    # 提取偶数句的韵母
    rhyme_vowels = extract_even_rhyme_vowels(text)
    
    # 判断偶数句的韵母是否一致
    if len(set(rhyme_vowels)) == 1:  # 如果集合长度为1，说明韵母一致
        return 1, f"✅ 偶数句韵母一致，偶数句韵母为：{rhyme_vowels}"
    else:
        return 0, f"❌ 偶数句韵母不一致，偶数句韵母为：{rhyme_vowels}"

def get_tone(pinyin_list):
    tones = []
    for py in pinyin_list:
        if py[-1].isdigit():
            tones.append(int(py[-1]))
        else:
            tones.append(0)  # 轻声
    return tones

def get_pingze(sentence):
    pinyin_result = pinyin(sentence, style=Style.TONE3)
    tones = get_tone([py[0] for py in pinyin_result])
    pingze = []
    for tone in tones:
        if tone in [1, 2]:
            pingze.append('平')
        elif tone in [3, 4]:
            pingze.append('仄')
        else:
            pingze.append('轻')
    return ''.join(pingze)

def pingze(poem_list):
    for i in range(len(poem_list)):
        poem_list[i] = clean_up_text(poem_list[i])
    results = []
    pingzeset = set()
    for sentence in poem_list:
        pingze = get_pingze(sentence)
        pingzeset.add(pingze)
        results.append(f"'{str(sentence)}' 的平仄为: {str(pingze)}")
    if len(pingzeset) != 1:
        return 0, f"❌ 平仄不一致，平仄详情：{str(results)}"
    else:
        return 1, f"✅ 平仄一致，平仄详情：{str(results)}"

def model_jielong(chengyu_list):
    for i in range(len(chengyu_list)):
        chengyu_list[i] = clean_up_text(chengyu_list[i])

    for i in range(len(chengyu_list) - 1):
        last_char = chengyu_list[i][-1]
        next_first_char = chengyu_list[i + 1][0]
        if last_char != next_first_char:
            return 0, f"❌ 不匹配，成语：{str(chengyu_list[i])}的最后一个字和成语：{str(chengyu_list[i + 1])}的第一个字不一致"
    return 1, f"✅ 匹配，成语：{str(chengyu_list)}"


def fanti(text):
    text = clean_up_text(text[0])
    fanti_text = HanziConv.toTraditional(text)

    # print("简体： ", text)
    # print("繁体： ", fanti_text)
    for i in range(len(text)):
        # print(text[i]," - ",fanti_text[i])
        if text[i] != fanti_text[i]:
            return 0, f"❌ {text[i]} 不是繁体"
    return 1, "✅ 内容全是繁体"
