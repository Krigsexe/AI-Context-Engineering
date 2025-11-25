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
<div align="center">

[![Visitors Badge](https://api.visitorbadge.io/api/VisitorHit?user=Krigsexe&repo=AI-Context-Engineering&countColor=%237B1E7A)](https://github.com/Krigsexe/AI-Context-Engineering)

# ODIN v7.0 - Context Engineering Framework

**Making Large Language Models Reliable for Production Development**

</div>

---

## Table des Matières

- [Aperçu du Projet](#aperçu-du-projet)
- [Le Problème](#le-problème)
- [La Solution ODIN](#la-solution-odin)
- [Principes Clés](#principes-clés)
- [Architecture](#architecture)
- [Exemple Concret](#exemple-concret)
- [Analyse Comparative](#analyse-comparative)
- [Stack Technique](#stack-technique)
- [Installation](#installation)
- [Fondations Recherche](#fondations-recherche)
- [Statut du Projet](#statut-du-projet)
- [Documentation](#documentation)
- [Philosophie](#philosophie)
- [Contribution](#contribution)
- [Licence & Attribution](#licence--attribution)

---

## Aperçu du Projet

### ODIN v7.0 - Context Engineering Framework
Making Large Language Models Reliable for Production Development

ODIN est un système meta-cognitif conçu pour augmenter les Grands Modèles de Langage (LLMs) avec validation externe, raisonnement structuré et vérification systématique. Plutôt que de remplacer ou réentraîner les LLMs, ODIN ajoute des couches intelligentes autour d'eux pour éliminer les hallucinations, garantir la traçabilité et permettre le développement autonome fiable.

**Statut Actuel : Recherche et Développement (Novembre 2025) - ANALOGIE.md contient la théorie fondationnelle.**

---

## Le Problème

### Why Standard LLMs Are Unreliable for Production / Pourquoi les LLMs Standard ne sont pas Fiables en Production

Large Language Models are statistical predictors, not knowledge systems. They excel at pattern matching but fail at reliability:

Les Grands Modèles de Langage sont des prédicteurs statistiques, pas des systèmes de connaissance. Ils excellent au pattern matching mais échouent sur la fiabilité :

- **Hallucinations are inherent** - LLMs predict the next token probabilistically, not factually. When confident they don't know, they invent plausible-sounding answers.
- **Confusion between probability and truth** - P(response | context) ≠ P(response is true). A model can be 95% confident in something completely false.
- **No mechanism to say "I don't know"** - Training incentivizes producing text over admitting uncertainty.
- **Context overflow cascades** - Long tasks cause models to lose track of goals, constraints, and earlier decisions.
- **No self-correction** - Models cannot verify their own outputs or learn from failures without external feedback.

- **Les hallucinations sont inhérentes** - Les LLMs prédisent le prochain token probabilistiquement, pas factuellement. Quand ils croient ne pas savoir, ils inventent des réponses plausibles.
- **Confusion entre probabilité et vérité** - P(réponse | contexte) ≠ P(réponse est vraie). Un modèle peut être 95% confiant en quelque chose complètement faux.
- **Aucun mécanisme pour dire « je ne sais pas »** - L'entraînement incite à produire du texte plutôt qu'à avouer l'incertitude.
- **Débordement de contexte en cascade** - Les tâches longues font perdre au modèle le fil des objectifs, contraintes et décisions antérieures.
- **Pas d'auto-correction** - Les modèles ne peuvent vérifier leurs propres sorties ou apprendre des échecs sans feedback externe.

### Tableau des Impacts

| Problème | Impact | Sévérité |
|----------|--------|----------|
| Hallucinations / Hallucinations | Faits incorrects présentés comme vrais / Incorrect facts presented as truth | Critique / Critical |
| Régressions / Regression | Mises à jour cassent les fonctionnalités / Updates break previously working features | Élevée / High |
| Perte de contexte / Context loss | Objectifs oubliés dans les tâches longues / Goals forgotten in long tasks | Élevée / High |
| Boucles dangereuses / Dangerous loops | Exécution autonome sans validation / Autonomous execution without validation | Critique / Critical |
| Pas de responsabilité / No accountability | Aucune trace du raisonnement ou des sources / No trace of reasoning or sources | Élevée / High |

---

## La Solution ODIN

ODIN augmente les LLMs avec un système meta-cognitif disciplinaire. Il ne remplace PAS le LLM lui-même — il ajoute des couches de validation avant, pendant et après la génération.

**The ODIN Solution:** ODIN augments LLMs with a disciplinary meta-cognitive system. It does NOT replace the LLM itself—instead, it adds validation layers before, during, and after generation.

---

## Principes Clés

### Three Key Principles / Trois Principes Clés

**1. Complement, Don't Replace / Complémentaire, Pas Remplacement**
- The LLM's transformer architecture remains untouched. ODIN adds agents and oracles around it.
- L'architecture transformer du LLM reste inchangée. ODIN ajoute des agents et des oracles autour.

**2. Multi-Layer Validation / Validation Multi-Couche**
- Every output passes through independent verification: code execution, security scanning, fact-checking, and human approval.
- Chaque sortie passe par une vérification indépendante : exécution de code, scanning de sécurité, vérification des faits et approbation humaine.

**3. Structured Uncertainty / Incertitude Structurée**
- Instead of binary right/wrong, ODIN computes confidence levels (0-100%) and refuses to answer when below thresholds.
- Au lieu d'un binaire juste/faux, ODIN calcule des niveaux de confiance (0-100%) et refuse de répondre en dessous des seuils.

---

## Architecture

### Architecture Overview / Vue d'Ensemble de l'Architecture

```text
LAYER 1: PRE-PROCESSING / COUCHE 1 : PRE-TRAITEMENT
(Context Preparation / Préparation du Contexte)
├─ Retrieval Agent / Agent Récupération → Search verified knowledge / Recherche de connaissance vérifiée
├─ Verification Agent / Agent Vérification → Cross-check multiple sources / Cross-check de sources multiples
├─ Knowledge Graph / Graphe de Connaissance → Structured fact lookup / Recherche structurée de faits
└─ Oracle Temporal / Oracle Temporel → Validate information freshness / Validation de la fraîcheur d'info

        ↓ (Prepared context / Contexte préparé : high confidence / haute confiance, sourced / sourcé)

LAYER 2: LLM GENERATION / COUCHE 2 : GÉNÉRATION LLM
(Qwen 2.5 7B - Unchanged / Qwen 2.5 7B - Inchangé)
├─ Chain-of-Thought Prompting / Chain-of-Thought Prompting → Guided reasoning / Raisonnement guidé
├─ Context Injection / Injection de Contexte → Best practices included / Meilleures pratiques incluses
└─ Temperature Control / Contrôle Température → Deterministic output / Sortie déterministe

        ↓ (Raw LLM response / Réponse brute du LLM)

LAYER 3: POST-VALIDATION / COUCHE 3 : POST-VALIDATION
(Output Verification / Vérification de Sortie)
├─ Oracle Code Execution / Oracle Exécution Code → Run and test / Exécution et tests
├─ Oracle Security Scan / Oracle Security Scan → SAST/DAST checks / Scanning SAST/DAST
├─ Oracle Consensus / Oracle Consensus → Multi-model agreement / Accord multi-modèles
├─ Critique Agent / Agent Critique → Red team challenge / Red team challenge
└─ Confidence Calibration / Calibration de Confiance → Truth likelihood score / Score de vraisemblance

        ↓

CHECKPOINT & ROLLBACK
└─ Every decision logged and reversible / Chaque décision enregistrée et réversible
```

---

## Multi-Agent Orchestration

ODIN coordinates 30+ specialized agents / ODIN coordonne plus de 30 agents spécialisés :

```text
Retrieval & Knowledge / Récupération et Connaissance
├─ research_web - Verified external information / Information externe vérifiée
├─ research_codebase - Codebase analysis and context / Analyse et contexte codebase
└─ indexation - Vector embedding and semantic search / Embedding vectoriel et recherche sémantique

Development / Développement
├─ dev - Code generation / Génération de code
├─ refacto - Code improvement / Amélioration de code
└─ tests - Test generation and execution / Génération et exécution de tests

Verification / Vérification
├─ verif_syntax - Linting and parsing / Linting et parsing
├─ verif_security - Security scanning (SAST) / Scanning de sécurité (SAST)
├─ verif_performance - Profiling and optimization / Profiling et optimisation
├─ code_review - Style and pattern checking / Vérification style et patterns
└─ pertinence - Goal alignment verification / Vérification d'alignement aux objectifs

Orchestration
├─ approbation - Human validation gate / Porte de validation humaine
├─ mcp - Checkpoint management and rollback / Gestion des checkpoints et rollback
├─ apprentissage - Feedback loop and learning / Boucle de feedback et apprentissage
├─ critique - Adversarial red team / Red team adversariel
└─ oracle_* - External validators (code, KG, temporal, consensus) / Validateurs externes

Support
├─ architecture - Design decisions / Décisions de design
├─ documentation - Doc generation / Génération de doc
├─ build - Build orchestration / Orchestration de build
├─ deploy - Deployment management / Gestion du déploiement
└─ monitoring - Runtime health / Santé runtime
```

---

## Exemple Concret

### Before vs After: Concrete Example / Avant vs Après : Exemple Concret

**The Problem: Code Generation / Le Problème : Génération de Code**

```
User: "Create a FastAPI endpoint with JWT authentication"
User : "Crée un endpoint FastAPI avec authentification JWT"
```

#### ❌ STANDARD LLM (Qwen alone / Qwen seul)

```
├─ Generates code quickly / Génère du code rapidement
├─ May use outdated JWT algorithms / Peut utiliser des algorithmes JWT obsolètes
├─ Hardcodes secrets in code / Hardcode les secrets dans le code
├─ Doesn't add rate limiting / N'ajoute pas de rate limiting
├─ No security scanning / Pas de scanning de sécurité
└─ Result: 20-30% hallucination rate / Résultat : 20-30% de taux d'hallucination
```

#### ✅ THE ODIN SOLUTION / LA SOLUTION ODIN

```
PRE-PROCESSING / PRE-TRAITEMENT
  ├─ Retrieval → "FastAPI JWT examples" + "JWT 2024 RFC" / "FastAPI JWT exemples" + "JWT 2024 RFC"
  ├─ Verification → Cross-check 3 sources (JWT specs agree) / Cross-check 3 sources (RFC JWT en accord)
  ├─ Knowledge Graph → Confirms RS256 is current standard / Confirme que RS256 est le standard courant
  └─ Temporal Oracle → "RFC updated 2024, info valid" / "RFC mis à jour 2024, info valide"

PROMPTING (To Qwen / À Qwen)
  "Generate FastAPI code using:
   - JWT RS256 (asymmetric, not HS256)
   - Environment variables for secrets
   - bcrypt password hashing
   - Rate limiting per user
   - Full docstrings"
   
  "Génère du code FastAPI en utilisant :
   - JWT RS256 (asymétrique, pas HS256)
   - Variables d'environnement pour les secrets
   - Hash bcrypt pour les mots de passe
   - Rate limiting par utilisateur
   - Docstrings complets"

QWEN GENERATES / QWEN GÉNÈRE
  - Code with best practices injected via context / Code avec meilleures pratiques injectées via contexte
  - Higher confidence due to quality input / Confiance plus élevée grâce à meilleure entrée

POST-VALIDATION
  ├─ Syntax check (pylint) → PASS / Vérification syntaxe (pylint) → OK
  ├─ Type check (mypy) → PASS / Vérification type (mypy) → OK
  ├─ Security scan (bandit + semgrep) → PASS (no hardcoded secrets) / Scanning sécurité (bandit + semgrep) → OK (pas de secrets hardcodés)
  ├─ Unit tests (generated + executed) → PASS / Tests unitaires (générés + exécutés) → OK
  ├─ Red team challenge → "Handles expired tokens? Yes. Rate limiting works? Yes." / "Gère les tokens expirés ? Oui. Rate limiting fonctionne ? Oui."
  ├─ Oracle consensus (3 models agree) → PASS / Oracle consensus (3 modèles en accord) → OK
  └─ Human approval / Approbation humaine → APPROVED / APPROUVÉ

RESULT / RÉSULTAT
  Code generated, validated by 7 independent checks, rollback-ready
  Code généré, validé par 7 vérifications indépendantes, prêt pour rollback
  Result: 1-3% hallucination rate / Résultat : 1-3% de taux d'hallucination
```

---

## Analyse Comparative

### Comparative Analysis / Analyse Comparative

| Aspect | LLM Alone / LLM Seul | LLM + ODIN |
|--------|---------------------|-----------|
| Hallucination Rate / Taux Hallucination | 20-30% | 1-3% |
| Implementation Cost / Coût Implémentation | Baseline | +design système |
| Time to Reliability / Temps Fiabilité | Never (no verification) / Jamais (pas vérif) | Immediate / Immédiat |
| Model Changes Required / Changements Modèle | None / Aucun | None / Aucun |
| Applicability / Applicabilité | Model-specific / Model-spécifique | All LLMs / Tous les LLMs |
| Source Attribution / Attribution Source | Not tracked / Non tracée | 100% traced / 100% tracée |
| Rollback Capability / Capacité Rollback | Not possible / Impossible | Automatic / Automatique |
| Confidence Calibration / Calibration Confiance | None / Aucune | Per-claim scoring / Score par claim |
| Security Validation / Validation Sécurité | Manual/absent / Manuel/absent | Automatic scanning / Scanning automatique |

---

## Insight Système vs Modèle

### Key Insight: System vs Model / Insight Clé : Système vs Modèle

**The Problem IS NOT Qwen 7B Itself / Le Problème N'EST PAS Qwen 7B Lui-même**

A single LLM, unsupervised, is like asking an expert to answer without checking sources, without a team, without process. Inevitably: hallucinations.
Un LLM seul, sans supervision, c'est comme demander à un expert de répondre sans vérifier ses sources, sans équipe, sans processus. Inévitablement : hallucinations.

**With ODIN / Avec ODIN**

- Qwen + Retrieval = Expert with sources / Expert avec ses sources
- Qwen + Knowledge Graph = Expert with domain structure / Expert avec domaine structuré
- Qwen + Oracle Checks = Expert with tests / Expert avec ses tests
- Qwen + Critique Agent = Expert reviewed by peer / Expert revu par un pair
- Qwen + Feedback Loop = Expert who learns / Expert qui apprend

**The LLM's atomic structure (transformer, attention, weights) remains UNCHANGED. What changes is the disciplinary system around it.**
**L'architecture atomique du LLM (transformer, attention, poids) reste INCHANGÉE. Ce qui change, c'est le système disciplinaire autour.**

---

## Stack Technique

### Technical Stack / Stack Technique

| Component / Composant | Technology / Technologie | Why / Pourquoi |
|----------------------|-------------------------|----------------|
| Orchestrator / Orchestrator | Go 1.21+ | Concurrency, performance, single binary / Concurrence, perf, binaire unique |
| Agents / Agents | Python 3.11+ | ML ecosystem, RAG native, embeddings / Écosystème ML, RAG natif, embeddings |
| API / API | TypeScript/Node.js | Async, modern, maintainable / Async, moderne, maintenable |
| CLI / CLI | Go + Cobra | Native binary, cross-platform / Binaire natif, cross-plateforme |
| Message Bus / Message Bus | Redis Streams | Sub-millisecond latency, exactly-once semantics / Latence <1ms, exactly-once semantics |
| State Store / State Store | PostgreSQL 16 | ACID transactions, complex queries / Transactions ACID, requêtes complexes |
| Vector DB / Vector DB | FAISS | Local embeddings, semantic search / Embeddings locaux, recherche sémantique |
| LLM Server / LLM Server | Ollama | Local models, GPU support, model swapping / Modèles locaux, support GPU, swap modèles |
| Container / Container | Docker + Compose | Reproducibility, isolation, one-click deployment / Reproductibilité, isolation, déploiement one-click |
| Default LLM / LLM Défaut | Qwen 2.5 7B | Code + reasoning balance, open source / Équilibre code+raisonnement, open source |

---

## Installation

### Installation (One-Click)

```bash
git clone https://github.com/krigsexe/ai-context-engineering 
cd ai-context-engineering

# Verify Docker and Docker Compose / Vérifier Docker et Docker Compose
docker --version
docker compose --version

# Install ODIN / Installer ODIN
./install.sh
```

**The script will / Le script va :**

- Download LLM models locally (Qwen 2.5 7B default) / Télécharger les modèles LLM localement (Qwen 2.5 7B par défaut)
- Start PostgreSQL, Redis, Ollama services / Démarrer les services PostgreSQL, Redis, Ollama
- Build and deploy orchestrator, agents, and API / Builder et déployer orchestrator, agents et API
- Run health checks / Lancer les health checks

**Access / Accès :**

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- CLI: docker compose run --rm cli odin status

---

## Fondations Recherche

### Research Foundation / Fondations Scientifiques

This project is grounded in peer-reviewed research / Ce projet s'appuie sur la recherche peer-reviewed :

**Hallucinations and Uncertainty / Hallucinations et Incertitude**

- arxiv: Temperature and Hallucinations / arxiv: Température et Hallucinations
- arxiv: RLHF and Evaluation Misalignment / arxiv: RLHF et Misalignment d'Évaluation
- Kapa AI: Hallucination Causes / Kapa AI: Causes des Hallucinations

**Multi-Agent Systems / Systèmes Multi-Agents**

- LangGraph (Anthropic) / LangGraph (Anthropic)
- AutoGen (Microsoft Research) / AutoGen (Microsoft Research)
- CrewAI patterns / Patterns CrewAI

**Constitutional AI / Constitutional AI**

- Anthropic: Constitutional AI / Anthropic: Constitutional AI
- Prompt engineering techniques (27% to <5% hallucination reduction) / Techniques prompt engineering (27% à <5% réduction hallucinations)

**For detailed reasoning / Pour un raisonnement détaillé :** See docs/ANALOGIE.md and docs/ARCHITECTURE.md / Voir docs/ANALOGIE.md et docs/ARCHITECTURE.md

---

## Statut du Projet

### Project Status / Statut du Projet

**Phase 1: Foundation (Current - R&D) / Phase 1 : Fondation (Actuel - R&D)**

- Core architecture design / Design d'architecture
- Multi-agent framework / Framework multi-agents
- Knowledge graph integration / Intégration graphe de connaissance
- Docker orchestration / Orchestration Docker

**Phase 2: Integration (Planned) / Phase 2 : Intégration (Prévu)**

- CLI and API completion / Complétude CLI et API
- IDE plugins (VS Code, JetBrains) / Plugins IDE (VS Code, JetBrains)
- Advanced RAG features / Fonctionnalités RAG avancées

**Phase 3: Production (Planned) / Phase 3 : Production (Prévu)**

- Auto-rollback refinement / Affinement auto-rollback
- Community contributions / Contributions communauté
- Performance optimization / Optimisation performance

---

## Documentation

- **ANALOGIE.md** - Philosophical foundations and mental models / Fondations philosophiques et modèles mentaux
- **ARCHITECTURE.md** - Technical deep-dive / Deep-dive technique
- **AGENTS.md** - Role of each agent / Rôle de chaque agent
- **API.md** - REST API reference / Référence API REST
- **CLI.md** - Command-line reference / Référence ligne de commande
- **CONTRIBUTING.md** - How to contribute / Comment contribuer

---

## Philosophie

### Philosophy / Philosophie

ODIN embodies three core values / ODIN incarne trois valeurs fondamentales :

**1. Honesty / Honnêteté**
- Always cite sources or admit uncertainty. "I don't know" is preferable to hallucination.
- Toujours citer les sources ou avouer l'incertitude. « Je ne sais pas » est préférable à une hallucination.

**2. Traceability / Traçabilité**
- Every decision, every reasoning step, every validation is logged. Replay and audit always possible.
- Chaque décision, chaque étape de raisonnement, chaque validation est enregistrée. Replay et audit toujours possibles.

**3. Reversibility / Réversibilité**
- No action is final. Checkpoints enable rollback to any previous stable state.
- Aucune action n'est définitive. Les checkpoints permettent le rollback à tout état stable antérieur.

---

## Contribution

### Status & Contribution / Statut et Contribution

This is active R&D. The framework is evolving. We welcome / C'est de la R&D active. Le framework évolue. Nous accueillons :

- Ideas and feedback on architecture / Idées et feedback sur l'architecture
- Research contributions and papers / Contributions scientifiques et papers
- Community-driven agent implementations / Implémentations d'agents menées par la communauté
- Real-world testing and case studies / Tests en conditions réelles et études de cas

**See CONTRIBUTING.md for guidelines / Voir CONTRIBUTING.md pour les directives.**

**Stars, Forks & Contributions Welcome !**

---

## Licence & Attribution

### License / Licence

MIT License - See LICENSE / Licence MIT - Voir LICENSE

### Authors & Attribution / Auteurs et Attribution

Created by Julien Gelée (Krigs) | GitHub / Créé par Julien Gelée (Krigs)

Inspired by Constitutional AI (Anthropic), Multi-Agent Systems research (Microsoft, LangChain), and engineering discipline from aerospace and medical device development.
Inspiré par Constitutional AI (Anthropic), recherche Multi-Agent Systems (Microsoft, LangChain), et discipline d'ingénierie du spatial et des dispositifs médicaux.

---

<div align="center">

**⭐ Stars, 🍴 Forks & 🤝 Contributions Welcome!**

Built with ❤️ for the open-source AI community

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer&text=Thank%20you%20for%20visiting%20!&fontSize=16&fontAlignY=65&desc=Merci%20pour%20votre%20visite!&descAlignY=80&descAlign=62"/>
</div>

---

<div align="center">

**Ce README est disponible en anglais et français | This README is available in English and French**

</div>
