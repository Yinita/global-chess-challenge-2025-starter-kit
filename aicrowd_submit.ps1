# PowerShell script for AIcrowd submission
# Global Chess Challenge 2025

# Login to AIcrowd
# aicrowd login

# Configuration variables
$CHALLENGE = "global-chess-challenge-2025"
$HF_REPO = "Qwen/Qwen3-8B"
$HF_REPO_TAG = "main"
$PROMPT_TEMPLATE = "player_agents/qwen3_8b_prompt_template.jinja"

# Neuron/vLLM configuration for Trainium (2x 32GB, 2 Neuron Cores per device)
$NEURON_MODEL_TYPE = "qwen3"
$MAX_MODEL_LEN = "12000"
$GPU_MEMORY_UTIL = "0.85"
$TENSOR_PARALLEL_SIZE = "2"
$DTYPE = "bfloat16"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AIcrowd Submission - Global Chess Challenge 2025" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Model: $HF_REPO" -ForegroundColor Green
Write-Host "Prompt Template: $PROMPT_TEMPLATE" -ForegroundColor Green
Write-Host ""
Write-Host "Neuron/vLLM Configuration:" -ForegroundColor Yellow
Write-Host "  - Model Type: $NEURON_MODEL_TYPE"
Write-Host "  - Max Model Length: $MAX_MODEL_LEN"
Write-Host "  - GPU Memory Utilization: $GPU_MEMORY_UTIL"
Write-Host "  - Tensor Parallel Size: $TENSOR_PARALLEL_SIZE (dual card)"
Write-Host "  - Dtype: $DTYPE"
Write-Host ""
Write-Host "If the repo is private, make sure to add access to aicrowd."
Write-Host "Details can be found in docs/huggingface-gated-models.md"
Write-Host ""

# Submit the model with vLLM parameters
aicrowd submit-model `
    --challenge $CHALLENGE `
    --hf-repo $HF_REPO `
    --hf-repo-tag $HF_REPO_TAG `
    --prompt_template_path $PROMPT_TEMPLATE `
    --neuron.model-type $NEURON_MODEL_TYPE `
    --vllm.max-model-len $MAX_MODEL_LEN `
    --vllm.gpu-memory-utilization $GPU_MEMORY_UTIL `
    --vllm.tensor-parallel-size $TENSOR_PARALLEL_SIZE `
    --vllm.dtype $DTYPE `
    --vllm.enforce-eager true

Write-Host ""
Write-Host "Submission complete!" -ForegroundColor Green
