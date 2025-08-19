#!/bin/bash

# Meeseeks Chinese Data Example Script
# Please modify the following parameters according to your actual situation

echo "=== Running with Chinese data ==="
python run.py \
    --qwen_url "http://10.166.146.105:8080" \
    --qwen_coder_url "http://10.164.146.14:8080" \
    --tested_model_url "http://10.166.146.105:8080" \
    --batch_size 100 \
    --rounds 2 \
    --language chinese \
    --output_dir "evaluation_results_chinese" 
echo "Chinese data evaluation completed!"
