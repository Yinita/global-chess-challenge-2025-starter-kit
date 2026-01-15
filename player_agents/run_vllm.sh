MODEL_NAME_OR_PATH="Qwen/Qwen3-8B"
# MODEL_NAME_OR_PATH="<path/to/your/saved_sft_model>"

vllm serve $MODEL_NAME_OR_PATH \
    --served-model-name aicrowd-model \
    --dtype bfloat16 \
    --trust-remote-code \
    --gpu-memory-utilization 0.9 \
    --enforce-eager \
    --disable-log-stats \
    --host 0.0.0.0 \
    --max-model-len 12000 \
    --reasoning-parser qwen3 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --port 5000