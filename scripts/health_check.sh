#!/bin/bash
# =============================================================================
# ODIN v7.0 - Health Check Script
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "ODIN v7.0 - Health Check"
echo "========================"
echo ""

# PostgreSQL
if docker exec odin-postgres pg_isready -U odin > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} PostgreSQL"
else
    echo -e "${RED}[ERR]${NC} PostgreSQL"
fi

# Redis
if docker exec odin-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Redis"
else
    echo -e "${RED}[ERR]${NC} Redis"
fi

# Ollama (if running)
if docker ps --format '{{.Names}}' | grep -q odin-ollama; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}[OK]${NC} Ollama"
    else
        echo -e "${YELLOW}[--]${NC} Ollama (starting...)"
    fi
fi

# API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} API"
else
    echo -e "${YELLOW}[--]${NC} API (not responding)"
fi

# Orchestrator
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Orchestrator"
else
    echo -e "${YELLOW}[--]${NC} Orchestrator (not responding)"
fi

# Agents
for agent in intake retrieval dev mcp approbation oracle-code; do
    container="odin-agent-${agent}"
    if docker ps --format '{{.Names}}' | grep -q "$container"; then
        echo -e "${GREEN}[OK]${NC} Agent: $agent"
    else
        echo -e "${YELLOW}[--]${NC} Agent: $agent (not running)"
    fi
done

echo ""
echo "Done."
