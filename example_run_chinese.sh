#!/bin/bash

# Meeseeks Chinese Data Example Script
# Please modify the following parameters according to your actual situation

echo "=== Running with Chinese data ==="
python run.py \
    --qwen_url "http://10.164.37.122:8001" \
    --qwen_coder_url "http://10.164.26.69:8001" \
    --tested_model_url "http://10.164.37.122:8001" \
    --batch_size 100 \
    --rounds 2 \
    --language chinese \
    --output_dir "evaluation_results_chinese" 
echo "Chinese data evaluation completed!"
