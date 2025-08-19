#!/usr/bin/env python3
"""
Meeseeks 自定义数据运行脚本
使用自定义数据文件路径运行评估
"""

import subprocess
import sys
import os
import argparse

def main():
    """运行自定义数据评估"""
    parser = argparse.ArgumentParser(description='Meeseeks自定义数据评估脚本')
    parser.add_argument('--data_path', required=True, help='自定义数据文件路径')
    parser.add_argument('--qwen_url', default="http://10.164.46.86:8080", help='Qwen API的URL')
    parser.add_argument('--qwen_coder_url', default="http://10.164.46.199:8080", help='Qwen Coder API的URL')
    parser.add_argument('--tested_model_url', default="http://10.164.46.86:8080", help='被测模型API的URL')
    parser.add_argument('--batch_size', type=int, default=100, help='批处理大小')
    parser.add_argument('--rounds', type=int, default=2, help='评估轮数')
    parser.add_argument('--output_dir', default='evaluation_results_custom', help='输出目录')

    args = parser.parse_args()

    print("📁 Starting Meeseeks Custom Data Evaluation")
    print("=" * 50)

    # 检查数据文件是否存在
    if not os.path.exists(args.data_path):
        print(f"❌ Data file not found: {args.data_path}")
        return 1

    print("🔧 Configuration:")
    print(f"   - Data Path: {args.data_path}")
    print(f"   - Qwen URL: {args.qwen_url}")
    print(f"   - Qwen Coder URL: {args.qwen_coder_url}")
    print(f"   - Tested Model URL: {args.tested_model_url}")
    print(f"   - Batch Size: {args.batch_size}")
    print(f"   - Rounds: {args.rounds}")
    print(f"   - Output Directory: {args.output_dir}")
    print("=" * 50)

    # 构建命令
    cmd = [
        sys.executable, "run.py",
        "--qwen_url", args.qwen_url,
        "--qwen_coder_url", args.qwen_coder_url,
        "--tested_model_url", args.tested_model_url,
        "--batch_size", str(args.batch_size),
        "--rounds", str(args.rounds),
        "--data_path", args.data_path,
        "--output_dir", args.output_dir
    ]

    try:
        # 运行评估
        print("🚀 Starting evaluation...")
        result = subprocess.run(cmd, check=True)
        print("✅ Custom data evaluation completed successfully!")
        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running evaluation: {e}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Evaluation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
