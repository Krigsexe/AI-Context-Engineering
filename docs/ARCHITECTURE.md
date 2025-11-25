# ODIN v7.0 - Complete System Architecture

**Version**: 7.0.0
**Status**: Design Phase
**Last Updated**: 2025-11-25

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Cognitive Architecture](#2-cognitive-architecture)
3. [Agent Catalog](#3-agent-catalog)
4. [Oracle System](#4-oracle-system)
5. [Confidence Framework](#5-confidence-framework)
6. [Infrastructure Stack](#6-infrastructure-stack)
7. [Data Flow](#7-data-flow)
8. [Reliability Metrics](#8-reliability-metrics)
9. [Implementation Phases](#9-implementation-phases)

---

## 1. System Overview

### 1.1 Core Principles

**User Sovereignty**: The user ALWAYS chooses their LLM provider, deployment model, and privacy level.

ODIN v7.0 is a **provider-agnostic hybrid cognitive system** combining:
- **Neural**: LLM-based agents (ANY provider: Anthropic, OpenAI, Google, Groq, Ollama, vLLM, HuggingFace, etc.)
- **Symbolic**: Knowledge graph for verified facts
- **Procedural**: Deterministic oracles for validation
- **Human**: Approval loops for critical decisions

See [LLM_PROVIDERS.md](./LLM_PROVIDERS.md) for complete provider list.
See [USER_CONFIGURATION.md](./USER_CONFIGURATION.md) for configuration guide.

### 1.2 Anti-Hallucination Philosophy

**Root causes addressed**:

| Cause | Mitigation |
|-------|------------|
| Statistical prediction != truth | External oracle validation |
| Lossy compression of data | Knowledge graph ground truth |
| No world model | Multi-source consensus |
| Reward for "always answer" | Reward for "I don't know" |

**Sources**:
- arxiv.org/html/2402.05201v1
- arxiv.org/abs/2509.04664
- anthropic.com/engineering/claude-code-best-practices

### 1.3 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      INTERFACE LAYER                             │
│         CLI (Go)  │  API (TypeScript)  │  VS Code Plugin        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Go)                             │
│    State Machine  │  Router  │  Message Bus Publisher           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MESSAGE BUS (Redis Streams)                     │
│        Channels: tasks:new, agent:*, response:*, oracle:*       │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   COGNITIVE   │   │    ORACLE     │   │   EXECUTION   │
│    AGENTS     │   │    SYSTEM     │   │    AGENTS     │
│   (Python)    │   │   (Hybrid)    │   │   (Python)    │
│               │   │               │   │               │
│ - intake      │   │ - code_exec   │   │ - dev         │
│ - retrieval   │   │ - knowledge   │   │ - refacto     │
│ - verification│   │ - temporal    │   │ - tests       │
│ - reasoning   │   │ - consensus   │   │ - build       │
│ - critique    │   │ - human       │   │ - deploy      │
│ - formulation │   │               │   │               │
│ - calibration │   │               │   │               │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                             │
│  PostgreSQL  │  Redis Cache  │  Neo4j KG  │  FAISS Vector      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM LAYER                                   │
│          Ollama (Qwen 2.5 7B, DeepSeek Coder, Llama)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Cognitive Architecture

### 2.1 Three-Layer Separation

**Principle**: Strict separation between Memory, Reasoning, and Generation.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  EPISODIC MEMORY (Experiences)                                  │
│  ├── PostgreSQL: tasks, actions, outcomes                       │
│  ├── Timestamp + source + confidence score                      │
│  └── Success/failure logs with context                          │
│                                                                  │
│  SEMANTIC MEMORY (Knowledge)                                    │
│  ├── FAISS: Vector embeddings with metadata                     │
│  │   └── Each embedding linked to: source, date, confidence     │
│  ├── Neo4j: Knowledge graph (structured facts)                  │
│  │   └── RDF triplets: (subject, predicate, object)            │
│  └── Version-controlled, auditable                              │
│                                                                  │
│  PROCEDURAL MEMORY (Know-how)                                   │
│  ├── CLAUDE.md rules (project-specific)                         │
│  ├── Validated patterns (from "Perfect" feedback)               │
│  └── Anti-patterns (from "False" feedback)                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REASONING LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SELECTIVE RETRIEVAL                                            │
│  ├── Query memory with strict filters                           │
│  ├── Rank by relevance AND confidence                           │
│  └── If no reliable info → STOP, ask user                       │
│                                                                  │
│  CROSS-VERIFICATION                                             │
│  ├── Multi-source consensus (3+ independent sources)            │
│  ├── Contradiction detection                                    │
│  └── Triangulation required for claims                          │
│                                                                  │
│  EXPLICIT CHAIN-OF-THOUGHT                                      │
│  ├── Each step documented                                       │
│  ├── Hypotheses clearly stated                                  │
│  └── Uncertainties quantified                                   │
│                                                                  │
│  INTERNAL CRITIQUE (Red Team)                                   │
│  ├── Separate agent challenges reasoning                        │
│  ├── Adversarial testing                                        │
│  └── Counter-argument search                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GENERATION LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  HONEST FORMULATION                                             │
│  ├── "I know X" (confidence 95%+)                               │
│  ├── "It seems Y" (confidence 60-95%)                           │
│  ├── "I don't know Z" (confidence <60%)                         │
│  └── Always cite sources                                        │
│                                                                  │
│  PRE-EMISSION VALIDATION                                        │
│  ├── Automatic fact-checking                                    │
│  ├── Unsourced claim detection                                  │
│  └── Emotional temperature alert                                │
│                                                                  │
│  COMPLETE TRACEABILITY                                          │
│  ├── Each sentence → source(s) + reasoning                      │
│  ├── Replay possible (how we got there)                         │
│  └── Post-facto rollback if error detected                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Confidence Levels

| Level | Range | Criteria | Response Behavior |
|-------|-------|----------|-------------------|
| 0 - AXIOM | 100% | Project rules, passing tests, validated feedback | Direct response |
| 1 - HIGH | 95%+ | 3+ sources, oracle validated, no contradictions | Direct + sources |
| 2 - MODERATE | 70-95% | 1-2 sources, partial validation | Response + caveats |
| 3 - UNCERTAIN | 40-70% | Single source, no validation | "It seems..." + ask |
| 4 - UNKNOWN | <40% | No reliable source, contradictions | REFUSE, ask questions |

---

## 3. Agent Catalog

### 3.1 Complete Agent List (40 agents)

#### Cognitive Agents (10)

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| `intake` | Analyze and decompose requests | User query | Atomic sub-questions, type, confidence requirement |
| `retrieval` | Search all memory layers | Sub-questions | Knowledge items with confidence scores |
| `verification` | Cross-validate sources | Knowledge items | Validated items, contradictions, freshness |
| `reasoning` | Chain-of-thought processing | Validated items | Reasoning chain with uncertainties |
| `critique` | Red team adversarial analysis | Reasoning chain | Attacks, counter-arguments, flaws |
| `formulation` | Generate final response | Validated reasoning | Response with sources, confidence |
| `calibration` | Score confidence accuracy | Historical data | Calibration adjustments |
| `pertinence` | Evaluate task relevance | Task context | Relevance score, recommendations |
| `approbation` | Human validation loop | Critical decisions | Approved/rejected with feedback |
| `apprentissage` | Learning from feedback | User feedback | Pattern updates, anti-patterns |

#### Oracle Agents (5)

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| `oracle_code` | Execute and validate code | Generated code | Lint, type, security, test results |
| `oracle_kg` | Knowledge graph lookup | Claims, entities | Verified facts, contradictions |
| `oracle_temporal` | Temporal validation | Claims with dates | Freshness, validity, outdated flags |
| `oracle_consensus` | Multi-model verification | Claims | Agreement score, divergences |
| `oracle_human` | Human escalation | Critical claims | Human verdict |

#### Execution Agents (15)

| Agent | Role | Priority |
|-------|------|----------|
| `dev` | Code generation | P0 |
| `refacto` | Code refactoring | P1 |
| `tests` | Test generation/execution | P0 |
| `verif_syntax` | Syntax validation | P0 |
| `verif_security` | Security scanning | P0 |
| `verif_performance` | Performance profiling | P2 |
| `code_review` | Code quality review | P1 |
| `documentation` | Documentation generation | P1 |
| `build` | Build automation | P1 |
| `deploy` | Deployment automation | P2 |
| `monitoring` | System monitoring | P1 |
| `indexation` | Embedding generation, RAG | P1 |
| `research_web` | Web research | P1 |
| `research_codebase` | Codebase analysis | P0 |
| `architecture` | Architecture analysis | P2 |

#### System Agents (10)

| Agent | Role |
|-------|------|
| `mcp` | Checkpoints, rollback |
| `backup` | Backup management |
| `integrity` | Semantic hash verification |
| `context_guard` | Context drift detection |
| `router` | Task routing |
| `scheduler` | Task scheduling |
| `health` | Health monitoring |
| `metrics` | Metrics collection |
| `logger` | Centralized logging |
| `config` | Configuration management |

---

## 4. Oracle System

### 4.1 Code Execution Oracle

```python
class CodeOracle:
    """
    Deterministic code validation (non-LLM)
    """
    def validate(self, code: str, language: str) -> ValidationResult:
        results = []

        # 1. Syntax (AST parsing)
        results.append(self.check_syntax(code, language))

        # 2. Linting (pylint, eslint)
        results.append(self.run_linter(code, language))

        # 3. Type checking (mypy, tsc)
        results.append(self.check_types(code, language))

        # 4. Security (bandit, semgrep)
        results.append(self.scan_security(code, language))

        # 5. Test execution (if tests provided)
        if has_tests(code):
            results.append(self.run_tests(code))

        return ValidationResult(
            passed=all(r.passed for r in results),
            details=results
        )
```

### 4.2 Knowledge Graph Oracle

**Technology**: Neo4j

**Schema**:
```cypher
// Nodes
(:Technology {name, version, release_date, eol_date})
(:Feature {name, description, added_version})
(:Deprecation {name, deprecated_version, removed_version})
(:BestPractice {name, domain, source, confidence})

// Relationships
(:Technology)-[:HAS_FEATURE]->(:Feature)
(:Technology)-[:DEPRECATED]->(:Deprecation)
(:BestPractice)-[:APPLIES_TO]->(:Technology)
```

**Query example**:
```cypher
MATCH (t:Technology {name: "Python"})-[:HAS_FEATURE]->(f:Feature)
WHERE f.added_version = "3.12"
RETURN f.name, f.description
```

### 4.3 Temporal Oracle

```python
class TemporalOracle:
    def validate(self, claim: str, source_date: datetime) -> TemporalResult:
        current_date = datetime.now()
        mentioned_date = extract_date(claim)

        # Rule 1: No future predictions
        if mentioned_date and mentioned_date > current_date:
            return TemporalResult(valid=False, reason="Future event")

        # Rule 2: Check freshness by domain
        age_days = (current_date - source_date).days
        domain = classify_domain(claim)

        freshness_limits = {
            "tech": 90,      # 3 months
            "security": 30,  # 1 month
            "legal": 180,    # 6 months
            "science": 365,  # 1 year
            "general": 365   # 1 year
        }

        if age_days > freshness_limits.get(domain, 365):
            return TemporalResult(
                valid=False,
                reason=f"Information outdated ({age_days} days)",
                recommendation="Re-verify with recent source"
            )

        return TemporalResult(valid=True)
```

### 4.4 Consensus Oracle

```python
class ConsensusOracle:
    def __init__(self):
        self.models = [
            OllamaModel("qwen2.5:7b"),
            OllamaModel("llama3.1:8b"),
            OllamaModel("deepseek-coder:6.7b")
        ]

    def verify(self, claim: str) -> ConsensusResult:
        prompt = f"Is this claim factually correct? Answer TRUE, FALSE, or UNCERTAIN.\nClaim: {claim}"

        responses = [m.generate(prompt, temperature=0) for m in self.models]
        parsed = [self.parse(r) for r in responses]

        agreement = max(parsed.count(v) for v in ["TRUE", "FALSE", "UNCERTAIN"]) / len(parsed)

        if agreement >= 0.67:  # 2/3 majority
            majority = max(set(parsed), key=parsed.count)
            return ConsensusResult(consensus=True, verdict=majority, confidence=agreement)

        return ConsensusResult(consensus=False, recommendation="Escalate to human")
```

---

## 5. Confidence Framework

### 5.1 Knowledge Item Schema

```python
@dataclass
class KnowledgeItem:
    content: str
    confidence: float  # 0.0 to 1.0
    sources: List[Source]
    verification_date: datetime
    context_constraints: Dict[str, str]  # e.g., {"python_version": ">=3.11"}
    contradictions: List[str]
    oracle_validations: List[ValidationResult]

@dataclass
class Source:
    url: str
    title: str
    date: datetime
    type: str  # "official_docs", "paper", "community", "internal"
    reliability_score: float

@dataclass
class Response:
    content: str
    confidence: float
    reasoning_chain: List[ReasoningStep]
    sources: List[KnowledgeItem]
    uncertainties: List[str]
    assumptions: List[str]

    def should_output(self) -> bool:
        return (
            self.confidence >= 0.6 and
            len(self.sources) >= 1 and
            all(s.confidence >= 0.5 for s in self.sources)
        )
```

### 5.2 Confidence Calculation

```python
def calculate_confidence(
    sources: List[KnowledgeItem],
    oracle_results: List[ValidationResult],
    contradiction_count: int,
    freshness_score: float
) -> float:

    # Base: average source confidence
    base = sum(s.confidence for s in sources) / len(sources) if sources else 0.0

    # Oracle bonus
    oracle_pass_rate = sum(1 for o in oracle_results if o.passed) / len(oracle_results) if oracle_results else 0.0
    oracle_bonus = oracle_pass_rate * 0.2

    # Contradiction penalty
    contradiction_penalty = min(contradiction_count * 0.15, 0.5)

    # Freshness factor
    freshness_factor = freshness_score * 0.1

    # Multi-source bonus
    multi_source_bonus = min(len(sources) * 0.05, 0.15) if len(sources) > 1 else 0.0

    final = base + oracle_bonus + freshness_factor + multi_source_bonus - contradiction_penalty

    return max(0.0, min(1.0, final))
```

---

## 6. Infrastructure Stack

### 6.1 Docker Compose Services

| Service | Image | Port | Role |
|---------|-------|------|------|
| postgres | postgres:16-alpine | 5432 | State store |
| redis | redis:7-alpine | 6379 | Message bus, cache |
| neo4j | neo4j:5.14 | 7474, 7687 | Knowledge graph |
| ollama | ollama/ollama | 11434 | LLM server |
| orchestrator | custom (Go) | 9000 | Task routing |
| api | custom (Node.js) | 8000 | REST API |
| agent-* | custom (Python) | - | Workers |
| sandbox | gvisor/runsc | - | Code execution |

### 6.2 Network Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    odin-network (bridge)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │postgres │  │  redis  │  │  neo4j  │  │ ollama  │   │
│  │  :5432  │  │  :6379  │  │  :7687  │  │ :11434  │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │         │
│       └────────────┴────────────┴────────────┘         │
│                         │                              │
│       ┌─────────────────┴─────────────────┐            │
│       │                                   │            │
│  ┌────┴────┐                        ┌─────┴────┐       │
│  │orchestra│                        │   api    │       │
│  │  :9000  │                        │  :8000   │       │
│  └────┬────┘                        └──────────┘       │
│       │                                                │
│  ┌────┴────────────────────────────────────────┐       │
│  │              AGENT POOL                      │       │
│  │  intake, retrieval, verification, ...       │       │
│  └──────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Data Flow

### 7.1 Complete Task Flow

```
1. USER INPUT
   │
   ▼
2. INTAKE AGENT
   ├── Decompose into atomic sub-questions
   ├── Classify type (factual, code, opinion, procedural)
   ├── Determine confidence requirement
   └── Output: TaskPlan with sub-tasks
   │
   ▼
3. RETRIEVAL AGENT
   ├── Query FAISS (semantic search)
   ├── Query Neo4j (structured facts)
   ├── Query PostgreSQL (episodic memory)
   └── Output: KnowledgeItems with confidence
   │
   ▼
4. VERIFICATION AGENT
   ├── Cross-source consensus check
   ├── Contradiction detection
   ├── Freshness validation
   └── Output: ValidatedKnowledge
   │
   ├── Confidence < 60%? ────────────────┐
   │                                     ▼
   │                              APPROBATION AGENT
   │                              ├── "I don't know"
   │                              ├── List uncertainties
   │                              └── Ask clarifying questions
   │
   ▼ (Confidence >= 60%)
5. REASONING AGENT
   ├── Chain-of-thought construction
   ├── Hypothesis documentation
   ├── Uncertainty quantification
   └── Output: ReasoningChain
   │
   ▼
6. CRITIQUE AGENT (Red Team)
   ├── Challenge reasoning
   ├── Find counter-arguments
   ├── Test edge cases
   ├── Check logical fallacies
   └── Output: CritiqueReport
   │
   ├── Critical flaws found? ────────────┐
   │                                     ▼
   │                              Return to REASONING
   │                              with critique feedback
   │
   ▼ (No critical flaws)
7. ORACLE VALIDATION
   ├── Code Oracle (if code)
   ├── Knowledge Graph Oracle
   ├── Temporal Oracle
   ├── Consensus Oracle
   └── Output: OracleResults
   │
   ├── Validation failed? ───────────────┐
   │                                     ▼
   │                              APPROBATION AGENT
   │                              ├── Explain failure
   │                              └── Request human validation
   │
   ▼ (Validation passed)
8. FORMULATION AGENT
   ├── Generate response
   ├── Cite sources
   ├── State confidence level
   ├── Mention limitations
   └── Output: FinalResponse
   │
   ▼
9. MCP AGENT (Checkpoint)
   ├── Log action
   ├── Save state
   ├── Prepare rollback
   └── Output: Checkpoint
   │
   ▼
10. RESPONSE TO USER
    │
    ▼
11. FEEDBACK LOOP
    ├── User: "Perfect" → APPRENTISSAGE archives pattern
    ├── User: "False" → APPRENTISSAGE logs anti-pattern, triggers rollback
    └── User: neutral → No action
```

---

## 8. Reliability Metrics

### 8.1 KPIs

| Metric | Formula | Target |
|--------|---------|--------|
| Hallucination Rate | incorrect_claims / total_claims | <1% |
| Calibration Error (ECE) | avg(abs(confidence - accuracy)) | <5% |
| Abstention Rate | refused_to_answer / total_questions | 15-25% |
| Source Citation Rate | responses_with_sources / total_responses | >95% |
| Oracle Agreement Rate | oracle_passed / oracle_attempted | >90% |
| Human Override Rate | human_corrections / system_decisions | <10% |
| Rollback Frequency | rollbacks / total_actions | <5% |

### 8.2 Monitoring Dashboard

```python
class ReliabilityMetrics:
    def __init__(self, db: PostgreSQL):
        self.db = db

    def hallucination_rate(self, period_days: int = 30) -> float:
        total = self.db.count("responses", period_days)
        incorrect = self.db.count("responses", period_days, feedback="False")
        return incorrect / total if total > 0 else 0.0

    def calibration_error(self, period_days: int = 30) -> float:
        responses = self.db.query("responses", period_days, has_feedback=True)
        errors = []
        for r in responses:
            accuracy = 1.0 if r.feedback == "Perfect" else 0.0
            errors.append(abs(r.confidence - accuracy))
        return sum(errors) / len(errors) if errors else 0.0

    def abstention_rate(self, period_days: int = 30) -> float:
        total = self.db.count("requests", period_days)
        refused = self.db.count("requests", period_days, status="refused")
        return refused / total if total > 0 else 0.0
```

---

## 9. Implementation Phases

### Phase 1: Infrastructure (Current)
- [x] Monorepo structure
- [ ] Docker Compose (postgres, redis, ollama)
- [ ] install.sh
- [ ] Migrate integrity.py

### Phase 2: Core Orchestrator
- [ ] Go orchestrator with state machine
- [ ] Redis Streams message bus
- [ ] Basic routing

### Phase 3: MVP Agents
- [ ] BaseAgent class
- [ ] intake, retrieval, verification
- [ ] dev, mcp, approbation
- [ ] oracle_code

### Phase 4: Extended Agents
- [ ] reasoning, critique, formulation
- [ ] oracle_kg (Neo4j integration)
- [ ] oracle_temporal, oracle_consensus
- [ ] calibration, apprentissage

### Phase 5: Interfaces
- [ ] TypeScript API (Fastify)
- [ ] Go CLI (Cobra)
- [ ] VS Code extension (Phase 2)

### Phase 6: Production Ready
- [ ] Full test suite (unit, integration, e2e)
- [ ] Documentation (EN/FR)
- [ ] CI/CD (GitHub Actions)
- [ ] Reliability metrics dashboard

---

*Document generated by Claude Code - ODIN v7.0*
*Architecture Version: 1.0*
