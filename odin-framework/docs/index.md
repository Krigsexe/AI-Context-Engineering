# ODIN Framework Documentation

Welcome to the ODIN Framework - **Orchestrated Development Intelligence Network**.

## What is ODIN?

ODIN is a comprehensive Context Engineering & Multi-Agent framework that transforms unreliable LLMs into production-ready development tools through:

- **Multi-layer validation** - Pre-processing, generation, and post-validation
- **100% local data** - Complete sovereignty with SQLite storage
- **Provider agnostic** - Works with any LLM (Ollama, Anthropic, OpenAI, Google, Groq, etc.)
- **Anti-hallucination** - 5-level confidence framework with oracle verification
- **Checkpoint/Rollback** - Full state preservation and reversibility

## Key Features

### 🎯 Two-Part System

#### PARTIE A: Documentation Website

- Next.js showcase deployed on Vercel
- Auto-synced documentation from GitHub
- Interactive examples and guides

#### PARTIE B: CLI Framework

- Installable via `npx @odin/cli init`
- Patches your existing dev environment
- Compatible with Claude, Cursor, Windsurf, Aider, and more

### ✳ Multi-Agent Architecture

- **Cognitive Layer**: DevAgent, ReviewAgent, ArchitectAgent
- **Oracle Layer**: Code execution verification (AXIOM confidence)
- **Execution Layer**: TestAgent, SecurityAgent
- **System Layer**: CheckpointAgent, AuditAgent

### 🛡️ Confidence Framework

| Level | Value | Description |
|-------|-------|-------------|
| **AXIOM** | 100% | Deterministic/verified |
| **HIGH** | 95%+ | Very confident, verified  |
| **MODERATE** | 70-95% | Reasonably confident |
| **UNCERTAIN** | 40-70% | Needs verification |
| **UNKNOWN** | <40% | Should not proceed |

## Quick Start

```bash
# Install ODIN in your project
npx @odin/cli init

# Check installation
odin status

# View agents
odin agents
```

## How It Works

ODIN doesn't replace your LLM - it augments it with disciplinary systems:

```
┌─────────────────────┐
│   User Request      │
└──────────┬──────────┘
           │
    ┌──────▼───────┐
    │ Pre-Process  │  ← Retrieval, Verification, Knowledge Graph
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  LLM (Qwen)  │  ← Your chosen provider (unchanged)
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │ Post-Valid   │  ← Oracle checks, Security scan, Tests
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  Checkpoint  │  ← Rollback-ready result
    └──────────────┘
```

## Philosophy

ODIN embodies three core values:

1. **Honesty** - Always cite sources or admit uncertainty
2. **Traceability** - Every decision logged and auditable
3. **Reversibility** - No action is final, rollback always possible

## Next Steps

- [Installation Guide](./getting-started/installation.md)
- [Configuration](./getting-started/configuration.md)
- [Core Concepts](./concepts/agents.md)
- [CLI Reference](./cli/commands.md)

## Community

- 🌟 [Star on GitHub](https://github.com/Krigsexe/AI-Context-Engineering)
- 💬 [Discord Community](#)
- 📖 [Full Documentation](#)

---

Built with ❤️ by Julien Gelée (Krigs) and contributors
