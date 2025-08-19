import re
from prompts.General_Evaluator import EVALUATION_PROMPT
from LLM_APIs.qwen_api import call_model

# 查看依赖项
def check_dependencies(sub_question, item):
    for sub_q in item["sub_questions"]:
        if sub_q["point_id"] in sub_question["dep"]:
            if sub_q["eval_result"] == 0:
                return False
    return True

def model_evaluation(sub_questions):
    # try:
        # 为每个sub_question准备prompt
    prompts = [EVALUATION_PROMPT.format(
        input=sub_q['_item']["question"],
        output=sub_q['_item']["model_response"],
        question=sub_q["question"]
    ) for sub_q in sub_questions]
    
    # 批量调用模型
    raw_results = call_model(prompts)
    
    # 处理每个结果
    for sub_question, raw_res in zip(sub_questions, raw_results):
        try:
            re_result = re.findall(r'判断：是|判断：否', raw_res)
            if "是" in re_result[0]:
                sub_question["eval_result"] = 1
            else:
                sub_question["eval_result"] = 0
            sub_question["eval_explanation"] = raw_res
        except Exception as e:
            sub_question["eval_result"] = 0
            sub_question["eval_explanation"] = str(e)
        sub_question["eval_method"] = "pure model evaluation"
            
    return sub_questions

def get_mixed_evaluation(sub_questions, rule_based_evaluate_func):
    """使用传入的rule_based_evaluate函数进行评估"""
    for sub_q in sub_questions:
        item = sub_q["_item"]
        if sub_q['rule'].startswith("SCHEMA"):
            # SCHEMA规则返回多个验证点的列表，直接赋值给eval_result
            sub_q["eval_result"] = rule_based_evaluate_func(
                item, 
                sub_q["rule"], 
                item["model_response"]
            )
            sub_q["eval_method"] = "rule evaluation"
        else:
            corresponding_part = item["extraction_results"][sub_q["corresponding_part"]]
            if corresponding_part == "INVALID":  # 抓取的部分有问题这样
                sub_q["eval_result"] = 0
                sub_q['eval_explanation'] = "MODEL ERROR"
            else:
                # print(sub_q["question"], sub_q["rule"], corresponding_part)
                sub_q["eval_result"], sub_q['eval_explanation'] = rule_based_evaluate_func(
                    item, 
                    sub_q["rule"], 
                    corresponding_part
                )
                    
            sub_q["eval_method"] = "rule evaluation"
    return sub_questions

def get_dependency_level(questions_dict, sub_q):
    """获取问题的依赖层级"""
    if not sub_q["dep"]:
        return 0
    
    max_dep_level = 0
    for dep_id in sub_q["dep"]:
        # 找到这个依赖对应的问题
        for q in questions_dict[id(sub_q["_item"])]:
            if q["point_id"] == dep_id:
                dep_level = get_dependency_level(questions_dict, q)
                max_dep_level = max(max_dep_level, dep_level)
    
    return max_dep_level + 1

def collect_questions_by_level(items):
    """按依赖层级收集问题"""
    # 使用id()作为键来建立映射
    # print(items)
    questions_dict = {id(item): item["sub_questions"] for item in items}
    
    # 为每个问题添加所属的item引用并确定其层级
    questions_by_level = {}
    total_questions = 0
    
    for item in items:
        for sub_q in item["sub_questions"]:
            total_questions += 1
            sub_q["_item"] = item
            level = get_dependency_level(questions_dict, sub_q)
            if level not in questions_by_level:
                questions_by_level[level] = []
            questions_by_level[level].append(sub_q)
    
    print(f"Total questions: {total_questions}")
    for level in sorted(questions_by_level.keys()):
        print(f"Level {level} questions: {len(questions_by_level[level])}")
    
    return questions_by_level

def process_all_items(items, batch_size=5, rule_based_evaluate_func=None):
    print(f"Starting to process {len(items)} items...")
    questions_by_level = collect_questions_by_level(items)
    max_level = max(questions_by_level.keys())
    
    # 保存原始的item引用关系
    original_items = {id(item): item for item in items}
    
    # 按层级处理问题
    for level in range(max_level + 1):
        print(f"\nProcessing level {level} questions...")
        level_questions = questions_by_level[level]
        processed_count = 0
        
        # 处理当前层级的问题
        for i in range(0, len(level_questions), batch_size):
            batch = level_questions[i:i+batch_size]
            valid_batch = []
            
            # 检查依赖
            for sub_q in batch:
                if level == 0 or check_dependencies(sub_q, sub_q["_item"]):
                    valid_batch.append(sub_q)
                else:
                    sub_q["eval_result"] = 0
                    sub_q["eval_explanation"] = "Dependencies failed"
                    sub_q["eval_method"] = "dependency check"
                    processed_count += 1
                    print(f"Question marked as failed due to dependencies")
            
            # 处理有效的批次
            if valid_batch:
                non_rule_batch = [sub_q for sub_q in valid_batch if sub_q.get("rule") is None]
                rule_batch = [sub_q for sub_q in valid_batch if sub_q.get("rule") is not None]
                if rule_batch:
                    get_mixed_evaluation(rule_batch, rule_based_evaluate_func)
                if non_rule_batch:
                    model_evaluation(non_rule_batch)
            processed_count += len(valid_batch)
            print(f"Processed {processed_count}/{len(level_questions)} level {level} questions")
        
        # 在处理完当前层后，更新剩余层级的item引用
        if level < max_level:
            for next_level in range(level + 1, max_level + 1):
                for sub_q in questions_by_level[next_level]:
                    # 使用原始items重新设置_item引用
                    item_id = id(sub_q["_item"])
                    sub_q["_item"] = original_items[item_id]
    
    # 最后清理所有临时添加的item引用
    for item in items:
        for sub_q in item["sub_questions"]:
            if "_item" in sub_q:
                del sub_q["_item"]
            # 关键：SCHEMA规则的特殊处理，直接用eval_result替换sub_questions
            if sub_q.get("rule") == "SCHEMA:json_schema" and isinstance(sub_q.get("eval_result"), list):
                item["sub_questions"] = sub_q["eval_result"] + item["sub_questions"][1:]

    print("\nProcessing completed!")

    return items
