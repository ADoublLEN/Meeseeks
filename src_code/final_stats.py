#!/usr/bin/env python3
"""
计算评估结果的最终统计指标
包含 meeseeks_score、utility_scores 和层级能力统计
"""

import json
import os


# 中英文映射字典
CHINESE_TO_ENGLISH_MAPPING = {
    "任务意图理解": "Intent Recognition",
    "在干扰下完成指令": "Follow instruction under distraction",
    "单元细节合规": "Granular Content Validation",
    "主题约束": "Theme requirement",
    "文体约束": "Stylistic requirement",
    "生成特定文案": "Generate in certain style",
    "生成名字/标题": "Generate names/titles",
    "语言约束": "Language requirement",
    "中英文混杂": "Generate Chinese-English-mixed article",
    "繁体约束": "Generate in traditional/simple Chinese",
    "大小写": "Case requirement",
    "格式约束": "Granular format requirement",
    "特定格式": "Generate in other format",
    "日期格式": "Generate result in date-format",
    "字数约束": "Word count requirement",
    "精确": "Generate at accurate word number",
    "范围": "Generate in rough/range word number",
    "倍数": "Generate in X times word number of reference text",
    "多对象": "Generate multiple results under certain word requirement",
    "0~10字": "Generate in 0~10 words",
    "10~50字": "Generate in 10~50 words",
    "50~200字": "Generate in 50~200 words",
    "200字以上": "Generate in above 200 words",
    "其他特殊规则": "Other granular requirements",
    "押韵": "Generate rhyming content",
    "关键词": "Generate with certain keywords",
    "重复": "Generate repeat/non-repeat content",
    "平仄": "Generate with Chinese pingze rules",
    "接龙": "Generate with Chinese jielong rules",
    "emoji": "Generate with emoji",
    "符号": "Generate with/without punctuation",
    "写作手法": "Generate with certain rhetoric",
    "词频": "Generate with certain number of word X",
    "整体结构合规": "Output Structure Validation",
    "模版合规": "Output format requirement",
    "LaTeX": "LaTeX format",
    "JSON": "JSON format",
    "Markdown": "Markdown format",
    "单元数量合规": "Element number requirement",
    "答题逻辑合规": "Output logic requirement",
    "答题结构合规": "Generate by certain steps",
    "全面考虑": "Comprehensive consideration"
}


def translate_stats_dict(stats_dict, mapping):
    """将统计字典的键名从中文翻译为英文"""
    if not isinstance(stats_dict, dict):
        return stats_dict

    translated_dict = {}
    for key, value in stats_dict.items():
        # 翻译键名
        translated_key = mapping.get(key, key)

        if isinstance(value, dict):
            translated_value = {}
            for sub_key, sub_value in value.items():
                if sub_key == "children":
                    # 递归翻译children
                    translated_value[sub_key] = translate_stats_dict(sub_value, mapping)
                else:
                    translated_value[sub_key] = sub_value
            translated_dict[translated_key] = translated_value
        else:
            translated_dict[translated_key] = value

    return translated_dict


def calculate_final_score(subqs):
    """计算最终得分"""
    capabilities = {}

    for sub_q in subqs:
        # 如果没有"能力项"，使用"未定义"作为默认能力项
        capability_string = sub_q.get("能力项", "未定义")

        # 分割能力项字符串，处理可能存在的多个能力项
        if capability_string == "未定义":
            capability_names = ["未定义"]
        else:
            # 使用中文顿号、逗号或英文逗号分割
            capability_names = [name.strip() for name in capability_string.replace('、', ',').split(',')]
            # 过滤掉空字符串
            capability_names = [name for name in capability_names if name]

        # 为每个能力项添加评分
        for capability_name in capability_names:
            if capability_name not in capabilities:
                capabilities[capability_name] = []
            capabilities[capability_name].append(sub_q["eval_result"])

    score_by_capability = 0
    for capability, scores in capabilities.items():
        score_by_capability += sum(scores) / len(scores)

    if len(capabilities) == 0:
        score_by_capability = 0  # 肯定哪里出问题了
    else:
        score_by_capability = score_by_capability / len(capabilities)

    strict_cur_score = 0 if score_by_capability < 1 else score_by_capability
    return score_by_capability, strict_cur_score


def get_capability_result(result_info):
    """获取能力项层级统计结果"""
    # 层级关系定义
    hierarchical_relationship = {
        "任务意图理解": {
            "在干扰下完成指令": {}
        },
        "单元细节合规": {
            "主题约束": {},
            "文体约束": {
                "生成特定文案": {},
                "生成名字/标题": {}
            },
            "语言约束": {
                "中英文混杂": {},
                "繁体约束": {},
                "大小写": {}
            },
            "格式约束": {
                "特定格式": {},
                "日期格式": {}
            },
            "字数约束": {
                "精确": {},
                "范围": {},
                "倍数": {},
                "多对象": {},
                "0~10字": {},
                "10~50字": {},
                "50~200字": {},
                "200字以上": {}
            },
            "其他特殊规则": {
                "押韵": {},
                "关键词": {},
                "重复": {},
                "平仄": {},
                "接龙": {},
                "emoji": {},
                "符号": {},
                "写作手法": {},
                "词频": {}
            }
        },
        "整体结构合规": {
            "模版合规": {
                "LaTeX": {},
                "JSON": {},
                "Markdown": {}
            },
            "单元数量合规": {},
            "答题逻辑合规": {
                "答题结构合规": {},
                "全面考虑": {}
            }
        }
    }

    data = result_info
    capability_list = {}
    total_correct = 0
    total_wrong = 0

    for item in data:
        for subq in item["sub_questions"]:
            if "能力项" in subq:
                normalized_capabilities = subq["能力项"].replace("～", "~")
                cur_capabilities = normalized_capabilities.split("、")
                for capability in cur_capabilities:
                    if capability not in capability_list:
                        capability_list[capability] = [0, 0]
                    if subq["eval_result"] == 1:
                        capability_list[capability][0] += 1
                        total_correct += 1
                    else:
                        capability_list[capability][1] += 1
                        total_wrong += 1

    def calculate_hierarchical_stats(hierarchy, capability_stats):
        """递归计算每个层级节点的统计数据"""
        result = {}

        for key, value in hierarchy.items():
            correct = 0
            wrong = 0

            # 如果是叶子节点
            if not value:
                if key in capability_stats:
                    correct = capability_stats[key][0]
                    wrong = capability_stats[key][1]
            # 如果是非叶子节点，递归计算子节点
            else:
                sub_results = calculate_hierarchical_stats(value, capability_stats)
                for sub_stats in sub_results.values():
                    correct += sub_stats[0]
                    wrong += sub_stats[1]

            result[key] = [correct, wrong]

        return result

    # 计算所有层级的统计数据
    hierarchical_stats = calculate_hierarchical_stats(hierarchical_relationship, capability_list)

    def build_stats_dict(stats, hierarchy, level=0):
        """构建统计字典"""
        result_dict = {}
        for key, value in stats.items():
            total = value[0] + value[1]
            if total > 0:
                percentage = value[0] / total
                result_dict[key] = {
                    "percentage": percentage,
                    "correct": value[0],
                    "wrong": value[1],
                    "total": total
                }

                if key in hierarchy and isinstance(hierarchy[key], dict):
                    sub_stats = calculate_hierarchical_stats(hierarchy[key], capability_list)
                    result_dict[key]["children"] = build_stats_dict(sub_stats, hierarchy[key], level + 1)
                else:
                    result_dict[key]["children"] = {}

        return result_dict

    # 生成统计字典
    stats_dict = build_stats_dict(hierarchical_stats, hierarchical_relationship)
    return stats_dict


def calculate_and_save_stats(round_file_path, round_num, output_dir, language='chinese'):
    """
    计算并保存统计结果

    Args:
        round_file_path: round结果文件路径
        round_num: 轮次编号
        output_dir: 输出目录
        language: 语言类型，'chinese' 或 'english'
    """
    print(f"📊 Calculating statistics for round {round_num}...")

    # 读取数据
    with open(round_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 计算 meeseeks_score 和 utility_scores
    meeseeks_scores = [calculate_final_score(item["sub_questions"])[0] for item in data]
    utility_scores = [calculate_final_score(item["sub_questions"])[1] for item in data]

    meeseeks_score = sum(meeseeks_scores) / len(meeseeks_scores) if meeseeks_scores else 0
    utility_score = sum(utility_scores) / len(utility_scores) if utility_scores else 0

    # 计算层级统计（始终使用中文层级关系）
    capability_stats = get_capability_result(data)

    # 如果是英文，翻译键名
    if language == 'english':
        capability_stats = translate_stats_dict(capability_stats, CHINESE_TO_ENGLISH_MAPPING)

    # 整合结果
    final_stats = {
        "round": round_num,
        "meeseeks_score": meeseeks_score,
        "utility_score": utility_score,
        "capability_stats": capability_stats,
        "total_items": len(data)
    }

    # 保存结果
    stats_file = os.path.join(output_dir, f"round_{round_num}_stats.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(final_stats, f, ensure_ascii=False, indent=4)

    print(f"✅ Statistics saved to: {stats_file}")
    print(f"   - Meeseeks Score: {meeseeks_score:.4f}")
    print(f"   - Utility Score: {utility_score:.4f}")
    print(f"   - Total Items: {len(data)}")
    print(f"   - Language: {language}")

    return final_stats


if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python final_stats.py <round_file_path> <round_num> <output_dir> [language]")
        print("  language: 'chinese' (default) or 'english'")
        sys.exit(1)

    round_file_path = sys.argv[1]
    round_num = int(sys.argv[2])
    output_dir = sys.argv[3]
    language = sys.argv[4] if len(sys.argv) == 5 else 'chinese'

    calculate_and_save_stats(round_file_path, round_num, output_dir, language)
