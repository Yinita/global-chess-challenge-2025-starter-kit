# PowerShell script for AIcrowd submission
# Global Chess Challenge 2025
#
# ============================================================
# SUPPORTED vLLM FLAGS (aicrowd submit-model):
# ============================================================
# --vllm.max-model-len           # Maximum model context length
# --vllm.dtype                   # Data type (e.g., bfloat16, float16)
# --vllm.kv-cache-dtype          # KV cache data type
# --vllm.quantization            # Quantization method
# --vllm.load-format             # Model loading format
# --vllm.rope-theta              # RoPE theta parameter
# --vllm.rope-scaling            # RoPE scaling configuration
# --vllm.max-num-batched-tokens  # Max tokens per batch
# --vllm.max-num-seqs            # Max sequences
# --vllm.enforce-eager true      # Force eager execution
# --vllm.enable-lora true        # Enable LoRA
# --vllm.lora-dtype              # LoRA data type
# --vllm.lora-extra-vocab-size   # Extra vocab size for LoRA
# --vllm.enable-prefix-caching true  # Enable prefix caching
# --vllm-env.allow-long-max-model-len  # Allow long context
#
# Inference time parameters:
# --vllm-inference.max-tokens    # Max tokens for inference
# ============================================================

# Login to AIcrowd (uncomment if needed)
# aicrowd login

# Configuration variables
$CHALLENGE = "global-chess-challenge-2025"
$HF_REPO = "Qwen/Qwen2.5-7B-Instruct"
$HF_REPO_TAG = "main"
# $PROMPT_TEMPLATE = "player_agents/qwen3_8bnothink_prompt_template.jinja"
$PROMPT_TEMPLATE = "player_agents/llm_agent_prompt_template.jinja"

# Neuron/vLLM configuration
$NEURON_MODEL_TYPE = "qwen2"
$MAX_MODEL_LEN = "6000"
$DTYPE = "bfloat16"
# $KV_CACHE_DTYPE = "auto"
# $QUANTIZATION = ""
# $LOAD_FORMAT = "auto"
# $ROPE_THETA = ""
# $ROPE_SCALING = ""
# $MAX_NUM_BATCHED_TOKENS = ""
# $MAX_NUM_SEQS = ""
# $LORA_DTYPE = ""
# $LORA_EXTRA_VOCAB_SIZE = ""
# $INFERENCE_MAX_TOKENS = "2000"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AIcrowd Submission - Qwen2.5 (Supported Flags Only)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Model: $HF_REPO" -ForegroundColor Green
Write-Host "Prompt Template: $PROMPT_TEMPLATE" -ForegroundColor Green
Write-Host ""
Write-Host "Neuron/vLLM Configuration:" -ForegroundColor Yellow
Write-Host "  - Model Type: $NEURON_MODEL_TYPE"
Write-Host "  - Max Model Length: $MAX_MODEL_LEN"
Write-Host "  - Dtype: $DTYPE"
Write-Host "  - Enforce Eager: true"
Write-Host ""

# Submit the model with all available vLLM flags
# Uncomment and set values as needed
aicrowd submit-model `
    --challenge $CHALLENGE `
    --hf-repo $HF_REPO `
    --hf-repo-tag $HF_REPO_TAG `
    --prompt_template_path $PROMPT_TEMPLATE `
    --neuron.model-type $NEURON_MODEL_TYPE `
    --vllm.max-model-len $MAX_MODEL_LEN `
    --vllm.dtype $DTYPE `
    --vllm.enforce-eager true
    # --vllm.kv-cache-dtype $KV_CACHE_DTYPE `
    # --vllm.quantization $QUANTIZATION `
    # --vllm.load-format $LOAD_FORMAT `
    # --vllm.rope-theta $ROPE_THETA `
    # --vllm.rope-scaling $ROPE_SCALING `
    # --vllm.max-num-batched-tokens $MAX_NUM_BATCHED_TOKENS `
    # --vllm.max-num-seqs $MAX_NUM_SEQS `
    # --vllm.enable-lora true `
    # --vllm.lora-dtype $LORA_DTYPE `
    # --vllm.lora-extra-vocab-size $LORA_EXTRA_VOCAB_SIZE `
    # --vllm.enable-prefix-caching true `
    # --vllm-env.allow-long-max-model-len `
    # --vllm-inference.max-tokens $INFERENCE_MAX_TOKENS

Write-Host ""
Write-Host "Submission complete!" -ForegroundColor Green
