#!/bin/bash

# Meeseeks English Data Example Script
# Please modify the following parameters according to your actual situation

echo "=== Running with English data ==="
python run.py \
    --qwen_url "http://10.164.37.122:8080" \
    --qwen_coder_url "http://10.166.193.8:8080" \
    --tested_model_url "http://10.164.37.122:8080" \
    --batch_size 100 \
    --rounds 2 \
    --language english \
    --output_dir "evaluation_results_english"

echo "English data evaluation completed!"
