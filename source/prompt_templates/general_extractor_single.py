EXTRACTION_PROMPT_SINGLE = """
你是一个信息抽取专家。以下将会给你提供一个【输入指令】和对应的【模型回复】。此外，还会给你提供一个【抓取对象】，设计该问题的目的是评测【模型回复】是否满足【输入指令】的某个要求。现在，你需要抽取出【模型回复】中，【抓取对象】针对的评测对象。

**注意：你应该完全复制【模型回复】中连续的原文片段，严禁做任何修改、增添、删除、拼接，只能进行复制。即使其不符合【抓取对象】要求。你不需要关注【抓取对象】的具体要求是什么，更不需要评测【模型回复】是否满足【抓取对象】要求。**

你的目的是删除那些额外生成的辅助阅读的信息，比如“以下是我提供的信息：”，“非常好的问题！”
已知评分对象在【模型回复】中只存在一个，请你用python list的格式进行格式化并输出。

如果评分对象为整段文字，输出ALL。尽量输出ALL来减少输出token的数量

**请只输出一个是valid python list的评测对象或ALL，不要输出任何其他备注或任何其他内容！**

---example1---
【输入指令】
市场运营一段话定性表述整体情况：讲清楚取得了什么样的关键业绩结果，既要有定量的分析，也要有定性的总结，避免陷入数据的堆砌，却无法说明数据背后的意义，200字总结

【模型回复】
在本季度，市场运营团队通过创新的营销活动和精准的市场定位策略，成功推动了用户增长率达到了18%，并且提升了品牌知名度和市场份额。定量上，我们通过数据分析，确保了营销投入与回报率的最优化，同时，用户活跃度和参与度的提升也直接反映了市场运营的有效性。定性上，我们的市场运营不仅增强了用户对品牌的认同感，还通过社交媒体和线上互动提高了用户参与度，增强了品牌与消费者之间的互动和情感联系。这些成果不只是数字上的增长，更代表了我们在理解和满足消费者需求、构建长期品牌价值方面迈出的坚实步伐。

【抓取对象】
请你按照python list的格式，抓取模型回复中，定性表述整体情况的部分

**请只输出一个是valid python list的评测对象或ALL，不要输出任何其他备注或任何其他内容！**
【评测对象】
ALL

---example2---
【输入指令】
高考的作文题目是：\n吹灭别人的灯，并不会让自己更加光明；阻挡别人的路，也不会让自己行得更远。\n“一花独放不是春，百花齐放春满园。”如果世界上只有一种花朵，就算这种花朵再美，那也是单调的。\n以上两则材料出自习近平总书记的讲话，以生动形象的语言说出了普遍的道理。请据此写一篇文章，体现你的认识与思考。\n要求：选准角度，确定立意，明确文体，自拟标题；不要套作，不得抄袭；不得泄露个人信息；不少于800字。\n\n下面是某学生根据题目写的散文：\n众芳摇落独暄妍——共同发展的力量\n\n世界如同一座花园，花朵们各自绽放，散发出独特的芬芳。然而，若只有一种花朵独自绽放，即使再美，也难以让人感受到春天的气息。唯有百花齐放，春天才能真正充盈。\n\n习近平总书记的这句话，如同一股清风，吹散了人们心中的嫉妒与阻挡。它告诉我们，吹灭别人的灯，并不会让自己更加光明；阻挡别人的路，也不会让自己行得更远。相反，只有通过合作与共享，我们才能激发出无限的力量，实现共同发展。\n\n合作与共享的力量在人类社会中无处不在。国家之间的合作与交流，为全球的繁荣与发展提供了源源不断的动力。当各国携手合作，分享经验和资源，共同应对全球挑战时，我们才能够共同创造和平与繁荣的未来。正如习近平总书记所说：“一花独放不是春，百花齐放春满园。”只有通过合作，我们才能共同构建一个和谐、稳定的世界。\n\n在商业领域，企业之间的合作与共享也是推动发展的重要力量。当企业愿意携手合作，共同研发创新产品，共享市场资源，互利共赢时，我们才能够实现更大的成功。合作不仅能够提高企业的竞争力，也能够促进整个行业的发展。正是因为有了合作与共享的精神，我们才能够在激烈的市场竞争中取得更大的突破。\n\n在个人层面，合作与共享同样具有重要意义。每个人都有自己的优势和长处，当我们愿意与他人合作，互相学习、互相促进时，我们才能够实现个人的成长与进步。同时，分享的精神也是人类社会进步的推动力。只有愿意分享自己的知识、经验和资源，我们才能够共同进步，共同繁荣。\n\n在这个充满竞争与合作的世界里，我们应该明白，吹灭别人的灯，并不会让自己更加光明；阻挡别人的路，也不会让自己行得更远。唯有通过合作与共享，我们才能够激发出无限的力量，实现共同发展。让我们携起手来，摒弃嫉妒和阻挡的心态，以合作与共享的精神，共同推动社会的进步和发展。无论是在国家层面、企业层面还是个人层面，只有通过合作，我们才能够实现共同发展、共同繁荣。让我们共同努力，共同追求，为实现人类社会的进步与发展贡献自己的力量。\n\n\n评价一下优缺点，满分60分的话能得多少分？并尝试写一份满分高考作文

【模型回复】
评价学生作文：优点：1. 立意明确：文章紧扣材料主题，强调了合作与共享的重要性，并以此为核心展开论述。2. 结构清晰：文章由引言部分过渡到正文，再到结尾，层次分明，逻辑清楚。3. 语言流畅：文章使用了一些修辞手法，如比喻和排比，使得文章富有文采。4. 范围广泛：作者从国家、商业、个人三个层面进行了阐述，使得文章内容丰富，角度多元。缺点：1. 创新性不足：文章虽然结构完整，但缺乏独到的见解和深入的思考，内容略显平庸。2. 实例不够具体：虽然提到了国家合作、企业合作和个人分享，但未给出具体的例子，使得论证不够有力。3. 情感表达略显薄弱：文章较为理性分析，但情感渲染不足，缺少对主题深刻感悟的表达。综合评分：根据上述分析，该篇作文内容完整，结构清晰，但在创新性和论证力度上略显不足。如果满分为60分，我会给这篇文章大约45分。它是一篇结构良好的文章，但需要更多的独到见解和具体例证来提升分数。尝试写一份满分高考作文：【标题】光芒万丈，因你而灿烂【正文】在一片广袤的花海中，每一朵花都以其独特的姿态绽放，共同谱写着春天的华章。正如习近平总书记所言，一个人的光辉，或许能够照亮一隅，但只有众星捧月，方能照亮整个夜空。在人类的历史长河中，那些试图独占鳌头、孤芳自赏的行为，终究是昙花一现。历史的车轮滚滚向前，是由那些懂得合作与共享的人推动的。他们明白，吹灭别人的灯，不仅无助于照亮自己的道路，反而会让世界更加阴暗。在国与国的交往中，我们见证了合作的力量。当我们回望丝绸之路，那不仅是商品的交换，更是文化的融合、智慧的互鉴。

【抓取对象】
请你按照python list的格式，抓取模型回复中，给出的满分作文示例部分。

**请只输出一个是valid python list的评测对象或ALL，不要输出任何其他备注或任何其他内容！**
【评测对象】
["【标题】光芒万丈，因你而灿烂【正文】在一片广袤的花海中，每一朵花都以其独特的姿态绽放，共同谱写着春天的华章。正如习近平总书记所言，一个人的光辉，或许能够照亮一隅，但只有众星捧月，方能照亮整个夜空。在人类的历史长河中，那些试图独占鳌头、孤芳自赏的行为，终究是昙花一现。历史的车轮滚滚向前，是由那些懂得合作与共享的人推动的。他们明白，吹灭别人的灯，不仅无助于照亮自己的道路，反而会让世界更加阴暗。在国与国的交往中，我们见证了合作的力量。当我们回望丝绸之路，那不仅是商品的交换，更是文化的融合、智慧的互鉴。"]

---example3---
【输入指令】
清理系统垃圾问题一直困扰着普通用户，我想针对这个问题写一份调研报告，主要是想了解普通用户在什么场景下会遇到这个问题；对于他们来说，简单的清理方法是什么；还想有没有可能设计一款傻瓜软件惠及大众。帮我写一份这样的调研报告，字数在3000字以内。

【模型回复】
由于篇幅较长，以下是一份简化版的调研报告大纲，可供您根据需要进一步扩展：---# 调研报告：普通用户面临的系统垃圾问题及解决方案## 摘要本报告针对普通用户在日常使用计算机和移动设备过程中遇到的系统垃圾问题进行调研。旨在了解用户在何种场景下遇到系统垃圾问题，探讨简单有效的清理方法，并评估开发一款傻瓜式清理软件的可行性。## 引言系统垃圾问题是指计算机和移动设备在使用过程中产生的临时文件、缓存、无用程序和文件碎片等。这些垃圾占用存储空间，影响设备性能，甚至可能导致隐私泄露。普通用户往往缺乏专业知识来有效管理这些系统垃圾。## 调研方法- 网络问卷：针对普通用户发放问卷，收集数据。- 深度访谈：选取部分用户进行深度访谈，了解具体使用场景。- 市场分析：调研现有清理工具的市场情况。## 用户遇到系统垃圾的场景- 软件安装与卸载：安装程序时产生的临时文件，卸载后残留的配置信息。- 浏览网页：浏览器缓存和Cookie等。- 系统更新：旧系统文件未能清理干净。- 日常使用：文档编辑、应用使用过程中产生的临时文件。## 用户对清理方法的需求用户普遍希望有一种简单直观的清理方法，例如：- 一键清理功能，自动扫描并清理垃圾。- 定期提醒清理，帮助用户养成良好习惯。---请注意，这只是一个简化版的报告大纲。实际的调研报告需要根据调研数据和分析得出的具体内容进行撰写，包括详细的方法论、数据分析、用户反馈以及软件设计方案等，以达到3000字的要求。

【抓取对象】
请你按照python list的格式，抓取模型回复中，给出的整篇报告。

**请只输出一个是valid python list的评测对象或ALL，不要输出任何其他备注或任何其他内容！** 
【评测对象】
["调研报告：普通用户面临的系统垃圾问题及解决方案## 摘要本报告针对普通用户在日常使用计算机和移动设备过程中遇到的系统垃圾问题进行调研。旨在了解用户在何种场景下遇到系统垃圾问题，探讨简单有效的清理方法，并评估开发一款傻瓜式清理软件的可行性。## 引言系统垃圾问题是指计算机和移动设备在使用过程中产生的临时文件、缓存、无用程序和文件碎片等。这些垃圾占用存储空间，影响设备性能，甚至可能导致隐私泄露。普通用户往往缺乏专业知识来有效管理这些系统垃圾。## 调研方法- 网络问卷：针对普通用户发放问卷，收集数据。- 深度访谈：选取部分用户进行深度访谈，了解具体使用场景。- 市场分析：调研现有清理工具的市场情况。## 用户遇到系统垃圾的场景- 软件安装与卸载：安装程序时产生的临时文件，卸载后残留的配置信息。- 浏览网页：浏览器缓存和Cookie等。- 系统更新：旧系统文件未能清理干净。- 日常使用：文档编辑、应用使用过程中产生的临时文件。## 用户对清理方法的需求用户普遍希望有一种简单直观的清理方法，例如：- 一键清理功能，自动扫描并清理垃圾。- 定期提醒清理，帮助用户养成良好习惯。"]

---your turn---
【输入指令】
{input_instruction}

【模型回复】
{model_response}

【抓取对象】
{extraction_prompt}

**请只输出一个是valid python list的评测对象或ALL，不要输出任何其他备注或任何其他内容！**
【评测对象】
"""

