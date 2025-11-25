# ODIN v7.0 - Phase 0 Analysis Document

**Date**: 2025-11-25
**Current Version**: ODIN v6.1.0
**Target Version**: ODIN v7.0
**Status**: Awaiting validation before Phase 1

---

## 1. Current State Analysis / Analyse de l'Etat Actuel

### 1.1 Repository Structure

```
AI-Context-Engineering/
├── odin/                    # Monolithic Python package
│   ├── __init__.py          # v6.1.0
│   ├── cli.py               # CLI: init, audit, rollback, start, backups
│   ├── checkpoint.py        # JSON-based checkpoints
│   ├── router.py            # Risk profiles (low/med/high)
│   ├── integrity.py         # Semantic hashing (SIH) - CRITICAL
│   ├── audit_engine.py      # Audit engine
│   ├── backup.py            # Backup creation
│   ├── rollback.py          # Backup restoration
│   ├── learning.py          # Learning log
│   ├── context_guard.py     # Context signature
│   ├── utils.py             # Utilities (JSON, hash)
│   ├── grounded_only.py     # NOT IMPLEMENTED
│   ├── schema_guard.py      # NOT IMPLEMENTED
│   ├── tms.py               # NOT IMPLEMENTED
│   └── adjudicator.py       # NOT IMPLEMENTED
├── plugins/                 # Skeleton plugins
├── testgen/                 # Skeleton test generator
├── tests/                   # 3 pytest files
├── scripts/                 # Bash scripts
├── .odin/                   # Runtime config
└── .github/workflows/       # CI/CD
```

### 1.2 Implemented Features Status

| Feature | Status | File | Notes |
|---------|--------|------|-------|
| CLI (init/audit/rollback/start) | OK | `cli.py` | Functional |
| JSON Checkpoints | OK | `checkpoint.py` | File-based |
| Semantic Hashing (SIH) | OK | `integrity.py` | AST normalization |
| Backup/Restore | OK | `backup.py`, `rollback.py` | Physical copies |
| Audit diff | OK | `audit_engine.py` | Detects changes |
| Risk profiles | OK | `router.py` | low/med/high |
| Context signature | OK | `context_guard.py` | Global hash |
| Instance lock | OK | `checkpoint.py` | Lock file |
| Unit tests | Partial | `tests/` | 3 basic files |
| LLM Integration | NO | - | None |
| REST API | NO | - | None |
| Docker | NO | - | None |
| Multi-agents | NO | - | Monolithic |

---

## 2. Validated Technical Decisions / Decisions Techniques Validees

### 2.1 Multi-Language Stack

| Component | Language | Version | Justification |
|-----------|----------|---------|---------------|
| Orchestrator | Go | 1.21+ | Native concurrency (goroutines), performance, standalone binary |
| Agents | Python | 3.11+ | AI ecosystem (LangChain, transformers), RAG, embeddings |
| API | TypeScript | Node 20 LTS | Async performance, type safety, extensible |
| CLI | Go | 1.21+ | Native binary, cross-platform |

**Sources**: Go concurrency model, Python AI ecosystem dominance, TypeScript enterprise adoption

### 2.2 Infrastructure Stack

| Layer | Technology | Version | Role |
|-------|------------|---------|------|
| Message Bus | Redis Streams | 7.2+ | Pub/sub async, request/response |
| State Store | PostgreSQL | 16+ | Tasks, checkpoints, feedback (ACID) |
| Cache | Redis | 7.2+ | Session, hot data |
| Vector DB | FAISS | latest | Embeddings, RAG |
| LLM Server | Ollama | latest | Local models |
| Container | Docker Compose | 2.x | Multi-service orchestration |

### 2.3 Default LLM

- **Primary**: Qwen 2.5 7B (balance performance/resources)
- **Optional**: DeepSeek Coder 6.7B (code-specialized)
- **Extensible**: Llama 3.1 8B, Mistral 7B via `.env`

### 2.4 Migration Strategy

**Code to migrate**:
- `odin/integrity.py` -> `agents/shared/integrity.py` (semantic hashing, tested, quality code)
- Associated tests -> `tests/unit/agents/test_integrity.py`

**Code to abandon**:
- Current CLI (replaced by Go CLI)
- JSON checkpoints (replaced by PostgreSQL)
- Unimplemented modules (grounded_only, schema_guard, tms, adjudicator)

**Git strategy**:
```bash
# 1. Tag and preserve v6.1
git tag v6.1.0
git checkout -b legacy/v6.1

# 2. Main branch: new structure
git checkout main
# Migrate integrity.py
# Build new structure
```

---

## 3. Target Architecture / Architecture Cible

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERFACES                              │
│     CLI (Go)  |  API REST (TS/Fastify)  |  IDE Plugins      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR (Go)                           │
│   - State Machine (workflow FSM)                              │
│   - Router (task -> agent sequence)                           │
│   - Message Bus Publisher/Subscriber                          │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│               MESSAGE BUS (Redis Streams)                     │
│     Channels: tasks:new, agent:*, response:*                  │
└──────────────────────────┬───────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              30+ SPECIALIZED AGENTS (Python)                 │
│                                                              │
│  P0 (MVP):     dev, mcp, approbation, research_codebase     │
│  P1:           verif_syntax, verif_security, tests,         │
│                code_review, pertinence, research_web        │
│  P2:           documentation, indexation, refacto,          │
│                build, deploy, monitoring                    │
│  P3:           architecture, verif_performance,             │
│                apprentissage                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                             │
│   PostgreSQL 16  |  Redis 7  |  FAISS  |  Ollama            │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Anti-Hallucination Framework / Framework Anti-Hallucination

### 4.1 Root Causes (Validated Research)

1. **Pre-training architecture**: LLMs predict next token (statistical), not truth
2. **Probabilistic generation**: Even temp=0 does not eliminate hallucinations
3. **Dataset gaps**: Biased/incomplete data leads to plausible but false patterns
4. **Systemic issue**: Reward functions incentivize guessing over admitting uncertainty

**Sources**:
- arxiv.org/html/2402.05201v1
- arxiv.org/abs/2509.04664
- en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)

### 4.2 Defense-in-Depth (3 Layers)

| Layer | Techniques |
|-------|------------|
| Input | Query optimization, context filtering, verified source anchoring |
| Design | RAG, Chain-of-Thought prompting, separation research/generation |
| Output | Fact verification, guardrails, cite sources or "I don't know" |

**Sources**:
- redhat.com/en/blog/when-llms-day-dream-hallucinations-how-prevent-them
- kapa.ai/blog/ai-hallucination

### 4.3 ODIN Rules (Non-Negotiable)

```
ABSOLUTE RULES:
- ZERO hallucination: sources or "I don't know"
- ZERO deletion without validation
- ALWAYS ask if ambiguous
- ALWAYS checkpoint before major modification

WORKFLOW:
ANALYZE -> QUESTION -> PLAN -> VALIDATE -> IMPLEMENT (atomic) -> TEST -> CHECKPOINT -> DOCUMENT

FEEDBACK LOOP:
- "False" -> rollback + log + anti-pattern rule
- "Perfect" -> archive + favor pattern rule
```

---

## 5. Remaining Clarification Questions / Questions de Clarification

### Q1: Deployment Mode

**Question**: What is the deployment target?

| Option | Description | Impact |
|--------|-------------|--------|
| A | 100% local only (offline-first strict) | No network config, max privacy |
| B | Local + optional remote access (tunnel/VPN) | Network setup, auth required |
| C | Hybrid (local dev + optional cloud) | More complex architecture |

**Recommendation**: A (100% local) aligns with ODIN philosophy

---

### Q2: MVP Agents Priority

**Question**: Which agents are CRITICAL for MVP (v7.0.0)?

**Proposed MVP set (5 agents)**:
1. `research_codebase` - Analyze existing code
2. `dev` - Generate code
3. `verif_syntax` - Validate syntax
4. `mcp` - Checkpoints/rollback
5. `approbation` - Human validation

**Alternative**: All 30 agents in v1.0 (longer timeline)

| Option | Agents | Timeline |
|--------|--------|----------|
| A | MVP (5 agents) | Shorter, validate core first |
| B | Core (10 agents) | Medium |
| C | Full (30 agents) | Longer, complete from start |

---

### Q3: IDE Integration Priority

**Question**: IDE plugins in Phase 1?

| Option | Description |
|--------|-------------|
| A | VS Code only | Focus quality, largest market share |
| B | VS Code + JetBrains | Broader reach, more work |
| C | CLI/API only (IDE Phase 2) | Fastest MVP, defer plugins |

**Recommendation**: C (CLI/API first, IDE Phase 2)

---

### Q4: Tests & CI/CD

**Question**: Test coverage level?

| Option | Scope |
|--------|-------|
| A | Unit tests only | Fast feedback |
| B | Unit + Integration | Good coverage |
| C | Unit + Integration + E2E | Complete but slower |

**CI/CD**:
| Option | Platform |
|--------|----------|
| A | GitHub Actions | Native, simple |
| B | GitLab CI | Alternative |
| C | Manual | No automation |

**Recommendation**: B (Unit + Integration), A (GitHub Actions)

---

### Q5: Documentation

**Question**: Documentation scope?

**Languages**:
| Option | Languages |
|--------|-----------|
| A | English only | International reach |
| B | Bilingual EN/FR | Current style |
| C | Multilingual | More maintenance |

**Level**:
| Option | Target Audience |
|--------|-----------------|
| A | Expert (assumes Docker/Python/Go) | Minimal docs |
| B | Intermediate (explains concepts) | Balanced |
| C | Beginner (step-by-step) | Comprehensive |

**Recommendation**: B (EN/FR), B (Intermediate)

---

## 6. Implementation Phases / Phases d'Implementation

| Phase | Objective | Deliverables |
|-------|-----------|--------------|
| 0 | Analysis & Validation | This document, Q1-Q5 answers |
| 1 | Infrastructure | Monorepo structure, Docker Compose, install.sh |
| 2 | Orchestrator | Go orchestrator, router, state machine |
| 3 | Agents MVP | BaseAgent, dev, mcp, approbation agents |
| 4 | API | TypeScript/Fastify REST API |
| 5 | CLI | Go CLI with Cobra |
| 6 | Documentation | Full docs, tests, README |

---

## 7. Checkpoints

| ID | Phase | Description |
|----|-------|-------------|
| cp_000 | 0 | Analysis complete, decisions validated |
| cp_001 | 1 | Infrastructure ready, Docker works |
| cp_002 | 2 | Orchestrator functional |
| cp_003 | 3 | MVP agents operational |
| cp_004 | 4 | API endpoints working |
| cp_005 | 5 | CLI functional |
| cp_006 | 6 | Production ready |

---

## 8. Validated Decisions / Decisions Validees

**Status**: VALIDATED - Proceeding to Phase 1

| Question | Decision | Details |
|----------|----------|---------|
| Q1: Deployment | B+C | Local + remote access + hybrid cloud option |
| Q2: Agents | C | Full 30 agents, multi-purpose, user choice |
| Q3: IDE | A+C | VS Code primary, CLI/API first (IDE Phase 2) |
| Q4: Tests | C+A | Full coverage (Unit+Integration+E2E) + GitHub Actions |
| Q5: Docs | B+Expert | Bilingual EN/FR, Expert level |

### Final Architecture Decisions

1. **Deployment**: Hybrid architecture supporting 100% local, remote access, and cloud options
2. **Agents**: All 30 agents implemented, configurable per use case
3. **IDE**: VS Code extension planned, CLI/API prioritized for Phase 1
4. **Testing**: Complete test pyramid (unit, integration, e2e) with GitHub Actions CI/CD
5. **Documentation**: Bilingual EN/FR, targeting experienced developers

---

## 9. Phase 1 Ready / Phase 1 Pret

Checkpoint `cp_000_analysis_validated` complete.

Next: Phase 1 - Infrastructure & Foundations
- Monorepo structure creation
- Docker Compose configuration
- install.sh script
- Migration of integrity.py

---

*Document generated by Claude Code - ODIN v7.0 Phase 0*
*Validated: 2025-11-25*
