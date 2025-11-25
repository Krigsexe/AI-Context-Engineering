# ODIN v7.0 - Multi-Agent Orchestration for Reliable AI Development

[![CI](https://github.com/Krigsexe/AI-Context-Engineering/workflows/CI/badge.svg)](https://github.com/Krigsexe/AI-Context-Engineering/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ODIN** (Orchestrated Development Intelligence Network) is a multi-agent framework for reliable AI-assisted development with anti-hallucination features, provider-agnostic LLM support, and complete user sovereignty.

## 🎯 Key Features

- **Provider Agnostic**: Use ANY LLM provider - Ollama, Anthropic, OpenAI, Google, Groq, Together, DeepSeek, HuggingFace, or your own
- **Multi-Agent Architecture**: 10 specialized agents for different tasks
- **Anti-Hallucination**: 5-level confidence framework with oracle verification
- **Checkpoint/Rollback**: Full state preservation with semantic integrity hashing
- **100% Local Option**: Run entirely offline with Ollama

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Request                              │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      IntakeAgent                                 │
│              (Classify, Extract Context, Route)                  │
└─────────────────────────────────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   DevAgent      │ │  ReviewAgent    │ │  SecurityAgent  │
│   (Generate,    │ │  (Review,       │ │  (Scan, Check   │
│    Modify,      │ │   Quality)      │ │   Secrets)      │
│    Debug)       │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OracleCodeAgent                              │
│            (Execute, Verify, Validate - AXIOM Confidence)        │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Krigsexe/AI-Context-Engineering.git
cd AI-Context-Engineering

# Install Python package
pip install -e ".[dev]"

# Or use one-click install
./install.sh
```

### Configure LLM Provider

**Option 1: Local with Ollama (Recommended for privacy)**
```bash
# Install Ollama (https://ollama.ai)
ollama pull qwen2.5:7b
```

**Option 2: Cloud Provider**
```bash
# Set your preferred provider's API key
export ANTHROPIC_API_KEY="your-key"  # or
export OPENAI_API_KEY="your-key"     # or
export GROQ_API_KEY="your-key"       # etc.
```

### Basic Usage

```python
import asyncio
from agents import LLMClient, DevAgent, InMemoryStateStore

async def main():
    # Initialize
    client = LLMClient()  # Auto-detects available providers
    store = InMemoryStateStore()
    dev = DevAgent(llm_client=client, state_store=store)

    await dev.start()

    # Generate code
    result = await dev.run_task(
        "generate_code",
        {
            "requirements": "Create a function to calculate fibonacci",
            "language": "python",
        }
    )

    print(f"Success: {result.success}")
    print(f"Confidence: {result.confidence.name}")
    print(f"Code: {result.data['code']}")

    await dev.stop()

asyncio.run(main())
```

### CLI Usage

```bash
# List available agents
odin-agent list

# Run a task
odin-agent task dev generate_code -i '{"requirements": "Hello World function", "language": "python"}'

# Check available providers
odin-agent providers

# System health check
odin-agent health
```

## 📦 Available Agents

| Agent | Type | Description |
|-------|------|-------------|
| `IntakeAgent` | Cognitive | Request analysis, classification, routing |
| `DevAgent` | Cognitive | Code generation, modification, debugging |
| `RetrievalAgent` | Cognitive | Context gathering, codebase search |
| `ReviewAgent` | Cognitive | Code review, quality scoring |
| `ArchitectAgent` | Cognitive | Architecture decisions, design patterns |
| `OracleCodeAgent` | Oracle | Code execution verification (AXIOM confidence) |
| `TestAgent` | Execution | Test generation and execution |
| `SecurityAgent` | Execution | OWASP scanning, secret detection |
| `CheckpointAgent` | System | State preservation, rollback |
| `AuditAgent` | System | Activity logging, audit trails |

## 🔌 Supported LLM Providers

### Local (No API Key Required)
- **Ollama** - Default, recommended for privacy
- **vLLM** - High-performance serving
- **llama.cpp** - CPU inference
- **LocalAI** - OpenAI-compatible local server

### Cloud
- **Anthropic** (Claude)
- **OpenAI** (GPT-4, GPT-3.5)
- **Google** (Gemini)
- **Groq** (Fast inference)
- **Together.ai**
- **DeepSeek**
- **HuggingFace**
- **And more...**

## 🛡️ Confidence Framework

ODIN uses a 5-level confidence system:

| Level | Value | Description |
|-------|-------|-------------|
| **AXIOM** | 100% | Deterministic/verified (Oracle results) |
| **HIGH** | 95%+ | Very confident, verified |
| **MODERATE** | 70-95% | Reasonably confident |
| **UNCERTAIN** | 40-70% | Needs verification |
| **UNKNOWN** | <40% | Should not proceed |

## 📁 Project Structure

```
AI-Context-Engineering/
├── agents/                    # Python agent framework
│   ├── cognitive/            # Cognitive layer agents
│   ├── oracle/               # Oracle verification agents
│   ├── execution/            # Execution agents
│   ├── system/               # System management agents
│   └── shared/               # Shared infrastructure
│       ├── providers/        # LLM provider implementations
│       ├── llm_client.py     # Universal LLM client
│       ├── message_bus.py    # Redis Streams messaging
│       └── state_store.py    # PostgreSQL state management
├── orchestrator/             # Go orchestrator
├── api/                      # TypeScript REST/WebSocket API
├── tests/                    # Unit and integration tests
├── examples/                 # Usage examples
├── docs/                     # Documentation
└── docker-compose.yml        # Multi-service orchestration
```

## 🐳 Docker Deployment

```bash
# Start all services
docker compose up -d

# Start with local LLM (Ollama)
docker compose --profile local-llm up -d

# Start with knowledge graph (Neo4j)
docker compose --profile knowledge-graph up -d
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov-report=html

# Run specific test file
pytest tests/unit/test_integrity.py -v
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [LLM Providers Guide](docs/LLM_PROVIDERS.md)
- [Configuration Reference](docs/USER_CONFIGURATION.md)
- [Vision & Philosophy](docs/VISION.md)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a PR

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**⭐ Stars, 🍴 Forks & 🤝 Contributions Welcome!**

Built with ❤️ for the open-source AI community

[Report Bug](https://github.com/Krigsexe/AI-Context-Engineering/issues) · [Request Feature](https://github.com/Krigsexe/AI-Context-Engineering/issues)

</div>
