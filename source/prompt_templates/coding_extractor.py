EXTRACTION_PROMPT_BY_CODING = """
你是一个Python数据处理专家，负责根据不同的需求编写Python代码来提取并格式化model_response中的信息。

Step 1. 根据instruction去除头部和尾部额外备注
请你检查model_response中是否存在头部或者尾部额外备注，如果不存在则不需要执行此操作；如果存在，请使用re.sub方法去除model_response中不需要的头部尾部额外备注，以确保输出仅包含instruction的指定内容。头部和尾部的额外备注使用re.sub去除。

Step2. 根据instruction去除中间的额外备注
请你检查model_response中是否存在嵌套在中间的额外备注，如果存在，请用replace方法去除。

以下是常见的额外备注：
【以下是评论：】【以上是所有内容】【（注：由于篇幅限制，这里只提供了40条评论示例。）】【对不起，以上内容可能存在重复，请忽略重复内容】

Step 3. 数据分割
你需要根据instruction使用re.findall分割数据，使用适当的分割方法（如按索引、空格、标点符号等）以确保每个信息片段是独立的。你需要保证提取部分完整，例如：model_response="1. 这个建议真的很好\n。2. 非常赞同这种观点。\n"，应当提取全部信息，包括index和内容，而不是只提取index或内容。理想结果为：["1. 这个建议真的很好","2. 非常赞同这种观点"]，因此，务必不要出现dishes = re.findall(r'\d+\. \*\*(.*?)\*\*', model_response)的代码，应该用dishes = re.findall(r'(\d+\.\s*.*?)(?=\d+\.|$)', model_response, re.DOTALL)来囊括包括index的内容作为输出。

#输出格式#：
假设你已经有"model_response"了：
你的code格式必须严格参照如下：确保你的函数名为extract_info_list。你的return结果应该是一个list。请只输出函数：extract_info_list(model_response)，不要输出任何其他信息。

def extract_info_list(model_response):
    # 1. 先检查头部和尾部是否存在额外备注，假如不存在，请直接跳过这步。假如【xxxxx】是头部额外备注，【yyyyy】为尾部额外备注，则用sub删除【xxxxx】和【yyyyy】
    # 比如: cleaned_text = re.sub(r'^.*xxxxx|yyyyy.*$', '', model_response, flags=re.DOTALL)

    # 2. 若存在一些非instruction所需要的中间嵌套额外备注【zzzzzz】，用replace方法去除
    # 比如: model_response = model_response.replace("zzzzzz", "")

    # 若不存在任何额外信息，可以不执行Step1和Step2，直接赋值model_response到cleaned_text
    # 比如: cleaned_text = model_response

    if cleaned_text:
        # 3. 根据模型回答的格式来匹配到的范围内使用正则表达式提取评论，抓取包括index在内的所有内容，如果原文存在index，则必须抓取相应的index：例如：comments = re.findall(r'(\d+\.\s*.*?)(?=\d+\.|$)', cleaned_text, re.DOTALL)
        # 请你填充这部分代码
        # ...
    return []

**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
---example1---
#model_response#:
以下是评论：1. 这个建议真的棒极了2. 这个观点我超级赞同（我认为这条其实不是特别好）3. 说的真有道理，值得深思4. 这个必须给个大大的赞5. 建议很棒，希望能被采纳6. 这个观点我百分百同意7. 你说的太对了，我也这么觉得8. 这个点子赞爆了，点个赞9. 这个观点很有深度，赞一个，以上是所有内容，如果你有任何不满，请继续和我的对话。

#instruction#
请去除非评论内容的信息或备注后，按照python list的形式，将model_response中的评论输出，请分割输出。

**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
#extract function#:
def extract_info_list(model_response):
    # 1. 检测到头部备注为【以下是评论：】，sub使用 "^.*是评论：" 去除头部备注；尾部额外备注为【，以上是所有内容，如果你有任何不满，请继续和我的对话。】，sub使用 "|，以上.*$" 去除尾部备注。只使用头部备注后的几个字符和尾部备注前几个字符来确保正则没有问题。
    cleaned_text = re.sub(r'^.*是评论：|，以上.*$', '', model_response, flags=re.DOTALL)

    # 2. 【（我认为这条其实不是特别好）】不属于评论内容，是额外的备注，使用replace去除
    cleaned_text = cleaned_text.replace("（我认为这条其实不是特别好）", "")

    if cleaned_text:
        # 3. 检测到model_response中存在index，则使用正则表达式提取index+评论内容
        comments = re.findall(r'(\d+\.\s*.*?)(?=\d+\.|$)', cleaned_text, re.DOTALL)
        return comments
    return []

---example2---
#model_response#:
1. 视频里的环境看上去非常舒适，老年人一定会喜欢这样的地方。 以上是所有评论

#instruction#
请去除非评论内容的信息或备注后，按照python list的形式，将model_response中的评论输出，请分割输出。

**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
#extract function#:
def extract_info_list(model_response):
    # 1. 检测到头部备注不存在；检测到头部备注为【 以上是所有评论】，sub使用"| 以上.*$"去除尾部备注。sub内只使用尾部备注前的几个字符来确保正则没有问题。
    cleaned_text = re.sub(r'| 以上.*$', '', model_response, flags=re.DOTALL)
    if cleaned_text:
        # 3. 检测到model_response中存在index，则使用正则表达式提取index+评论内容
        comments = re.findall(r'(\d+\.\s*.*?)(?=\d+\.|$)', cleaned_text, re.DOTALL)
        return comments
    return []


---example3---
#model_response#:
以下是一条评论：1. 视频里的环境看上去非常舒适，老年人一定会喜欢这样的地方。 

#instruction#
请去除非评论内容的信息或备注后，按照python list的形式，将model_response中的评论输出，请分割输出。

**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
#extract function#:
def extract_info_list(model_response):
    # 1. 检测到尾部备注不存在；检测到头部备注为【以下是一条评论：】，sub使用"^.*评论："去除头部备注。不抽取完整的头部额外备注，以保证正则没有问题。只使用头部备注后的几个字符来确保正则没有问题。
    cleaned_text = re.sub(r'^.*评论：', '', model_response, flags=re.DOTALL)
    if cleaned_text:
        # 3. 检测到model_response中存在index，则使用正则表达式提取index+评论内容
        comments = re.findall(r'(\d+\.\s*.*?)(?=\d+\.|$)', cleaned_text, re.DOTALL)
        return comments
    return []

---example4---
#model_response#:
牛肉烤鸭子、猪肉炖鲤鱼、鸡肉炸虾仁、羊肉焖豆腐、鱼肉蒸南瓜

#instruction#
请你用去除非名字的所有信息后，分割并输出所有模型生成的名字

**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
#extract function#:
def extract_info_list(model_response):
    # 检查不到任何头部、尾部或中间的额外备注，直接使用原始文本
    cleaned_text = model_response
    if cleaned_text:
        # 使用逗号分割所有菜品名称
        dishes = re.findall(r'[^、]+', cleaned_text)
        # 去除可能存在的空白字符
        dishes = [dish.strip() for dish in dishes]
        return dishes
    return []

---your turn---
#model_response#:
{model_response}

#instruction#
{instruction}

**请务必注意：请只输出函数：extract_info_list(model_response)，只输出代码！不要输出任何其他内容！**
#extract function#:
"""