#!/bin/bash
# =============================================================================
# ODIN v7.0 - Installation Script
# =============================================================================
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "============================================="
echo "     ODIN v7.0 - Installation"
echo "============================================="
echo -e "${NC}"

# -----------------------------------------------------------------------------
# Prerequisites Check
# -----------------------------------------------------------------------------

echo -e "${YELLOW}Checking prerequisites...${NC}"

# Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found.${NC}"
    echo "Install Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo -e "${GREEN}[OK] Docker${NC}"

# Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose not found.${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Docker Compose${NC}"

# GPU Detection
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}[OK] NVIDIA GPU detected - GPU acceleration available${NC}"
    GPU_AVAILABLE=true
else
    echo -e "${YELLOW}[--] No NVIDIA GPU - CPU mode (slower for local LLM)${NC}"
    GPU_AVAILABLE=false
fi

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

echo ""
echo -e "${YELLOW}Configuration...${NC}"

# .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}[OK] .env created from .env.example${NC}"
    echo -e "${YELLOW}    Edit .env to customize settings${NC}"
else
    echo -e "${YELLOW}[--] .env already exists (kept)${NC}"
fi

# odin.config.yaml
if [ ! -f odin.config.yaml ]; then
    cp odin.config.example.yaml odin.config.yaml
    echo -e "${GREEN}[OK] odin.config.yaml created${NC}"
else
    echo -e "${YELLOW}[--] odin.config.yaml already exists (kept)${NC}"
fi

# -----------------------------------------------------------------------------
# LLM Provider Selection
# -----------------------------------------------------------------------------

echo ""
echo -e "${BLUE}LLM Provider Setup${NC}"
echo "Choose your LLM provider(s):"
echo ""
echo "  1) Local only (Ollama) - Privacy-first, requires download"
echo "  2) Cloud only - Requires API keys"
echo "  3) Hybrid - Local primary, cloud fallback"
echo ""
read -p "Selection [1-3] (default: 1): " LLM_CHOICE
LLM_CHOICE=${LLM_CHOICE:-1}

case $LLM_CHOICE in
    1)
        echo -e "${GREEN}Local LLM selected${NC}"
        USE_LOCAL_LLM=true
        ;;
    2)
        echo -e "${GREEN}Cloud LLM selected${NC}"
        USE_LOCAL_LLM=false
        echo ""
        echo "Configure your API keys in .env file:"
        echo "  ANTHROPIC_API_KEY=sk-ant-..."
        echo "  OPENAI_API_KEY=sk-..."
        echo "  GROQ_API_KEY=gsk_..."
        ;;
    3)
        echo -e "${GREEN}Hybrid mode selected${NC}"
        USE_LOCAL_LLM=true
        echo ""
        echo "Configure your fallback API keys in .env file"
        ;;
    *)
        echo -e "${YELLOW}Invalid selection, defaulting to local${NC}"
        USE_LOCAL_LLM=true
        ;;
esac

# -----------------------------------------------------------------------------
# Download Local Models
# -----------------------------------------------------------------------------

if [ "$USE_LOCAL_LLM" = true ]; then
    echo ""
    echo -e "${YELLOW}Starting Ollama for model download...${NC}"
    docker compose --profile local-llm up -d ollama

    echo "Waiting for Ollama to start..."
    sleep 10

    echo -e "${BLUE}Downloading Qwen 2.5 7B (recommended)...${NC}"
    docker exec odin-ollama ollama pull qwen2.5:7b || {
        echo -e "${YELLOW}Model download will continue in background${NC}"
    }

    echo ""
    read -p "Download additional models? (Llama 3.1, DeepSeek Coder) [y/N]: " EXTRA_MODELS
    if [[ $EXTRA_MODELS =~ ^[Yy]$ ]]; then
        echo "Downloading Llama 3.1 8B..."
        docker exec odin-ollama ollama pull llama3.1:8b || true
        echo "Downloading DeepSeek Coder..."
        docker exec odin-ollama ollama pull deepseek-coder:6.7b || true
    fi

    docker compose stop ollama
fi

# -----------------------------------------------------------------------------
# Build Services
# -----------------------------------------------------------------------------

echo ""
echo -e "${YELLOW}Building services...${NC}"
docker compose build

# -----------------------------------------------------------------------------
# Initialize Database
# -----------------------------------------------------------------------------

echo ""
echo -e "${YELLOW}Initializing database...${NC}"
docker compose up -d postgres
sleep 10

# Run migrations if script exists
if [ -f scripts/setup_db.sh ]; then
    bash scripts/setup_db.sh
fi

# -----------------------------------------------------------------------------
# Start Services
# -----------------------------------------------------------------------------

echo ""
echo -e "${YELLOW}Starting ODIN services...${NC}"

if [ "$USE_LOCAL_LLM" = true ]; then
    docker compose --profile local-llm up -d
else
    docker compose up -d
fi

# Wait for services
echo "Waiting for services to be ready..."
sleep 15

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------

echo ""
echo -e "${YELLOW}Health check...${NC}"

# Check API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}[OK] API is running${NC}"
else
    echo -e "${YELLOW}[--] API starting...${NC}"
fi

# Check Orchestrator
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo -e "${GREEN}[OK] Orchestrator is running${NC}"
else
    echo -e "${YELLOW}[--] Orchestrator starting...${NC}"
fi

# Check Redis
if docker exec odin-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}[OK] Redis is running${NC}"
else
    echo -e "${RED}[ERR] Redis not responding${NC}"
fi

# Check PostgreSQL
if docker exec odin-postgres pg_isready -U odin > /dev/null 2>&1; then
    echo -e "${GREEN}[OK] PostgreSQL is running${NC}"
else
    echo -e "${RED}[ERR] PostgreSQL not responding${NC}"
fi

# -----------------------------------------------------------------------------
# Complete
# -----------------------------------------------------------------------------

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}     Installation complete!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo -e "${BLUE}Access points:${NC}"
echo "  API:          http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Orchestrator: http://localhost:9000"
echo ""
echo -e "${BLUE}Commands:${NC}"
echo "  make status   - Check service status"
echo "  make logs     - View logs"
echo "  make cli      - Open CLI"
echo "  make stop     - Stop services"
echo "  make restart  - Restart services"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  .env              - Environment variables"
echo "  odin.config.yaml  - ODIN configuration"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  docs/ARCHITECTURE.md       - System architecture"
echo "  docs/LLM_PROVIDERS.md      - Provider options"
echo "  docs/USER_CONFIGURATION.md - Configuration guide"
echo ""
echo -e "${GREEN}Ready to use ODIN!${NC}"
