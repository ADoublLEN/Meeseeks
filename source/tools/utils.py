import json
import re
import ast
from math import inf
from typing import Any, List

BATCH_SIZE = 100

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8')  as file:
        data = json.load(file)
    return data

def txt_to_json(text):
    json_content = re.search(r'\[.*\]', text, re.DOTALL).group()
    return ast.literal_eval(json_content)

def str_to_lists(text):
    pattern = r'\["(.*?)"\]'
    # 使用正则表达式查找所有匹配内容
    result_list = re.findall(pattern, text, re.DOTALL)
    return result_list

def extract_and_load_json(text):
    # 使用正则表达式提取```json到```之间的内容
    pattern = r'```json(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    
    if not match:
        pattern = r'```(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
    
    if match:
        json_content = match.group(1).strip()
    else:
        json_content = text
    # 使用json.loads解析提取的内容
    json_data = json.loads(json_content)
    return json_data

def txt_to_json_braces(text):
    # json_str = extract_json(text)
    # return ast.literal_eval(json_str)
    return extract_and_load_json(text)

def get_json_info_by_key(model_response, prompt):
    key = prompt.split(":")[1]
    processed_model_response = txt_to_json_braces(model_response)
    if isinstance(processed_model_response, list):
        return txt_to_json_braces(model_response)[0][key]
    return txt_to_json_braces(model_response)[key]

def remove_invalid_characters(data):
    if isinstance(data, dict):
        return {key: remove_invalid_characters(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_invalid_characters(element) for element in data]
    elif isinstance(data, str):
        return data.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    else:
        return data

def clean_up_text(text):
    # 先删除所有空格
    text = text.replace(" ", "")

    text_after_index = remove_index(text)
        
    # 清理文本，移除非字母数字字符
    cleaned_text = re.sub(r'[^\w]', '', text_after_index)
    return cleaned_text

def remove_index(text):
    # 定义各种索引模式
    patterns = [
        r'^\d+\.',          # 12.
        r'^\d+\s*',          # 12 
        r'^\d+\)',          # 12)
        r'^\d+\]',          # 12]
        r'^\d+\}',          # 12}
        r'^\d+、',          # 12、
        r'^\d+\s',          # 12 
        r'^[a-zA-Z]\.',     # a.
        r'^[a-zA-Z]\)',     # a)
        r'^[a-zA-Z]\]',     # a]
        r'^[a-zA-Z]\}',     # a}
        r'^[a-zA-Z]、',     # a、
        r'^[a-zA-Z]\s',     # a 
        r'^[ivxIVX]+\.',    # iv.
        r'^[ivxIVX]+\)',    # iv)
        r'^[ivxIVX]+\]',    # iv]
        r'^[ivxIVX]+\}',    # iv}
        r'^[ivxIVX]+、',    # iv、
        r'^[ivxIVX]+\s',    # iv 
        r'^\(\d+\)',        # (12)
        r'^\([a-zA-Z]\)',   # (a)
        r'^\[[a-zA-Z]\]',   # [a]
        r'^\[\d+\]',        # [12]
        r'^\{[a-zA-Z]\}',   # {a}
        r'^\{\d+\}',        # {12}
    ]
    
    # 合并所有模式
    combined_pattern = '|'.join(patterns)
    
    # 删除匹配到的索引
    result = re.sub(combined_pattern, '', text)
    
    # 删除开头的空白字符
    result = result.lstrip()
    
    return result

def json_parse(json_string: str, keep_undefined: bool = True) -> Any:
    """
    解析JSON字符串，处理特殊值如Infinity、NaN和undefined
    
    Args:
        json_string: 要解析的JSON字符串
        keep_undefined: 是否保留undefined值作为字符串，否则转为None
        
    Returns:
        解析后的Python对象
    """
    def parse_handler(obj):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):  # 使用list()创建副本以便在迭代中修改字典
                if isinstance(v, str):
                    if v == '{{Infinity}}':
                        obj[k] = float('inf')
                    elif v == '{{-Infinity}}':
                        obj[k] = float('-inf')
                    elif v == '{{NaN}}':
                        obj[k] = float('nan')
                    elif v == '{{undefined}}':
                        obj[k] = None if not keep_undefined else v
                    elif re.match(r'^{{"{{(Infinity|NaN|-Infinity|undefined)}}"}}$', v):
                        obj[k] = re.sub(r'^{{"{{(Infinity|NaN|-Infinity|undefined)}}"}}$', r'{{\1}}', v)
        return obj

    # 预处理JSON字符串，处理特殊值
    processed = json_string
    
    # 处理带引号的特殊值
    processed = re.sub(
        r'":\s*"{{(Infinity|NaN|-Infinity|undefined)}}"([,}\n])',
        r':"{{\"{{\\1}}\"}}"\\2',
        processed
    )
    
    # 处理不带引号的特殊值
    processed = re.sub(
        r'":\s*(Infinity|NaN|-Infinity|undefined)([,}\n])',
        r':"{{\\1}}"\\2',
        processed
    )

    try:
        # 尝试解析JSON
        result = json.loads(processed, object_hook=parse_handler)
        return result
    except json.JSONDecodeError:
        # 如果解析失败，尝试清理JSON字符串后再解析
        # 移除可能导致解析错误的控制字符
        cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', processed)
        return json.loads(cleaned, object_hook=parse_handler)


def json_from_string(text: str) -> List[Any]:
    """
    从字符串中提取和解析JSON数据。
    尝试多种方法：
    1. 使用ast.literal_eval解析
    2. 直接使用json_parse
    3. 使用正则表达式提取JSON片段再解析
    
    Args:
        text: 包含JSON数据的字符串
        
    Returns:
        解析出的JSON对象列表
    """
    # 方法1: 尝试使用ast.literal_eval解析
    try:
        python_obj = ast.literal_eval(text)
        if python_obj:
            return [python_obj]
    except Exception:
        pass
    
    # 方法2: 尝试直接使用json_parse
    try:
        parsed = json_parse(text, True)
        if parsed:
            return [parsed]
    except Exception:
        pass
    
    # 方法3: 使用正则表达式提取JSON片段
    matches = []
    
    # 尝试提取完整的JSON对象或数组
    json_patterns = [
        # 标准JSON对象模式
        r'(\{(?:[^{}]|(?:\{[^{}]*\}))*\})',
        # 标准JSON数组模式
        r'(\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\])'
    ]
    
    for pattern in json_patterns:
        for match in re.finditer(pattern, text, re.DOTALL):
            json_str = match.group(0)
            try:
                parsed_obj = json_parse(json_str, True)
                if parsed_obj:  # 确保解析结果不为空
                    matches.append(parsed_obj)
            except Exception:
                # 如果单个片段解析失败，忽略该片段
                continue
    
    # 如果找到了匹配项，返回结果
    if matches:
        return matches
    
    # 如果所有方法都失败，返回ERROR
    raise Exception("Failed to parse JSON from string")



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