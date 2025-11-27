# ✳ ODIN Framework

**Orchestrated Development Intelligence Network**

A complete Context Engineering & Multi-Agent framework for reliable AI-assisted development.

## 🎯 Overview

ODIN is a dual-purpose framework:

### **PARTIE A: Documentation Website**

- Next.js showcase website
- Auto-synced documentation from GitHub
- Deployed on Vercel with Neon database
- Features, guides, and API reference

### **PARTIE B: CLI Framework**

- Installable CLI tool (`npx @odin/cli init`)
- Patches your existing dev projects
- Compatible with Claude, Cursor, Windsurf, Aider, Continue, Cline, Roo-Cline
- 100% local data storage (SQLite)
- Provider-agnostic LLM support

## 🚀 Quick Start

### Install ODIN in Your Project

```bash
# Using npx (recommended)
npx @odin/cli init

# Or install globally
pnpm add -g @odin/cli
odin init
```

### Select Your LLM Provider

ODIN supports:

- 🏠 **Ollama** (Local - No API key)
- ☁️ **Anthropic** (Claude)
- ☁️ **OpenAI** (GPT)
- ☁️ **Google** (Gemini)
- ☁️ **Groq** (Fast Inference)
- ☁️ **xAI** (Grok)
- ☁️ **Mistral**
- ☁️ **Together AI**
- ☁️ **DeepSeek**
- ☁️ **HuggingFace**

## 📦 What Gets Installed

ODIN injects itself **inside** your existing AI tool directory:

```
.claude/odin/          # or .cursor/odin, .windsurf/odin, etc.
├── config.yaml        # LLM provider configuration
├── orchestrator.md    # Main orchestrator agent
├── rules/             # 30+ architecture rules
│   ├── no-hardcoded-secrets.md
│   ├── code-review-required.md
│   └── checkpoint-before-refactor.md
├── agents/            # Agent definitions
│   ├── dev.yaml
│   ├── security.yaml
│   └── ...
├── db/
│   └── odin.db        # Local SQLite database
├── memory-bank/       # Persistent project context
├── archives/          # Session history
├── index/             # Semantic index
└── security/          # Security policies
```

## 🎨 Features

### Multi-Agent Architecture

- **Cognitive Agents**: Dev, Review, Architecture
- **Oracle Agents**: Code execution, verification
- **Execution Agents**: Tests, Security scanning
- **System Agents**: Checkpoints, Audit trails

### Anti-Hallucination Framework

- 5-level confidence system (AXIOM → UNKNOWN)
- Source attribution required
- Oracle verification for code
- Multi-model consensus

### 100% Local Data

- SQLite database for memory
- No external dependencies (except chosen LLM)
- Complete data sovereignty
- Works offline with Ollama

### Checkpoint & Rollback

- Automatic checkpoints before major changes
- Semantic integrity hashing
- One-command rollback

## 📚 CLI Commands

```bash
# Initialize ODIN
odin init

# Check status
odin status

# View configuration
odin config

# List agents
odin agents --verbose

# Sync with latest framework
odin sync
```

## 🏗️ Monorepo Structure

```
odin-framework/
├── apps/
│   ├── web/           # Next.js documentation site
│   └── docs/          # Additional docs app
├── packages/
│   ├── cli/           # CLI tool (this package)
│   ├── core/          # Shared logic
│   └── patch/         # Patch templates
├── docs/              # Markdown documentation
└── turbo.json         # Turborepo config
```

## 🌐 Website

Visit [odin-framework.vercel.app](https://odin-framework.vercel.app) for:

- Complete documentation
- Interactive examples
- Architecture guides
- Best practices

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](../../LICENSE)

## 🙏 Credits

Created by **Julien Gelée (Krigs)**

Inspired by:

- Constitutional AI (Anthropic)
- Multi-Agent Systems (Microsoft, LangChain)
- Aerospace & medical device engineering discipline

---

**⭐ Star us on GitHub!**

Built with ❤️ for the open-source AI community
