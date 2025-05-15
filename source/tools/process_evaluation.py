

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


