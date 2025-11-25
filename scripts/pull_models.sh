#!/bin/bash
# =============================================================================
# ODIN v7.0 - Pull LLM Models
# =============================================================================
set -e

echo "ODIN v7.0 - Model Download"
echo "=========================="
echo ""

# Ensure Ollama is running
if ! docker ps --format '{{.Names}}' | grep -q odin-ollama; then
    echo "Starting Ollama..."
    docker compose --profile local-llm up -d ollama
    sleep 10
fi

# Models to download
declare -A MODELS
MODELS["qwen2.5:7b"]="Qwen 2.5 7B (recommended, balanced)"
MODELS["llama3.1:8b"]="Llama 3.1 8B (Meta, popular)"
MODELS["deepseek-coder:6.7b"]="DeepSeek Coder 6.7B (code specialized)"
MODELS["mistral:7b"]="Mistral 7B (fast)"
MODELS["phi3:mini"]="Phi-3 Mini (small, fast)"

echo "Available models:"
echo ""
i=1
for model in "${!MODELS[@]}"; do
    echo "  $i) $model - ${MODELS[$model]}"
    ((i++))
done
echo ""
echo "  a) All models"
echo "  q) Quit"
echo ""

read -p "Select model(s) to download [1-5, a, q]: " selection

download_model() {
    local model=$1
    echo ""
    echo "Downloading $model..."
    docker exec odin-ollama ollama pull "$model"
    echo "Done: $model"
}

case $selection in
    1) download_model "qwen2.5:7b" ;;
    2) download_model "llama3.1:8b" ;;
    3) download_model "deepseek-coder:6.7b" ;;
    4) download_model "mistral:7b" ;;
    5) download_model "phi3:mini" ;;
    a|A)
        for model in "${!MODELS[@]}"; do
            download_model "$model"
        done
        ;;
    q|Q) echo "Cancelled." ;;
    *) echo "Invalid selection." ;;
esac

echo ""
echo "Current models:"
docker exec odin-ollama ollama list
