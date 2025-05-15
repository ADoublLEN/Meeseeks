EXTRACTION_PROMPT_BY_CODING_SINGLE = """

你是一个Python数据处理专家，你会被输入【model_response】和【抓取对象】，请根据【抓取对象】编写Python代码来去除【model_response】中的非【抓取对象】信息。

Step 1. 寻找并去除头尾部非【抓取对象】信息
请你检查model_response中是否存在头部或者尾部非【抓取对象】信息，如果不存在则不需要执行此操作；如果存在，请使用re.sub方法去除model_response中不需要的头尾部非【抓取对象】信息，以确保输出仅包含【抓取对象】的指定内容。

Step2. 寻找并去除中间非【抓取对象】信息
请你检查model_response中是否存在嵌套在中间的非【抓取对象】信息，如果存在，请用replace方法去除。

以下是常见的非【抓取对象】信息：
“以下是满分作文：”，“以上是所有内容，希望你满意”

Step 3. 输出数据
以Python list的形式输出model_response中，去除非【抓取对象】信息后的数据。

#输出格式#：
假设你已经有"model_response"了：
你的code格式必须严格参照如下：确保你的函数名为extract_info_list。你的return结果应该是一个list。请只输出函数：extract_info_list(model_response)
详细格式：
def extract_info_list(model_response):
    # 1. 先检查头部和尾部是否存在非【抓取对象】信息，假如不存在，请直接跳过这步。
    # 假如【xxxxx】是头部非【抓取对象】信息，【yyyyy】为尾部非【抓取对象】信息，则用sub删除【xxxxx】和【yyyyy】
    # 比如: cleaned_text = re.sub(r'^.*xxxxx|yyyyy.*$', '', model_response, flags=re.DOTALL)

    # 2. 若非【抓取对象】信息嵌套于【抓取对象】信息内部，用replace方法去除非【抓取对象】信息
    # 如果非【抓取对象】信息是zzzzzz，按照以下方法去除，model_response = model_response.replace("zzzzzz", "")

    # 很多情况下，实际上不存在任何非【抓取对象】信息，可以不执行Step1和Step2，直接赋值model_response到cleaned_text
    # 比如: cleaned_text = model_response

    # 3. 以python list的格式输出删除额外信息后的数据
    return [cleaned_text]

**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**

---example1---
【model_response】
评价学生作文：优点：1. 立意明确：文章紧扣材料主题，强调了合作与共享的重要性，并以此为核心展开论述。2. 结构清晰：文章由引言部分过渡到正文，再到结尾，层次分明，逻辑清楚。3. 语言流畅：文章使用了一些修辞手法，如比喻和排比，使得文章富有文采。4. 范围广泛：作者从国家、商业、个人三个层面进行了阐述，使得文章内容丰富，角度多元。缺点：1. 创新性不足：文章虽然结构完整，但缺乏独到的见解和深入的思考，内容略显平庸。2. 实例不够具体：虽然提到了国家合作、企业合作和个人分享，但未给出具体的例子，使得论证不够有力。3. 情感表达略显薄弱：文章较为理性分析，但情感渲染不足，缺少对主题深刻感悟的表达。综合评分：根据上述分析，该篇作文内容完整，结构清晰，但在创新性和论证力度上略显不足。如果满分为60分，我会给这篇文章大约45分。它是一篇结构良好的文章，但需要更多的独到见解和具体例证来提升分数。尝试写一份满分高考作文：【标题】光芒万丈，因你而灿烂【正文】在一片广袤的花海中，每一朵花都以其独特的姿态绽放，共同谱写着春天的华章。正如习近平总书记所言，一个人的光辉，或许能够照亮一隅，但只有众星捧月，方能照亮整个夜空。在人类的历史长河中，那些试图独占鳌头、孤芳自赏的行为，终究是昙花一现。历史的车轮滚滚向前，是由那些懂得合作与共享的人推动的。他们明白，吹灭别人的灯，不仅无助于照亮自己的道路，反而会让世界更加阴暗。

【抓取对象】
正文内容

【extract function】
**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
def extract_info_list(model_response):
    # 因为要抓取的对象为正文内容，因此：抓取“【正文】”后的内容即可
    cleaned_text = re.sub(r'^.*【正文】', '', model_response, flags=re.DOTALL)
    return [cleaned_text]

---example2---
【model_response】
由于篇幅较长，以下是一份简化版的调研报告大纲，可供您根据需要进一步扩展：---# 调研报告：普通用户面临的系统垃圾问题及解决方案## 摘要本报告针对普通用户在日常使用计算机和移动设备过程中遇到的系统垃圾问题进行调研。旨在了解用户在何种场景下遇到系统垃圾问题，探讨简单有效的清理方法，并评估开发一款傻瓜式清理软件的可行性。## 引言系统垃圾问题是指计算机和移动设备在使用过程中产生的临时文件、缓存、无用程序和文件碎片等。这些垃圾占用存储空间，影响设备性能，甚至可能导致隐私泄露。普通用户往往缺乏专业知识来有效管理这些系统垃圾。## 调研方法- 网络问卷：针对普通用户发放问卷，收集数据。。---请注意，这只是一个简化版的报告大纲。实际的调研报告需要根据调研数据和分析得出的具体内容进行撰写，包括详细的方法论、数据分析、用户反馈以及软件设计方案等，以达到3000字的要求。

【抓取对象】
整个调研报告大纲。
        
【extract function】
**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
def extract_info_list(model_response):
    # 因为要抓取的对象为整个调研报告大纲。因此：抓取“【# 调研报告：】”后，到“【。---请注意】”中间的内容即可。
    cleaned_text = re.sub(r'^.*# 调研报告：|。---请注意.*$', '', model_response, flags=re.DOTALL)
    return [cleaned_text]

---your turn---
【model_response】
{model_response}

【抓取对象】
{instruction}

【extract function】
**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
"""
