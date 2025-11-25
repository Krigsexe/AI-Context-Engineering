# ODIN v7.0 - User Configuration Guide

**Your system, your rules. / Votre systeme, vos regles.**

---

## Quick Start / Demarrage Rapide

### 1. Copy the example configuration

```bash
cp .env.example .env
cp odin.config.example.yaml odin.config.yaml
```

### 2. Choose your LLM provider

Edit `odin.config.yaml`:

```yaml
# Option A: 100% Local (Ollama)
llm:
  primary:
    provider: ollama
    model: qwen2.5:7b

# Option B: Cloud (Anthropic)
llm:
  primary:
    provider: anthropic
    model: claude-3-5-sonnet-20241022

# Option C: Hybrid (Local + Cloud fallback)
llm:
  primary:
    provider: ollama
    model: qwen2.5:7b
  fallback:
    - provider: anthropic
      model: claude-3-haiku-20240307
```

### 3. Set API keys (if using cloud)

Edit `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=gsk_...
```

### 4. Run installation

```bash
./install.sh
```

---

## Complete Configuration Reference

### odin.config.yaml

```yaml
# =============================================================================
# ODIN v7.0 Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# LLM Configuration
# -----------------------------------------------------------------------------
llm:
  # Primary provider (used for main tasks)
  primary:
    provider: ollama          # See LLM_PROVIDERS.md for all options
    model: qwen2.5:7b
    temperature: 0.2          # Lower = more deterministic
    max_tokens: 4096
    timeout: 300              # Seconds

  # Fallback chain (tried in order if primary fails)
  fallback:
    - provider: groq
      model: llama-3.1-70b-versatile
    - provider: anthropic
      model: claude-3-haiku-20240307

  # Consensus oracle configuration
  consensus:
    enabled: true
    min_agreement: 0.67       # Minimum agreement ratio (2/3)
    providers:
      - provider: ollama
        model: qwen2.5:7b
      - provider: ollama
        model: llama3.1:8b
      - provider: ollama
        model: deepseek-coder:6.7b

  # Task-specific model overrides
  specialized:
    code_generation:
      provider: ollama
      model: deepseek-coder:6.7b
      temperature: 0.1        # Very low for code
    code_review:
      provider: anthropic
      model: claude-3-5-sonnet-20241022
    research:
      provider: perplexity
      model: pplx-70b-online
    fast_tasks:
      provider: groq
      model: llama-3.1-8b-instant

# -----------------------------------------------------------------------------
# Confidence Thresholds
# -----------------------------------------------------------------------------
confidence:
  # When to respond directly
  high_confidence: 0.95

  # When to respond with caveats
  moderate_confidence: 0.60

  # When to refuse and ask questions
  low_confidence: 0.40

  # Minimum sources required
  min_sources: 1

  # Require oracle validation for these task types
  require_oracle:
    - code_generation
    - security_review
    - deployment

# -----------------------------------------------------------------------------
# Agent Configuration
# -----------------------------------------------------------------------------
agents:
  # Enable/disable specific agents
  enabled:
    - intake
    - retrieval
    - verification
    - reasoning
    - critique
    - formulation
    - dev
    - tests
    - oracle_code
    - mcp
    - approbation
    - apprentissage

  # Agent-specific settings
  settings:
    critique:
      # How aggressive the red team should be
      aggressiveness: medium  # low, medium, high

    approbation:
      # Always require human approval for these actions
      require_approval:
        - file_deletion
        - deployment
        - database_migration
        - security_changes

    apprentissage:
      # Learning from feedback
      auto_learn: true
      require_validation: true  # Human must validate learned patterns

# -----------------------------------------------------------------------------
# Oracle Configuration
# -----------------------------------------------------------------------------
oracles:
  code:
    enabled: true
    linters:
      python: [pylint, flake8]
      javascript: [eslint]
      typescript: [eslint, tsc]
    type_checkers:
      python: mypy
      typescript: tsc
    security_scanners:
      python: [bandit, safety]
      javascript: [npm-audit]
    test_runner: true

  knowledge_graph:
    enabled: true
    provider: neo4j
    auto_populate: false     # Manual curation preferred

  temporal:
    enabled: true
    freshness_limits:
      tech: 90               # Days
      security: 30
      legal: 180
      general: 365

  consensus:
    enabled: true
    min_models: 2
    max_models: 5

# -----------------------------------------------------------------------------
# Checkpoint & Rollback
# -----------------------------------------------------------------------------
checkpoints:
  # Create checkpoint before these actions
  auto_checkpoint:
    - file_modification
    - code_generation
    - refactoring
    - deployment

  # Retention policy
  retention:
    max_checkpoints: 100
    max_age_days: 30

  # Storage backend
  storage: postgresql        # postgresql, filesystem, s3

# -----------------------------------------------------------------------------
# Feedback & Learning
# -----------------------------------------------------------------------------
feedback:
  # Feedback options presented to user
  options:
    - value: perfect
      label: "Perfect - Exactly what I needed"
      action: archive_pattern
    - value: acceptable
      label: "Acceptable - Minor issues"
      action: log_improvement
    - value: false
      label: "False - Incorrect or harmful"
      action: rollback_and_log

  # Auto-actions on feedback
  auto_rollback_on_false: true
  require_reason_on_false: true

# -----------------------------------------------------------------------------
# Privacy & Security
# -----------------------------------------------------------------------------
privacy:
  # Data retention
  log_retention_days: 90

  # What to log
  log_prompts: true
  log_responses: true
  log_sources: true

  # Anonymization
  anonymize_logs: false

  # Cloud provider restrictions
  allowed_cloud_providers:
    - anthropic
    - openai
    - google
    - groq
    # Remove providers you don't trust

  # Sensitive file patterns (never sent to cloud)
  sensitive_patterns:
    - "*.env"
    - "*credentials*"
    - "*secret*"
    - "*.pem"
    - "*.key"

# -----------------------------------------------------------------------------
# Performance
# -----------------------------------------------------------------------------
performance:
  # Parallel agent execution
  max_parallel_agents: 5

  # Caching
  cache_enabled: true
  cache_ttl_seconds: 3600

  # Rate limiting (for cloud providers)
  rate_limit:
    requests_per_minute: 60
    tokens_per_minute: 100000

# -----------------------------------------------------------------------------
# User Interface
# -----------------------------------------------------------------------------
ui:
  # Language
  language: en              # en, fr

  # Verbosity
  verbosity: normal         # quiet, normal, verbose, debug

  # Colors in terminal
  colors: true

  # Show confidence scores
  show_confidence: true

  # Show reasoning chain
  show_reasoning: false     # Can be verbose

  # Show sources
  show_sources: true

# -----------------------------------------------------------------------------
# Integrations
# -----------------------------------------------------------------------------
integrations:
  # Git integration
  git:
    auto_commit: false
    commit_message_prefix: "[ODIN]"

  # IDE integration
  vscode:
    enabled: true
    show_inline_suggestions: true

  # CI/CD integration
  ci:
    fail_on_low_confidence: true
    confidence_threshold: 0.80
```

---

## Environment Variables Reference

```bash
# =============================================================================
# ODIN Environment Variables
# =============================================================================

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=odin
POSTGRES_USER=odin
POSTGRES_PASSWORD=your_secure_password

# -----------------------------------------------------------------------------
# Redis
# -----------------------------------------------------------------------------
REDIS_URL=redis://localhost:6379

# -----------------------------------------------------------------------------
# Neo4j (Knowledge Graph)
# -----------------------------------------------------------------------------
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# -----------------------------------------------------------------------------
# LLM Providers (add keys for providers you use)
# -----------------------------------------------------------------------------

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...          # Optional

# Google
GOOGLE_API_KEY=...

# xAI (Grok)
XAI_API_KEY=...

# Groq
GROQ_API_KEY=gsk_...

# Mistral
MISTRAL_API_KEY=...

# Together AI
TOGETHER_API_KEY=...

# Fireworks
FIREWORKS_API_KEY=...

# Perplexity
PERPLEXITY_API_KEY=pplx-...

# DeepSeek
DEEPSEEK_API_KEY=...

# HuggingFace
HF_API_KEY=hf_...

# Cohere
COHERE_API_KEY=...

# -----------------------------------------------------------------------------
# Local Providers
# -----------------------------------------------------------------------------

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# vLLM
VLLM_BASE_URL=http://localhost:8000

# Custom OpenAI-compatible endpoint
CUSTOM_LLM_BASE_URL=https://your-server.com/v1
CUSTOM_LLM_API_KEY=...

# -----------------------------------------------------------------------------
# API Server
# -----------------------------------------------------------------------------
API_PORT=8000
API_SECRET_KEY=your_32_char_minimum_secret_key

# -----------------------------------------------------------------------------
# Orchestrator
# -----------------------------------------------------------------------------
ORCHESTRATOR_PORT=9000

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_LEVEL=info              # debug, info, warn, error
LOG_FORMAT=json             # json, text

# -----------------------------------------------------------------------------
# Features
# -----------------------------------------------------------------------------
ODIN_ENV=production         # development, production
ODIN_DEBUG=false
```

---

## Configuration Profiles / Profils de Configuration

### Profile: Privacy-First (100% Local)

```yaml
# odin.config.privacy-first.yaml
llm:
  primary:
    provider: ollama
    model: qwen2.5:7b
  consensus:
    providers:
      - provider: ollama
        model: qwen2.5:7b
      - provider: ollama
        model: llama3.1:8b

privacy:
  allowed_cloud_providers: []  # None
  log_prompts: false
  anonymize_logs: true
```

### Profile: Performance-First (Cloud)

```yaml
# odin.config.performance.yaml
llm:
  primary:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
  fallback:
    - provider: openai
      model: gpt-4o
  consensus:
    providers:
      - provider: anthropic
        model: claude-3-5-sonnet-20241022
      - provider: openai
        model: gpt-4o
      - provider: google
        model: gemini-1.5-pro

performance:
  max_parallel_agents: 10
```

### Profile: Budget-First (Free Tier)

```yaml
# odin.config.budget.yaml
llm:
  primary:
    provider: groq           # Free tier
    model: llama-3.1-70b-versatile
  fallback:
    - provider: ollama       # Local fallback
      model: qwen2.5:3b
  consensus:
    enabled: false           # Save tokens
```

### Profile: Enterprise (Self-Hosted)

```yaml
# odin.config.enterprise.yaml
llm:
  primary:
    provider: vllm
    model: Qwen/Qwen2.5-72B-Instruct
    base_url: https://llm.internal.company.com

privacy:
  allowed_cloud_providers: []
  log_retention_days: 365    # Compliance

checkpoints:
  storage: s3
  retention:
    max_checkpoints: 1000
```

---

## CLI Configuration Commands

```bash
# View current configuration
odin config show

# Set a value
odin config set llm.primary.provider anthropic
odin config set llm.primary.model claude-3-5-sonnet-20241022

# Use a profile
odin config profile privacy-first

# Validate configuration
odin config validate

# Export configuration
odin config export > my-config.yaml

# Import configuration
odin config import my-config.yaml
```

---

## Troubleshooting / Depannage

### Provider not working

```bash
# Test provider connectivity
odin provider test anthropic

# List available models
odin provider models ollama

# Check API key
odin provider check-key anthropic
```

### Configuration issues

```bash
# Validate all settings
odin config validate --verbose

# Reset to defaults
odin config reset

# Show effective configuration (with all defaults)
odin config show --resolved
```

---

*Your configuration, your control. / Votre configuration, votre controle.*
