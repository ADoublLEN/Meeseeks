import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jsonschema
from utils import str_to_lists, json_from_string


def model_schema(item, key, model_response):
    if key == "json_schema":
        return json_schema(item, model_response)
    elif key == "list":
        return list_schema(model_response)


def json_schema(item, model_response):
    schema = item["json_schema"]
    try:
        data = json_from_string(model_response)
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
            """Recursively extract all validation points"""
            points = []
            
            if schema.get("type") == "object":
                # Handle object type
                properties = schema.get("properties", {})
                required_fields = schema.get("required", [])
                
                # 处理所有字段（必需和非必需）
                all_fields = set(required_fields)
                if path.endswith("[*]"):  # 在数组项中，所有字段都需要验证
                    all_fields.update(properties.keys())

                for field_name in all_fields:
                    field_path = f"{path}.{field_name}" if path else field_name
                    field_schema = properties.get(field_name, {})
                    ability = field_schema.get("能力项", "JSON")
                    
                    # Add validation point for current field
                    # Add JSON tag to ability
                    final_ability = f"{ability}、JSON" if ability != "JSON" else "JSON"
                    points.append({
                        "path": field_path,
                        "field_name": field_name,
                        "schema": field_schema,
                        "ability": final_ability,
                        "is_required": field_name in required_fields
                    })
                    
                    # Recursively handle nested structures
                    if field_schema.get("type") == "object":
                        nested_points = extract_validation_points(field_schema, field_path)
                        points.extend(nested_points)
                    elif field_schema.get("type") == "array" and "items" in field_schema:
                        # Handle nested objects in arrays
                        items_schema = field_schema["items"]
                        if items_schema.get("type") == "object":
                            nested_points = extract_validation_points(items_schema, f"{field_path}[*]")
                            points.extend(nested_points)
                
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
                        "question": f"Does {path} meet requirements",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - Array path does not exist",
                            "能力项": ability
                        }
                else:
                    array_data = data_item
                    array_exists = True
                
                if not isinstance(array_data, list):
                    return {
                        "question": f"Does {path} meet requirements",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - Expected array type, actual type is {type(array_data).__name__}",
                        "能力项": ability
                    }
                
                # Count field occurrences in array
                found_count = 0
                valid_count = 0
                error_messages = []
                
                for i, item in enumerate(array_data):
                    if field_path:
                        # Check nested fields
                        nested_value, field_exists = get_nested_value(item, field_path)
                        if field_exists:  # Field exists (even if value is None)
                            found_count += 1
                            # Validate field value
                            try:
                                temp_schema = {
                                    "type": "object",
                                    "properties": {field_name: field_schema},
                                    "required": [field_name] if is_required else []
                                }
                                jsonschema.validate({field_name: nested_value}, temp_schema)
                                valid_count += 1
                            except jsonschema.exceptions.ValidationError as e:
                                error_messages.append(f"Item {i+1} {field_path} does not meet rules: {e.message}")
                    else:
                        # Validate array item itself
                        try:
                            jsonschema.validate(item, field_schema)
                            found_count += 1
                            valid_count += 1
                        except jsonschema.exceptions.ValidationError as e:
                            found_count += 1
                            error_messages.append(f"Item {i+1} does not meet rules: {e.message}")
                
                # Determine validation result
                if is_required and found_count == 0:
                    return {
                        "question": f"Does {path} meet requirements",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - Required field not found in array",
                        "能力项": ability
                    }
                elif found_count > 0:
                    if valid_count == found_count:
                        return {
                            "question": f"Does {path} meet requirements",
                            "eval_result": 1,
                            "eval_explanation": f"✅ {path} - Found {found_count} valid values in {len(array_data)} array items",
                            "能力项": ability
                        }
                    else:
                        return {
                            "question": f"Does {path} meet requirements",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - {len(error_messages)} invalid out of {found_count} values: " + "; ".join(error_messages),
                            "能力项": ability
                        }
                else:
                    # Non-required field and not found
                    return {
                        "question": f"Does {path} meet requirements",
                        "eval_result": 1,
                        "eval_explanation": f"✅ {path} - Optional field not used",
                        "能力项": ability
                    }
            else:
                # Handle regular field path
                field_value, field_exists = get_nested_value(data_item, path)
                
                if not field_exists and is_required:
                    return {
                        "question": f"Does {path} meet requirements",
                        "eval_result": 0,
                        "eval_explanation": f"❌ {path} - Required field missing",
                        "能力项": ability
                    }
                elif field_exists:
                    # Validate field value (even if None)
                    try:
                        temp_schema = {
                            "type": "object",
                            "properties": {field_name: field_schema},
                            "required": [field_name] if is_required else []
                        }
                        jsonschema.validate({field_name: field_value}, temp_schema)
                        return {
                            "question": f"Does {path} meet requirements",
                            "eval_result": 1,
                            "eval_explanation": f"✅ {path} - Meets rules",
                            "能力项": ability
                        }
                    except jsonschema.exceptions.ValidationError as e:
                        return {
                            "question": f"Does {path} meet requirements",
                            "eval_result": 0,
                            "eval_explanation": f"❌ {path} - Does not meet rules: {e.message}",
                            "能力项": ability
                        }
                else:
                    # Field does not exist
                    return {
                        "question": f"Does {path} meet requirements",
                        "eval_result": 1,
                        "eval_explanation": f"✅ {path} - Optional field",
                        "能力项": ability
                    }


        # Extract all validation points
        validation_points = extract_validation_points(schema)
        
        # Validate each data item
        if schema.get("type") == "array":
            # Top level is array, validate entire array
            for validation_point in validation_points:
                result = validate_field(data, validation_point)
                result["point_id"] = point_id
                result["dep"] = []
                results.append(result)
                point_id -= 1
        else:
            # Top level is object, validate each object in array individually
            for index, item_data in enumerate(data):
                for validation_point in validation_points:
                    result = validate_field(item_data, validation_point)
                    result["point_id"] = point_id
                    result["dep"] = []
                    results.append(result)
                    point_id -= 1


        return results
    
    except Exception as e:
        # Exception handling: create failure results for all validation points
        results = []
        point_id = 0
        
        def extract_all_fields(schema, path=""):
            """Extract all fields for exception cases"""
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
                    
                    # Recursively handle nesting
                    if field_schema.get("type") == "object":
                        nested_fields = extract_all_fields(field_schema, field_path)
                        fields.extend(nested_fields)
                    elif field_schema.get("type") == "array" and "items" in field_schema:
                        items_schema = field_schema["items"]
                        if items_schema.get("type") == "object":
                            nested_fields = extract_all_fields(items_schema, f"{field_path}[*]")
                            fields.extend(nested_fields)
                
                # Add non-required fields in array items
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
                "question": f"Does {field_path} meet requirements",
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



if __name__ == '__main__':
    item =   {
        "category": "SCHEMA",
        "question": "You are a senior travel expert and professional article analyst. I will provide you with an article that recommends suitable travel destinations. Your task is to analyze this article and extract information from it by attraction name dimension.\n\n1. poiName: Extract the names of attractions mentioned in the article. Attractions must be location-level geographical positions, absolutely not cities or provinces. For example: botanical gardens, parks, ancient towns, scenic areas, museums, temples and other specific attractions (such as Taiyuan Botanical Garden, Jingshan Park, Gubei Water Town).\n\nOutput requirements:\n1. Return extracted information in JSON format\n2. Each attraction as a separate object, containing poiName field\n3. All attraction objects form an array\n4. Do not return any characters other than JSON format\nYou need to identify the type of each attraction (such as park, ancient town, museum, temple, theme park, scenic area, etc.), and return the poiType field in json.\nYou need to identify whether each attraction is suitable for parent-child play (return \"Yes\" if suitable, otherwise return \"No\"), and return the isParentChildFriendly field in json.\nYou need to identify whether each attraction has night view (return \"Yes\" if it has night view, otherwise return \"No\"), and return the hasNightView field in json.\nOutput format example:\n[\n  {\"poiName\": \"example value\", \"poiType\": \"example type\", \"isParentChildFriendly\": \"Yes/No\", \"hasNightView\": \"Yes/No\"}\n]\n\nArticle content:Beijing surrounding tour recommendations:\n1. Taiyuan Botanical Garden is the largest botanical garden in North China, suitable for parent-child tours\n2. Jingshan Park overlooks the panoramic view of the Forbidden City\n3. The night view of Gubei Water Town is stunning, recommend staying in the scenic area",
        "json_schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "poiName",
                    "poiType",
                    "isParentChildFriendly",
                    "hasNightView"
                ],
                "properties": {
                    "poiName": {
                        "type": "string",
                        "description": "Attraction name, must be a specific location-level geographical position",
                        "能力项": "JSON"
                    },
                    "poiType": {
                        "type": "string",
                        "description": "Attraction type, such as park, ancient town, museum, temple, theme park, scenic area, etc.",
                        "能力项": "JSON"
                    },
                    "isParentChildFriendly": {
                        "type": "string",
                        "enum": [
                            "Yes",
                            "No"
                        ],
                        "description": "Whether it is suitable for parent-child",
                        "能力项": "特定格式"
                    },
                    "hasNightView": {
                        "type": "string",
                        "enum": [
                            "Yes",
                            "No"
                        ],
                        "description": "Whether it has night view",
                        "能力项": "特定格式"
                    }
                },
                "additionalProperties": False
            }
        },
        "sub_questions": [
            {
                "question": "是否满足json_schema",
                "rule": "schema:json_schema",
                "能力项": "JSON",
                "point_id": -1,
                "dep": []
            }
        ],
        "model_response": "```json\n[\n  {\"poiName\": \"Taiyuan Botanical Garden\", \"poiType\": \"botanical garden\", \"isParentChildFriendly\": \"Yes\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Jingshan Park\", \"poiType\": \"park\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Gubei Water Town\", \"poiType\": \"ancient town\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"Yes\"}\n]\n```"
    }

    model_response = "```json\n[\n  {\"poiName\": \"Taiyuan Botanical Garden\", \"poiType\": \"botanical garden\", \"isParentChildFriendly\": \"Yes\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Jingshan Park\", \"poiType\": \"park\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"No\"},\n  {\"poiName\": \"Gubei Water Town\", \"poiType\": \"ancient town\", \"isParentChildFriendly\": \"No\", \"hasNightView\": \"Yes\"}\n]\n```"

    print(json_schema(item, model_response))
