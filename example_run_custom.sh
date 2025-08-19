#!/bin/bash

# Meeseeks Custom Data Example Script
# Please modify the following parameters according to your actual situation

echo "=== Running with custom data file ==="
python run.py \
    --qwen_url "http://10.164.37.122:8080" \
    --qwen_coder_url "http://10.164.26.69:8080" \
    --tested_model_url "http://10.164.37.122:8080" \
    --batch_size 100 \
    --rounds 2 \
    --data_path "/Users/jiamingwang/Desktop/Meeseeks开源版本/白盒数据.json" \
    --output_dir "evaluation_results_custom"

echo "Custom data evaluation completed!"
