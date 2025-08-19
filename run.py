#!/usr/bin/env python3
"""
OG_meeseeks项目的主运行文件
替代evaluate.py的逻辑，支持参数化配置
"""

import sys
import subprocess
import os

def install_requirements():
    """自动安装requirements.txt中的依赖包"""
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')

    if os.path.exists(requirements_file):
        print("🔧 Checking and installing dependencies...")
        try:
            # 读取requirements.txt
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.readlines()

            # 过滤掉注释和空行
            packages = []
            for line in requirements:
                line = line.strip()
                if line and not line.startswith('#'):
                    packages.append(line)

            if packages:
                print(f"📦 Found {len(packages)} dependencies to check...")
                for package in packages:
                    print(f"   - {package}")

                # 安装依赖
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", requirements_file
                ])
                print("✅ All dependencies installed successfully!")
            else:
                print("📦 No dependencies found to install")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            print("Please run manually: pip install -r requirements.txt")
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
    else:
        print("⚠️  requirements.txt file not found")

def fix_json_data(data):
    new_data = []
    for item in data:
        flag = 1 if iferror(item) else 0
        if "json_schema" in item or "SCHEMA" in item:
            og_subqs = [
                {
                    "point_id": 0,
                    "question": "Does it meet schema requirements",
                    "rule": "SCHEMA:json_schema",
                    "eval_result": flag,
                    "dep": [],
                    "被依赖": False,
                    "能力项": "JSON"
                }]
            for subq in item["sub_questions"]:
                if subq["point_id"] > 0:
                    og_subqs.append(subq)
            item["sub_questions"] = og_subqs
        new_data.append(item)

    return new_data

# 在导入其他模块之前先安装依赖
if __name__ == "__main__":
    install_requirements()

import json
import time
import argparse
import requests
import sys
import os

# 添加src_code目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src_code'))

from process_corresponding_parts import extract_content
from process_evaluation import process_all_items
from multi_round_template_added import multi_round_template_added
from LLM_APIs.qwen_api import set_qwen_url
from LLM_APIs.qwen_coder_api import set_qwen_coder_url
from LLM_APIs.tested_model_api import set_tested_model_url, call_tested_model
from final_stats import calculate_and_save_stats


def get_language_modules(language):
    """根据语言参数动态导入相应的模块"""
    if language == 'english':
        # 导入英文版本的模块
        from process_rule_based_evaluate_eng import rule_based_evaluate
        return rule_based_evaluate
    else:
        # 默认使用中文版本的模块
        from process_rule_based_evaluate import rule_based_evaluate
        return rule_based_evaluate


def test_single_api(url, api_name, test_prompt="Hello"):
    """测试单个API是否可用"""
    print(f"🔗 Testing {api_name}: {url}")

    payload = {
        "prompt": test_prompt,
        "max_new_tokens": 50,
        "temperature": 0.00,
        "top_k": 1
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=1800)

        if response.status_code == 200:
            try:
                response_json = response.json()
                if 'completions' in response_json and response_json['completions']:
                    print(f"✅ {api_name} is working")
                    return True
                else:
                    print(f"❌ {api_name} returned invalid format")
                    return False
            except json.JSONDecodeError:
                print(f"❌ {api_name} returned non-JSON response")
                return False
        else:
            print(f"❌ {api_name} returned HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ {api_name} connection failed")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {api_name} timeout")
        return False
    except Exception as e:
        print(f"❌ {api_name} error: {e}")
        return False


def test_all_apis(qwen_url, qwen_coder_url, tested_model_url):
    """测试所有三个API是否可用"""
    print("🧪 Testing API connections...")
    print("=" * 50)

    results = {}
    results['qwen'] = test_single_api(qwen_url, "Qwen API")
    results['qwen_coder'] = test_single_api(qwen_coder_url, "Qwen Coder API")
    results['tested_model'] = test_single_api(tested_model_url, "Tested Model API")

    print("=" * 50)

    all_working = all(results.values())
    if all_working:
        print("✅ All APIs are working properly!")
        return True
    else:
        print("❌ Some APIs are not working:")
        for api_name, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {api_name}: {'Working' if status else 'Failed'}")

        print("\n💡 Please check:")
        print("   - API services are running")
        print("   - URLs are correct")
        print("   - Network connectivity")
        print("   - Firewall settings")

        user_input = input("\n❓ Continue anyway? (y/N): ").strip().lower()
        return user_input in ['y', 'yes']


def process_in_batches(data, batch_size=100):
    """批量处理数据，调用被测模型获取响应"""
    total_items = len(data)
    for batch_start in range(0, total_items, batch_size):
        batch_end = min(batch_start + batch_size, total_items)
        current_batch = data[batch_start:batch_end]

        # Print processing progress
        print(f"📊 Processing items {batch_start}-{batch_end-1} out of {total_items} total items...")

        try:
            # Batch get questions and call model
            batch_questions = [item["question"] for item in current_batch]
            batch_responses = call_tested_model(batch_questions)  # 使用被测模型

            # Assign responses back to data items
            for item, response in zip(current_batch, batch_responses):
                item["model_response"] = response

        except Exception as e:
            print(f"❌ Error occurred while processing batch {batch_start}-{batch_end-1}: {str(e)}")
            # Add retry logic or error handling here


def iferror(item):
    """检查是否有评估错误"""
    for subq in item["sub_questions"]:
        if subq["eval_result"] == 0:
            return True
    return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OG_meeseeks评估系统')
    parser.add_argument('--qwen_url', required=True, help='Qwen API的URL')
    parser.add_argument('--qwen_coder_url', required=True, help='Qwen Coder API的URL')
    parser.add_argument('--tested_model_url', required=True, help='被测模型API的URL')
    parser.add_argument('--batch_size', type=int, default=100, help='批处理大小')
    parser.add_argument('--rounds', type=int, default=2, help='评估轮数')
    parser.add_argument('--output_dir', default='evaluation_results', help='输出目录')

    # 创建互斥组：language 和 data_path 只能选择一个
    data_group = parser.add_mutually_exclusive_group(required=True)
    data_group.add_argument('--language', choices=['chinese', 'english'],
                           help='选择语言数据集：chinese 或 english')
    data_group.add_argument('--data_path', help='自定义数据文件路径')



    args = parser.parse_args()

    # 设置API URLs
    set_qwen_url(args.qwen_url)
    set_qwen_coder_url(args.qwen_coder_url)
    set_tested_model_url(args.tested_model_url)

    # 测试API连接
    if not test_all_apis(args.qwen_url, args.qwen_coder_url, args.tested_model_url):
        print("🛑 API test failed, program exiting")
        return

    print()  # 添加空行分隔

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 处理数据路径
    if args.language:
        # 根据语言参数确定数据目录
        if args.language == 'chinese':
            data_dir = os.path.join(os.path.dirname(__file__), 'input_data', 'chinese_data', 'raw_input')
        else:  # english
            data_dir = os.path.join(os.path.dirname(__file__), 'input_data', 'english_data', 'raw_input')

        print(f"📂 Loading {args.language} data from directory: {data_dir}")

        # 获取目录中所有JSON文件
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        if not json_files:
            print(f"❌ No JSON files found in {data_dir}")
            return

        print(f"📄 Found {len(json_files)} JSON files:")
        for file in json_files:
            print(f"   - {file}")

        # 合并所有JSON文件的数据
        current_data = []
        for json_file in json_files:
            file_path = os.path.join(data_dir, json_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    if isinstance(file_data, list):
                        current_data.extend(file_data)
                    else:
                        current_data.append(file_data)
                print(f"✅ Loaded {json_file}")
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
    else:
        # 使用自定义数据路径
        print(f"📂 Loading data from: {args.data_path}")
        with open(args.data_path, "r", encoding="utf-8") as f:
            current_data = json.load(f)

    # 保存原始问题
    for item in current_data:
        item["og_question"] = item["question"]

    print(f"📊 Loaded {len(current_data)} items")
    print(f"🔧 Configuration:")
    print(f"   - Qwen URL: {args.qwen_url}")
    print(f"   - Qwen Coder URL: {args.qwen_coder_url}")
    print(f"   - Tested Model URL: {args.tested_model_url}")
    print(f"   - Batch Size: {args.batch_size}")
    print(f"   - Rounds: {args.rounds}")
    if args.language:
        print(f"   - Language: {args.language}")
        print(f"   - Data Directory: {data_dir}")
    else:
        print(f"   - Data Path: {args.data_path}")
    print(f"   - Output Directory: {args.output_dir}")
    print("=" * 80)

    # 根据语言参数获取相应的评估函数
    rule_based_evaluate_func = get_language_modules(args.language if args.language else 'chinese')
    print(f"🔧🔧🔧 Using {'English' if args.language == 'english' else 'Chinese'} evaluation modules")

    # 多轮评估
    all_data = current_data.copy()  # 保存所有数据的副本

    for round_num in range(args.rounds):
        print(f"🚀 Starting Round {round_num + 1} Evaluation")
        print("=" * 60)

        # 第一轮之后，只对有错误的项目重新评估，但保留所有数据
        if round_num != 0:
            # 找出需要重新评估的项目（从all_data中查找）
            items_to_reevaluate = [item for item in all_data if iferror(item)]
            if not items_to_reevaluate:
                print("✅ No items to re-evaluate in this round. All evaluations passed!")
                # 仍然保存完整结果
                output_file = os.path.join(args.output_dir, f"round_{round_num + 1}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=4)
                print(f"💾 Complete results saved to: {output_file}")
                break

            # 对需要重新评估的项目应用多轮模板
            items_to_reevaluate = multi_round_template_added(items_to_reevaluate)
            items_to_reevaluate = fix_json_data(items_to_reevaluate)
            print(f"📊 Re-evaluating {len(items_to_reevaluate)} items with errors from previous round")

            # 设置当前处理的数据为需要重新评估的项目
            current_data = items_to_reevaluate
        else:
            print(f"📊 Processing {len(current_data)} items in first round")

        if not current_data:
            print("✅ No items to process in this round!")
            break

        # 处理model_response收集
        print("📝 Getting model responses for evaluation...")
        process_in_batches(current_data, args.batch_size)

        # 开始评估
        og_start_time = time.time()
        print(f"🔄 Round {round_num + 1} Processing Started")

        # 步骤1：提取对应部分
        start_time = time.time()
        print("🔍 Step 1: Extracting corresponding parts from all responses...")
        current_data = extract_content(current_data, args.batch_size)
        print("✅ Corresponding parts extraction completed successfully")
        end_time = time.time()
        print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
        print()

        # 步骤2：处理和评估
        start_time = time.time()
        print("🔍 Step 2: Processing and evaluating all items...")
        current_data = process_all_items(current_data, args.batch_size, rule_based_evaluate_func)
        print("✅ Item processing and evaluation completed successfully")
        end_time = time.time()
        print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
        print()

        total_time = end_time - og_start_time
        print("=" * 60)
        print(f"🎉 Round {round_num + 1} Completed Successfully!")
        print(f"⏱️  Total round time: {total_time:.2f} seconds")
        print("=" * 60)

        # 保存结果
        if round_num == 0:
            # 第一轮：更新all_data为当前评估结果
            all_data = current_data.copy()
            output_file = os.path.join(args.output_dir, f"round_{round_num + 1}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            print(f"💾 Results saved to: {output_file}")
        else:
            # 后续轮次：合并结果，用重新评估的结果更新对应项目
            # 使用原始问题作为唯一标识符来匹配项目
            reevaluated_items = {item.get('og_question', item.get('question', '')): item for item in current_data}

            # 更新all_data中对应的项目
            for i, item in enumerate(all_data):
                item_key = item.get('og_question', item.get('question', ''))
                if item_key in reevaluated_items:
                    all_data[i] = reevaluated_items[item_key]

            output_file = os.path.join(args.output_dir, f"round_{round_num + 1}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            print(f"💾 Complete results (including previous rounds) saved to: {output_file}")

        # 计算并保存统计结果
        try:
            # 确定语言参数
            language = args.language if args.language else 'chinese'
            calculate_and_save_stats(output_file, round_num + 1, args.output_dir, language)
        except Exception as e:
            print(f"⚠️  Warning: Failed to calculate statistics for round {round_num + 1}: {e}")

        print()


    print("🎊 All rounds completed successfully!")


if __name__ == "__main__":
    main()
