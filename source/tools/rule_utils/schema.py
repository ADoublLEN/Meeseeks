import subprocess
import sys

try:
    import jsonschema
except ImportError:
    # 使用pip安装pinyin
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema"])
    # 再次导入pinyin
    import jsonschema

from ..utils import txt_to_json_braces, txt_to_json, str_to_lists, json_from_string
from jsonschema import validate, ValidationError, Draft7Validator

def model_schema(item, key, model_response):
    if key == "json_schema":
        return json_schema(item, model_response)
        
    elif key == "list":
        return list_schema(model_response)

def json_schema(item, model_response):
    schema = item["json_schema"]
    try:
        data = json_from_string(model_response)[0]
        # 检测响应是否为对象而非数组，如果是对象则包装成数组统一处理
        if not isinstance(data, list) and isinstance(data, dict):
            data = [data]

        results = []
        point_id = -1
        
        # 确定schema类型
        is_object_schema = schema.get("type") == "object"
        
        # 获取必需字段列表
        required_fields = schema.get("required", []) if is_object_schema else schema.get("items", {}).get("required", [])
        
        # 获取属性定义
        properties = schema.get("properties", {}) if is_object_schema else schema.get("items", {}).get("properties", {})

        for index, item_data in enumerate(data):
            # 检查所有必需字段
            for field_name in required_fields:
                # 检查字段是否存在
                if field_name not in item_data:
                    explanation = f"❌ {field_name} - 必需字段缺失"
                    ability = "JSON"
                    results.append({
                        "point_id": point_id,
                        "question": f"{field_name}是否符合要求",
                        "dep": [0],
                        "eval_result": 0,
                        "eval_explanation": explanation,
                        "能力项": ability
                    })
                    point_id -= 1
                    continue
                
                # 字段存在，检查是否有规则定义
                if field_name in properties:
                    field_schema = properties[field_name]
                    ability = field_schema.get("能力项", "JSON")
                    
                    try:
                        # 创建临时schema验证字段值
                        temp_schema = {
                            "type": "object",
                            "properties": {
                                field_name: field_schema
                            },
                            "required": [field_name]
                        }
                        jsonschema.validate({field_name: item_data[field_name]}, temp_schema)
                        explanation = f"✅ {field_name} - 符合规则"
                        eval_result = 1
                    except jsonschema.exceptions.ValidationError as e:
                        explanation = f"❌ {field_name} - 不符合规则: {e.message}"
                        eval_result = 0
                else:
                    # 字段没有规则定义，但因为存在所以符合要求
                    explanation = f"✅ {field_name} - 必需字段存在"
                    ability = "JSON"
                    eval_result = 1
                
                results.append({
                    "point_id": point_id,
                    "question": f"{field_name}是否符合要求",
                    "dep": [],
                    "eval_result": eval_result,
                    "eval_explanation": explanation,
                    "能力项": ability
                })
                point_id -= 1
        return results
    except Exception as e:
        ## ALL to be 0
        results = []
        point_id = 0
        
        # 确定schema类型（对象或数组）
        is_object_schema = schema.get("type") == "object"
        
        # 根据schema类型获取必需字段
        required_fields = schema.get("required", []) if is_object_schema else schema.get("items", {}).get("required", [])
        
        # 获取属性定义位置
        properties = schema.get("properties", {}) if is_object_schema else schema.get("items", {}).get("properties", {})
        
        # 为每个必需字段创建一个失败的结果
        for field_name in required_fields:
            # 确定能力项
            ability = "JSON"
            if field_name in properties and "能力项" in properties[field_name]:
                ability = properties[field_name]["能力项"]
            
            results.append({
                "point_id": point_id,
                "question": f"{field_name}是否符合要求",
                "dep": [],
                "eval_result": 0,
                "eval_explanation": f"❌ {field_name} - JSON解析失败: {str(e)}",
                "能力项": ability
            })
            point_id += 1 
        
        return results  # 提前返回所有失败结果

 
def list_schema(model_response):
    try:
        model_response = str_to_lists(model_response)
    except Exception as e:
        return 0, f"INVALID LIST: ERROR DETAILS: {str(e)}"
    return 1, "VALID LIST"


