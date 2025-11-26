# =============================================================================
# ODIN v7.0 - Oracle Code Agent
# =============================================================================

FROM odin-agent-base:latest

# Set working directory
WORKDIR /app

# Install additional tools for code analysis (linters, scanners)
USER root
RUN pip install pylint flake8 mypy bandit safety
USER odin

# Copy specific agent code
COPY agents/oracle /app/agents/oracle
COPY agents/shared /app/agents/shared
COPY agents/__init__.py /app/agents/
COPY agents/cli.py /app/agents/

# Set Python path
ENV PYTHONPATH=/app

# Run the agent
CMD ["python", "-m", "agents.cli", "run", "oracle_code"]
