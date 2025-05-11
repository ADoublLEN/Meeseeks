import re
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