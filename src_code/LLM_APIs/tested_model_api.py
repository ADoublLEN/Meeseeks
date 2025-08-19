import requests

# 全局变量存储URL
_tested_model_url = None

def set_tested_model_url(url):
    """设置被测模型API的URL"""
    global _tested_model_url
    _tested_model_url = url

def call_tested_model(prompt):
    """调用被测模型API"""
    if _tested_model_url is None:
        raise ValueError("Tested model URL not set. Please call set_tested_model_url() first.")

    payload = {
        "prompt": prompt,
        "max_new_tokens": 8096,
        "temperature": 0.00,
        "top_k": 1
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # print(f"🔗 Calling API: {_tested_model_url}")
        # print(f"📝 Payload: {payload}")

        response = requests.request("POST", _tested_model_url, headers=headers, json=payload, timeout=1800)

        # print(f"📊 Response status: {response.status_code}")
        # print(f"📄 Response headers: {dict(response.headers)}")
        # print(f"📝 Raw response text: {response.text[:500]}...")  # 只显示前500个字符

        # 检查HTTP状态码
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        # 检查响应是否为空
        if not response.text.strip():
            raise Exception("Empty response from API")

        # 尝试解析JSON
        response_json = response.json()

        # 检查响应格式
        if 'completions' not in response_json:
            raise Exception(f"Invalid response format. Expected 'completions' key. Got: {response_json}")

        return [item['text'] for item in response_json['completions']]

    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except ValueError as e:
        raise Exception(f"JSON parsing error: {e}. Response text: {response.text}")
    except Exception as e:
        raise Exception(f"API call failed: {e}")
