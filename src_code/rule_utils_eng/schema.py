import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jsonschema
from utils_eng import str_to_lists, json_from_string


def model_schema(item, key, model_response):
    if key == "json_schema":
        return json_schema(item, model_response)
    elif key == "list":
        return list_schema(model_response)


def json_schema(item, model_response):
    schema = item["json_schema"]
    try:
        data = json_from_string(model_response)
        print("data: ", data)
        # 根据顶层schema决定如何处理数据
        if schema.get("type") == "array":
            # 如果schema顶层是数组，data应该直接是数组
            if isinstance(data, list):
                # 数据本身就是数组，直接使用
                pass
            else:
                # 数据不是数组，包装成数组
                data = [data]
        else:
            # 如果schema顶层是对象，检测响应是否为对象而非数组
            if not isinstance(data, list) and isinstance(data, dict):
                data = [data]


        results = []
        point_id = -1
        
        def extract_validation_points(schema, path="", parent_data=None):
            """递归提取所有需要验证的点"""
            points = []
            
            if schema.get("type") == "object":
                # 处理对象类型
                properties = schema.get("properties", {})
                required_fields = schema.get("required", [])
                
                for field_name in required_fields:
                    field_path = f"{path}.{field_name}" if path else field_name
                    field_schema = properties.get(field_name, {})
                    ability = field_schema.get("能力项", "JSON")
                    
                    # 添加当前字段的验证点
                    # 在能力项中添加JSON标签
                    final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                    points.append({
                        "path": field_path,
                        "field_name": field_name,
                        "schema": field_schema,
                        "ability": final_ability,
                        "is_required": True
                    })
                    
                    # 递归处理嵌套结构
                    if field_schema.get("type") == "object":
                        nested_points = extract_validation_points(field_schema, field_path)
                        points.extend(nested_points)
                    elif field_schema.get("type") == "array" and "items" in field_schema:
                        # 处理数组中的嵌套对象
                        items_schema = field_schema["items"]
                        if items_schema.get("type") == "object":
                            nested_points = extract_validation_points(items_schema, f"{field_path}[*]")
                            points.extend(nested_points)
                
                # 处理非必需字段，但在数组items中的所有字段都需要验证
                if path.endswith("[*]"):  # 这是数组项的schema
                    for field_name, field_schema in properties.items():
                        if field_name not in required_fields:
                            field_path = f"{path}.{field_name}" if path else field_name
                            ability = field_schema.get("能力项", "JSON")
                            final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                            
                            points.append({
                                "path": field_path,
                                "field_name": field_name,
                                "schema": field_schema,
                                "ability": final_ability,
                                "is_required": False  # 标记为非必需
                            })
            
            elif schema.get("type") == "array" and "items" in schema:
                # 处理数组类型
                items_schema = schema["items"]
                if items_schema.get("type") == "object":
                    nested_points = extract_validation_points(items_schema, f"{path}[*]" if path else "[*]")
                    points.extend(nested_points)
            
            return points


        def get_nested_value(data, path):
            """根据路径获取嵌套数据的值，区分None和不存在"""
            if not path:
                return data, True  # 返回值和是否存在的标志
            
            parts = path.split('.')
            current = data
            
            try:
                for part in parts:
                    if '[*]' in part:
                        # 处理数组情况
                        field_name = part.replace('[*]', '')
                        if field_name:
                            current = current[field_name]
                        # 返回数组，让调用者处理每个元素
                        return current, True
                    else:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            return None, False  # 字段不存在
                return current, True  # 字段存在，即使值为None
            except (KeyError, TypeError, IndexError):
                return None, False


        def validate_field(data_item, validation_point):
            """验证单个字段"""
            path = validation_point["path"]
            field_name = validation_point["field_name"]
            field_schema = validation_point["schema"]
            ability = validation_point["ability"]
            is_required = validation_point["is_required"]
            
            # 处理路径中包含数组索引的情况
            if '[*]' in path:
                # 获取数组路径和字段路径
                path_parts = path.split('[*]')
                array_path = path_parts[0]
                field_path = path_parts[1].lstrip('.')
                
                # 获取数组数据
                if array_path:
                    array_data, array_exists = get_nested_value(data_item, array_path)
                    if not array_exists:
                        return {
                            "question": f"Does {path} meet the requirements",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - Array path does not exist",
                            "能力项": ability
                        }
                else:
                    array_data = data_item
                    array_exists = True
                
                if not isinstance(array_data, list):
                    return {
                        "question": f"Does {path} meet the requirements",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - Expected array type, got {type(array_data).__name__}",
                        "能力项": ability
                    }
                
                # 统计字段在数组中的出现情况
                found_count = 0
                valid_count = 0
                error_messages = []
                
                for i, item in enumerate(array_data):
                    if field_path:
                        # 检查嵌套字段
                        nested_value, field_exists = get_nested_value(item, field_path)
                        if field_exists:  # 字段存在（即使值为None）
                            found_count += 1
                            # 验证字段值
                            try:
                                temp_schema = {
                                    "type": "object",
                                    "properties": {field_name: field_schema},
                                    "required": [field_name] if is_required else []
                                }
                                jsonschema.validate({field_name: nested_value}, temp_schema)
                                valid_count += 1
                            except jsonschema.exceptions.ValidationError as e:
                                error_messages.append(f"Item {i+1} {field_path} does not meet requirements: {e.message}")
                    else:
                        # 验证数组项本身
                        try:
                            jsonschema.validate(item, field_schema)
                            found_count += 1
                            valid_count += 1
                        except jsonschema.exceptions.ValidationError as e:
                            found_count += 1
                            error_messages.append(f"Item {i+1} does not meet requirements: {e.message}")
                
                # 判断验证结果
                if is_required and found_count == 0:
                    return {
                        "question": f"Does {path} meet the requirements",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - Required field not found in array",
                        "能力项": ability
                    }
                elif found_count > 0:
                    if valid_count == found_count:
                        return {
                            "question": f"Does {path} meet the requirements",
                            "eval_result": 1,
                            "eval_explanation": f"✅ {path} - Found {found_count} valid values in {len(array_data)} array items",
                            "能力项": ability
                        }
                    else:
                        return {
                            "question": f"Does {path} meet the requirements",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - {len(error_messages)} invalid values out of {found_count}: " + "; ".join(error_messages),
                            "能力项": ability
                        }
                else:
                    # 非必需字段且未找到
                    return {
                        "question": f"Does {path} meet the requirements",
                        "eval_result": 1,
                        "eval_explanation": f"✅ {path} - Optional field not used",
                        "能力项": ability
                    }
            else:
                # 处理普通字段路径
                field_value, field_exists = get_nested_value(data_item, path)
                
                if not field_exists and is_required:
                    return {
                        "question": f"Does {path} meet the requirements",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - Required field missing",
                        "能力项": ability
                    }
                elif field_exists:
                    # 验证字段值（即使是None也要验证）
                    try:
                        temp_schema = {
                            "type": "object",
                            "properties": {field_name: field_schema},
                            "required": [field_name] if is_required else []
                        }
                        jsonschema.validate({field_name: field_value}, temp_schema)
                        return {
                            "question": f"Does {path} meet the requirements",
                            "eval_result": 1,
                            "eval_explanation": f"✅ {path} - Meets requirements",
                            "能力项": ability
                        }
                    except jsonschema.exceptions.ValidationError as e:
                        return {
                            "question": f"Does {path} meet the requirements",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - Does not meet requirements: {e.message}",
                            "能力项": ability
                        }
                else:
                    # 字段不存在
                    return {
                        "question": f"Does {path} meet the requirements",
                        "eval_result": 1,
                        "eval_explanation": f"✅ {path} - Optional field",
                        "能力项": ability
                    }


        # 提取所有验证点
        validation_points = extract_validation_points(schema)
        
        # 对每个数据项进行验证
        if schema.get("type") == "array":
            # 顶层是数组，验证整个数组
            for validation_point in validation_points:
                result = validate_field(data, validation_point)
                result["point_id"] = point_id
                result["dep"] = []
                results.append(result)
                point_id -= 1
        else:
            # 顶层是对象，逐个验证数组中的每个对象
            for index, item_data in enumerate(data):
                for validation_point in validation_points:
                    result = validate_field(item_data, validation_point)
                    result["point_id"] = point_id
                    result["dep"] = []
                    results.append(result)
                    point_id -= 1


        return results
    
    except Exception as e:
        # 异常处理：创建所有验证点的失败结果
        results = []
        point_id = 0
        
        def extract_all_fields(schema, path=""):
            """提取所有字段用于异常情况"""
            fields = []
            if schema.get("type") == "object":
                properties = schema.get("properties", {})
                required_fields = schema.get("required", [])
                
                for field_name in required_fields:
                    field_path = f"{path}.{field_name}" if path else field_name
                    field_schema = properties.get(field_name, {})
                    ability = field_schema.get("能力项", "JSON")
                    final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                    fields.append((field_path, final_ability))
                    
                    # 递归处理嵌套
                    if field_schema.get("type") == "object":
                        nested_fields = extract_all_fields(field_schema, field_path)
                        fields.extend(nested_fields)
                    elif field_schema.get("type") == "array" and "items" in field_schema:
                        items_schema = field_schema["items"]
                        if items_schema.get("type") == "object":
                            nested_fields = extract_all_fields(items_schema, f"{field_path}[*]")
                            fields.extend(nested_fields)
                
                # 添加数组项中的非必需字段
                if path.endswith("[*]"):
                    for field_name, field_schema in properties.items():
                        if field_name not in required_fields:
                            field_path = f"{path}.{field_name}" if path else field_name
                            ability = field_schema.get("能力项", "JSON")
                            final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                            fields.append((field_path, final_ability))
            
            return fields
        
        all_fields = extract_all_fields(schema)
        
        for field_path, ability in all_fields:
            results.append({
                "point_id": point_id,
                "question": f"Does {field_path} meet the requirements",
                "dep": [],
                "eval_result": 0,
                "eval_explanation": f"❌ {field_path} - JSON parsing failed: {str(e)}",
                "能力项": ability
            })
            point_id += 1 
        
        return results
    
     
def list_schema(model_response):
    try:
        model_response = str_to_lists(model_response)
    except Exception as e:
        return 0, f"INVALID LIST: ERROR DETAILS: {str(e)}"
    return 1, "VALID LIST"
