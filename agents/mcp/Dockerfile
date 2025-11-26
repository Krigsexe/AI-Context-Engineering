# =============================================================================
# ODIN v7.0 - MCP Agent (Checkpoint/System)
# =============================================================================

FROM odin-agent-base:latest

# Set working directory
WORKDIR /app

# Copy specific agent code
COPY agents/system /app/agents/system
COPY agents/shared /app/agents/shared
COPY agents/__init__.py /app/agents/
COPY agents/cli.py /app/agents/

# Set Python path
ENV PYTHONPATH=/app

# Run the agent
CMD ["python", "-m", "agents.cli", "run", "mcp"]
