#!/usr/bin/env python3
"""
API connection testing script
Used for debugging API connection issues
"""

import requests
import json

def test_api_connection(url, test_prompt="Hello, how are you?"):
    """Test API connection"""
    print(f"🔗 Testing API: {url}")
    print(f"📝 Test prompt: {test_prompt}")
    print("-" * 50)

    payload = {
        "prompt": test_prompt,
        "max_new_tokens": 100,
        "temperature": 0.00,
        "top_k": 1
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("📤 Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        print(f"📝 Raw response text: {response.text}")
        print()

        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"✅ JSON parsing successful")
                print(f"📋 Response structure: {json.dumps(response_json, indent=2, ensure_ascii=False)}")

                if 'completions' in response_json:
                    print(f"✅ Found 'completions' key")
                    completions = response_json['completions']
                    if completions and len(completions) > 0:
                        print(f"✅ Found {len(completions)} completion(s)")
                        for i, completion in enumerate(completions):
                            if 'text' in completion:
                                print(f"✅ Completion {i+1} has 'text' key: {completion['text'][:100]}...")
                            else:
                                print(f"❌ Completion {i+1} missing 'text' key")
                    else:
                        print(f"❌ No completions found")
                else:
                    print(f"❌ Missing 'completions' key in response")

            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")

        else:
            print(f"❌ HTTP error: {response.status_code}")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print("=" * 60)

def main():
    """Main function"""
    print("🧪 API Connection Testing Tool")
    print("=" * 60)

    # Test default API URLs
    test_urls = [
        "http://10.164.51.197:8080",  # Qwen API
        "http://10.166.176.56:8080",  # Qwen Coder API
    ]

    for url in test_urls:
        test_api_connection(url)
        print()

    # Interactive testing
    while True:
        print("🔧 Interactive Testing Mode")
        custom_url = input("Enter API URL to test (or press Enter to exit): ").strip()
        if not custom_url:
            break

        custom_prompt = input("Enter test prompt (or press Enter for default): ").strip()
        if not custom_prompt:
            custom_prompt = "Hello, how are you?"

        test_api_connection(custom_url, custom_prompt)
        print()

if __name__ == "__main__":
    main()
