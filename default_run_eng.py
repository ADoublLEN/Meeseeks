#!/usr/bin/env python3
"""
Meeseeks English Data Default Run Script
Run English data evaluation with preset API addresses and parameters
"""

import subprocess
import sys
import os

def main():
    """Run English data evaluation"""
    print("🇺🇸 Starting Meeseeks English Data Evaluation")
    print("=" * 50)

    # Default configuration parameters
    config = {
        "qwen_url": "http://10.164.46.86:8080",
        "qwen_coder_url": "http://10.164.46.199:8080",
        "tested_model_url": "http://10.164.46.86:8080",
        "batch_size": 100,
        "rounds": 2,
        "language": "english",
        "output_dir": "evaluation_results_english"
    }

    print("🔧 Configuration:")
    for key, value in config.items():
        print(f"   - {key}: {value}")
    print("=" * 50)

    # Build command
    cmd = [
        sys.executable, "run.py",
        "--qwen_url", config["qwen_url"],
        "--qwen_coder_url", config["qwen_coder_url"],
        "--tested_model_url", config["tested_model_url"],
        "--batch_size", str(config["batch_size"]),
        "--rounds", str(config["rounds"]),
        "--language", config["language"],
        "--output_dir", config["output_dir"]
    ]

    try:
        # Run evaluation
        print("🚀 Starting evaluation...")
        result = subprocess.run(cmd, check=True)
        print("✅ English data evaluation completed successfully!")
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
