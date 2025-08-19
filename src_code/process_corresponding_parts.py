import re
from prompts.General_Extractor_Multi import EXTRACTION_PROMPT_MULTI
from prompts.General_Extractor_Single import EXTRACTION_PROMPT_SINGLE
from prompts.Coding_Extractor import EXTRACTION_PROMPT_BY_CODING
from prompts.Coding_Extractor_Single import EXTRACTION_PROMPT_BY_CODING_SINGLE
from LLM_APIs.qwen_coder_api import call_coder_model
from LLM_APIs.qwen_api import call_model
from utils import txt_to_json, get_json_info_by_key, str_to_lists

"""
每条数据都会有一个词条叫：corresponding_parts
"""
def extract_by_coding(code_in_str, model_response):
    code_in_str = re.sub(r'```python(.*?)```', r'\1', code_in_str, flags=re.DOTALL)
    try:
        # 创建一个局部命名空间字典
        local_namespace = {}
        # 在局部命名空间中执行代码
        exec(code_in_str, globals(), local_namespace)
        # 从局部命名空间中获取 extract_info_list 函数
        extract_info_list = local_namespace['extract_info_list']
        # 调用函数并返回结果
        return extract_info_list(model_response)
    except Exception as e:
        print("invalid code: ")
        print(code_in_str)
        print(f"提取失败: {e}")
        return "INVALID"
def extract_content(data, batch_size=5):
    """
    重构的内容提取函数，修复了批处理逻辑和潜在的无限循环问题
    """
    # 初始化提取结果
    for item in data:
        if "corresponding_parts" in item:
            item["extraction_results"] = item["corresponding_parts"].copy()
    
    # 收集所有需要处理的任务
    all_tasks = []
    for data_index, item in enumerate(data):
        if "corresponding_parts" not in item:
            continue
            
        for key, extraction_prompt in item["corresponding_parts"].items():
            # 判断任务类型
            is_coding = "#CODE#" in extraction_prompt
            is_JSON = "#JSONSCHEMA#" in extraction_prompt
            is_list = "#LISTSCHEMA#" in extraction_prompt
            
            # 准备prompt
            if is_coding:
                coding_prompt = EXTRACTION_PROMPT_BY_CODING_SINGLE if "single" in item["category"] else EXTRACTION_PROMPT_BY_CODING
                prompt = coding_prompt.format(
                    model_response=item["model_response"].replace("\n", ""), 
                    instruction=extraction_prompt.replace("#CODE#", "")
                )
            elif is_JSON or is_list:
                prompt = None  # JSON和LIST类型不需要调用模型
            else:
                general_prompt = EXTRACTION_PROMPT_SINGLE if "single" in item["category"] else EXTRACTION_PROMPT_MULTI
                prompt = general_prompt.format(
                    input_instruction=item["question"],
                    model_response=item["model_response"],
                    extraction_prompt=extraction_prompt
                )
            
            all_tasks.append({
                'data_index': data_index,
                'key': key,
                'prompt': prompt,
                'extraction_prompt': extraction_prompt,
                'is_coding': is_coding,
                'is_JSON': is_JSON,
                'is_list': is_list,
                'item': item
            })
    
    print(f"Total tasks to process: {len(all_tasks)}")
    
    # 分离不同类型的任务
    coding_tasks = [task for task in all_tasks if task['is_coding']]
    normal_tasks = [task for task in all_tasks if not task['is_coding'] and not task['is_JSON'] and not task['is_list']]
    json_tasks = [task for task in all_tasks if task['is_JSON']]
    list_tasks = [task for task in all_tasks if task['is_list']]
    
    # 处理JSON任务（不需要调用模型）
    print(f"Processing {len(json_tasks)} JSON tasks...")
    for task in json_tasks:
        try:
            result = str(get_json_info_by_key(
                task['item']["model_response"], 
                task['extraction_prompt'].replace("#JSONSCHEMA#", "")
            ))
            data[task['data_index']]["extraction_results"][task['key']] = [result]
        except Exception as e:
            print(f"JSON extraction failed for task {task['key']}: {e}")
            data[task['data_index']]["extraction_results"][task['key']] = "INVALID JSON"
    
    # 处理LIST任务（不需要调用模型）
    print(f"Processing {len(list_tasks)} LIST tasks...")
    for task in list_tasks:
        try:
            # 这里需要根据你的具体逻辑来处理LIST类型
            # 假设需要调用 str_to_lists 函数
            result = str_to_lists(
                task['item']["model_response"],
                task['extraction_prompt'].replace("#LISTSCHEMA#", "")
            )
            data[task['data_index']]["extraction_results"][task['key']] = result
        except Exception as e:
            print(f"LIST extraction failed for task {task['key']}: {e}")
            data[task['data_index']]["extraction_results"][task['key']] = "INVALID LIST"
    
    # 批处理CODING任务
    if coding_tasks:
        print(f"Processing {len(coding_tasks)} coding tasks in batches of {batch_size}...")
        process_coding_tasks_in_batches(coding_tasks, data, batch_size)
    
    # 批处理普通任务
    if normal_tasks:
        print(f"Processing {len(normal_tasks)} normal tasks in batches of {batch_size}...")
        process_normal_tasks_in_batches(normal_tasks, data, batch_size)
    
    return data


def process_coding_tasks_in_batches(coding_tasks, data, batch_size):
    """批处理编程任务"""
    for i in range(0, len(coding_tasks), batch_size):
        batch_tasks = coding_tasks[i:i+batch_size]
        batch_prompts = [task['prompt'] for task in batch_tasks]
        
        print(f"  Processing coding batch {i//batch_size + 1}/{(len(coding_tasks)-1)//batch_size + 1} ({len(batch_tasks)} tasks)")
        
        try:
            # 批量调用
            batch_results = call_coder_model(batch_prompts)
            
            # 处理结果
            for j, (result, task) in enumerate(zip(batch_results, batch_tasks)):
                try:
                    extracted_result = extract_by_coding(result, task['item']["model_response"])
                    data[task['data_index']]["extraction_results"][task['key']] = extracted_result
                    data[task['data_index']].setdefault("extraction_code", {})[task['key']] = result
                except Exception as e:
                    print(f"    Coding extraction failed for task {task['key']}: {e}")
                    data[task['data_index']]["extraction_results"][task['key']] = "INVALID"
                    
        except Exception as e:
            print(f"  Batch coding call failed: {e}")
            # 回退到逐个处理
            print("  Falling back to individual processing...")
            for task in batch_tasks:
                try:
                    result = call_coder_model([task['prompt']])[0]
                    extracted_result = extract_by_coding(result, task['item']["model_response"])
                    data[task['data_index']]["extraction_results"][task['key']] = extracted_result
                except Exception as e:
                    print(f"    Individual coding extraction failed for task {task['key']}: {e}")
                    data[task['data_index']]["extraction_results"][task['key']] = "INVALID"


def process_normal_tasks_in_batches(normal_tasks, data, batch_size):
    """批处理普通任务"""
    for i in range(0, len(normal_tasks), batch_size):
        batch_tasks = normal_tasks[i:i+batch_size]
        batch_prompts = [task['prompt'] for task in batch_tasks]
        
        print(f"  Processing normal batch {i//batch_size + 1}/{(len(normal_tasks)-1)//batch_size + 1} ({len(batch_tasks)} tasks)")
        
        try:
            # 批量调用
            batch_results = call_coder_model(batch_prompts)
            
            # 处理结果
            for result, task in zip(batch_results, batch_tasks):
                try:
                    # 转换为JSON格式
                    json_result = txt_to_json(result)
                    
                    if json_result == "ALL":
                        final_result = task['item']["model_response"]
                    else:
                        final_result = json_result
                        
                    data[task['data_index']]["extraction_results"][task['key']] = final_result
                    
                except Exception as e:
                    print(f"    Normal extraction failed for task {task['key']}: {e}")
                    print(f"    Raw result: {result}")
                    data[task['data_index']]["extraction_results"][task['key']] = "INVALID"
                    
        except Exception as e:
            print(f"  Batch normal call failed: {e}")
            # 回退到逐个处理
            print("  Falling back to individual processing...")
            for task in batch_tasks:
                try:
                    result = call_coder_model([task['prompt']])[0]
                    json_result = txt_to_json(result)
                    
                    if json_result == "ALL":
                        final_result = task['item']["model_response"]
                    else:
                        final_result = json_result
                        
                    data[task['data_index']]["extraction_results"][task['key']] = final_result
                    
                except Exception as e:
                    print(f"    Individual normal extraction failed for task {task['key']}: {e}")
                    data[task['data_index']]["extraction_results"][task['key']] = "INVALID"
                    
# def extract_content(data, batch_size=BATCH_SIZE):
#     for item in data:
#         if "corresponding_parts" in item:
#             item["extraction_results"] = item["corresponding_parts"].copy()
            
#     index = 0
#     while index < len(data):
#         print(f"Processing item {index + 1} of {len(data)}")
#         prompt_list = []
#         index_key_pairs = []
#         is_coding_list = []  # 记录每个prompt是否是coding类型
#         is_JSON_list = []
#         is_list_list = []
#         current_batch_size = 0
        
#         while index < len(data) and current_batch_size + len(data[index].get("corresponding_parts", {})) <= batch_size:
#             if "corresponding_parts" not in data[index]:
#                 index += 1
#                 continue   
#             general_prompt = EXTRACTION_PROMPT_SINGLE if "single" in data[index]["category"] else EXTRACTION_PROMPT_MULTI
#             coding_prompt = EXTRACTION_PROMPT_BY_CODING_SINGLE if "single" in data[index]["category"] else EXTRACTION_PROMPT_BY_CODING
            
#             for key, extraction_prompt in data[index]["corresponding_parts"].items():
#                 is_coding = "#CODE#" in extraction_prompt
#                 is_JSON = "#JSONSCHEMA#" in extraction_prompt
#                 is_list = "#LISTSCHEMA#" in extraction_prompt

#                 # print(extraction_prompt, is_coding)
#                 if is_coding:
#                     extract_task = coding_prompt.format(
#                         model_response=data[index]["model_response"].replace("\n", ""), 
#                         instruction=extraction_prompt.replace("#CODE#", "")
#                     )
#                 elif is_JSON:
#                     extract_task = "pass"
#                 elif is_list:
#                     extract_task = "pass"
#                 else:
#                     extract_task = general_prompt.format(
#                         input_instruction=data[index]["question"],
#                         model_response=data[index]["model_response"],
#                         extraction_prompt=extraction_prompt
#                     )
#                 prompt_list.append(extract_task)
#                 index_key_pairs.append((index, key))
#                 is_coding_list.append(is_coding)
#                 is_list_list.append(is_list)
#                 is_JSON_list.append(is_JSON)
#                 current_batch_size += 1
                
#             index += 1
        
#         # 确保我们有prompt要处理
#         if prompt_list:
#             # 分离coding和非coding的prompt
#             coding_prompts = [p for i, p in enumerate(prompt_list) if is_coding_list[i]]
#             coding_pairs = [pair for i, pair in enumerate(index_key_pairs) if is_coding_list[i]]

#             list_prompts = [p for i, p in enumerate(prompt_list) if is_list_list[i]]
#             list_pairs = [pair for i, pair in enumerate(index_key_pairs) if is_list_list[i]]

#             JSON_prompts = [p for i, p in enumerate(prompt_list) if is_JSON_list[i]]
#             JSON_pairs = [pair for i, pair in enumerate(index_key_pairs) if is_JSON_list[i]]
            
#             normal_prompts = [p for i, p in enumerate(prompt_list) if not is_coding_list[i] and not is_JSON_list[i] and not is_list_list[i]]
#             normal_pairs = [pair for i, pair in enumerate(index_key_pairs) if not is_coding_list[i] and not is_JSON_list[i] and not is_list_list[i]]
            
#             # 处理coding prompts
#             if coding_prompts:
#                 coding_results = []
#                 # 先尝试batch处理
#                 try:
#                     batch_results = call_coder_model(coding_prompts)
#                     batch_results = [
#                         extract_by_coding(coding, data[data_index]["model_response"]) 
#                         for coding, (data_index, _) in zip(batch_results, coding_pairs)
#                     ]
#                     coding_results = batch_results
#                 except Exception as e:
#                     print(f"Batch coding extraction failed: {e}")
#                     # 只对batch处理失败的部分进行individual processing
#                     for i, (prompt, (data_index, _)) in enumerate(zip(coding_prompts, coding_pairs)):
#                         if i >= len(coding_results): # 只处理还没有结果的部分
#                             try:
#                                 result = call_coder_model([prompt])[0]
#                                 coding_results.append(result)
#                             except Exception as e:
#                                 print(f"Individual coding extraction failed: {e}")
#                                 coding_results.append(None)
#             for i, (data_index, prompt_key) in enumerate(coding_pairs):
#                     data[data_index]["extraction_results"][prompt_key] = coding_results[i]
            
#             # 处理普通prompts
#             if normal_prompts:
#                 normal_results = call_coder_model(normal_prompts)
#                 # 将普通结果插回data
#                 for i, (data_index, prompt_key) in enumerate(normal_pairs):
#                     try:
#                         normal_results[i] = txt_to_json(normal_results[i])
#                     except Exception as e:
#                         print(f"Individual normal extraction failed (txt to json): {e}")
#                         print(normal_results[i])
#                         normal_results[i] = "INVALID"
#                     if normal_results[i] == "ALL":
#                         data[data_index]["extraction_results"][prompt_key] = data[data_index]["model_response"]
#                     else:
#                         data[data_index]["extraction_results"][prompt_key] = normal_results[i]
            
#             # 处理JSON prompt，JSON prompt不需要call model来获取copart，直接从JSON内提取即可
#             if JSON_prompts:
#                 for i, (data_index, prompt_key) in enumerate(JSON_pairs):
#                     try: 
#                         data[data_index]["extraction_results"][prompt_key] = [str(get_json_info_by_key(data[data_index]["model_response"], data[data_index]["extraction_results"][prompt_key]))]
#                     except Exception as e:
#                         data[data_index]["extraction_results"][prompt_key] = "INVALID JSON"
#     return data
