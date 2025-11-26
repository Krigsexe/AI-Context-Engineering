#!/bin/bash
# =============================================================================
# ODIN v7.0 - One-Click Deployment Script
# =============================================================================
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "============================================="
echo "     ODIN v7.0 - Auto Deployment"
echo "============================================="
echo -e "${NC}"

# 1. Prerequisites Check
echo -e "${YELLOW}[1/5] Checking system...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    exit 1
fi

# GPU Check
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
else
    echo -e "${YELLOW}! No NVIDIA GPU detected (CPU mode)${NC}"
fi

# 2. Configuration Setup
echo -e "${YELLOW}[2/5] Configuring environment...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env${NC}"
    # Set secure secrets automatically for local dev
    sed -i 's/change_me_in_production/odin_local_dev_secret/g' .env
    sed -i 's/generate_secure_key_minimum_32_chars/odin_api_local_dev_secret_key_32_chars/g' .env
fi

if [ ! -f odin.config.yaml ]; then
    cp odin.config.example.yaml odin.config.yaml
    echo -e "${GREEN}✓ Created odin.config.yaml${NC}"
fi

# 3. Build & Start Services
echo -e "${YELLOW}[3/5] Building and starting services...${NC}"
echo "This may take a few minutes for the first run..."

# Build base image first
docker compose build agent-base

# Build and start all services
docker compose up -d --build

# 4. Wait for Services
echo -e "${YELLOW}[4/5] Waiting for services...${NC}"

wait_for_service() {
    local service=$1
    local url=$2
    local max_retries=30
    local count=0
    
    echo -n "Waiting for $service..."
    while ! curl -s $url > /dev/null; do
        sleep 2
        echo -n "."
        count=$((count+1))
        if [ $count -ge $max_retries ]; then
            echo -e "${RED} Timeout!${NC}"
            return 1
        fi
    done
    echo -e "${GREEN} Ready!${NC}"
}

# Wait for API (which depends on Orchestrator -> Redis/Postgres)
# We check API health which confirms backend stack is up
wait_for_service "API" "http://localhost:8000/api/v1/health"

# 5. Model Initialization (Background)
echo -e "${YELLOW}[5/5] Initializing LLM models...${NC}"
if docker compose ps ollama | grep -q "Up"; then
    echo "Downloading Qwen 2.5 7B model (this happens in background)..."
    docker compose exec -d ollama ollama pull qwen2.5:7b
    echo -e "${GREEN}✓ Model download started${NC}"
else
    echo -e "${YELLOW}! Ollama service not running (Cloud mode?)${NC}"
fi

# Final Summary
echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}     DEPLOYMENT COMPLETE${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "Dashboard:    ${BLUE}http://localhost${NC}"
echo -e "API:          ${BLUE}http://localhost:8000${NC}"
echo -e "Orchestrator: ${BLUE}http://localhost:9000${NC}"
echo ""
echo -e "${YELLOW}Note: LLM models may still be downloading in the background.${NC}"
echo -e "Check status with: docker compose logs -f ollama"
echo ""
