# ODIN v7.0 - Analyse du Repository Existant

**Date**: 2025-11-25
**Version analysee**: ODIN v6.1.0
**Objectif**: Refonte complete vers framework multi-agents orchestre

---

## 1. Etat des Lieux

### 1.1 Structure Actuelle

```
AI-Context-Engineering/
├── odin/                    # Package principal (monolithique)
│   ├── __init__.py          # Version 6.1.0
│   ├── cli.py               # CLI argparse (init, audit, rollback, start, backups)
│   ├── checkpoint.py        # Gestion checkpoints JSON
│   ├── router.py            # Profils de risque (low/med/high)
│   ├── integrity.py         # Hachage semantique (SIH)
│   ├── audit_engine.py      # Moteur d'audit
│   ├── backup.py            # Creation backups
│   ├── rollback.py          # Restauration backups
│   ├── learning.py          # Logging apprentissage
│   ├── context_guard.py     # Signature contexte
│   ├── utils.py             # Utilitaires (JSON, hash)
│   ├── grounded_only.py     # (non implemente)
│   ├── schema_guard.py      # (non implemente)
│   ├── tms.py               # (non implemente)
│   └── adjudicator.py       # (non implemente)
├── plugins/                 # Plugins (squelettes)
│   ├── contextguard/        # Validation contexte (placeholder)
│   └── depguard/            # Validation deps (placeholder)
├── testgen/                 # Generateur tests (placeholder)
├── tests/                   # Tests pytest (3 fichiers)
├── scripts/                 # Scripts bash
├── .odin/                   # Configuration runtime
│   ├── AI_CHECKPOINT.json   # Etat checkpoint
│   ├── config.json          # Configuration
│   ├── learning_log.json    # Log apprentissage
│   ├── audit_report.md      # Rapport audit
│   └── backups/             # Sauvegardes
└── .github/workflows/       # CI/CD
```

### 1.2 Fonctionnalites Implementees

| Fonctionnalite | Statut | Fichier | Notes |
|----------------|--------|---------|-------|
| CLI (init/audit/rollback/start) | OK | `cli.py` | Fonctionnel |
| Checkpoints JSON | OK | `checkpoint.py` | File-based, pas DB |
| Hachage semantique Python | OK | `integrity.py` | AST normalization |
| Backup/Restore | OK | `backup.py`, `rollback.py` | Copies physiques |
| Audit diff | OK | `audit_engine.py` | Detecte added/removed/modified |
| Profils risque | OK | `router.py` | low/med/high |
| Context signature | OK | `context_guard.py` | Hash global projet |
| Lock instance | OK | `checkpoint.py` | Fichier .lock |
| Tests unitaires | Partiel | `tests/` | 3 fichiers basiques |
| Plugins | Squelette | `plugins/` | Non implementes |
| Grounded-only | Non | `grounded_only.py` | Vide |
| Schema guard | Non | `schema_guard.py` | Vide |
| TMS (Truth Management) | Non | `tms.py` | Vide |
| Adjudicator | Non | `adjudicator.py` | Vide |
| Integration LLM | Non | - | Aucune |
| API REST | Non | - | Aucune |
| Docker | Non | - | Aucun |
| Multi-agents | Non | - | Monolithique |

### 1.3 Technologies Actuelles

- **Langage**: Python 3.9+
- **CLI**: argparse (basique)
- **Stockage**: Fichiers JSON locaux
- **Tests**: pytest
- **CI/CD**: GitHub Actions (basique)
- **Packaging**: setuptools via pyproject.toml

---

## 2. Ce qui doit etre CONSERVE

### 2.1 Concepts Fondamentaux (valeur metier)

1. **Philosophie anti-hallucination** - Core value d'ODIN
2. **Validation avant execution** - Principe non-negociable
3. **Rollback automatique** - Securite critique
4. **Tracabilite totale** - Audit trail
5. **Apprentissage verifie** - Knowledge management
6. **Instance unique** - Isolation projet

### 2.2 Code Reutilisable

| Module | Reutilisation | Adaptation Requise |
|--------|--------------|-------------------|
| `integrity.py` | 100% | Ajouter plus de types fichiers |
| `utils.py` | 90% | Abstraire paths |
| `backup.py` | 70% | Adapter pour volumes Docker |
| `audit_engine.py` | 80% | Enrichir metriques |
| `context_guard.py` | 80% | Etendre markers |

### 2.3 Regles de Configuration

Le fichier `.odin/config.json` contient des concepts cles:
- Profils de risque (low/med/high)
- SLO hallucination max (0.005)
- Outils autorises
- Schema guard

---

## 3. Ce qui doit etre REFACTORISE

### 3.1 Architecture Monolithique -> Multi-Agents

| Actuel | Cible v7.0 |
|--------|------------|
| Package Python unique | 30+ agents Docker independants |
| Execution sequentielle | Orchestration parallele |
| Stockage fichiers | PostgreSQL + Redis |
| CLI seule | API + CLI + IDE plugins |
| Pas de LLM | Ollama/vLLM integration |

### 3.2 Modules a Refactoriser

1. **`cli.py`** -> Agent CLI + API FastAPI
2. **`checkpoint.py`** -> Agent MCP + StateStore PostgreSQL
3. **`router.py`** -> Orchestrator + Router sophistique
4. **`audit_engine.py`** -> Agent Audit + Monitoring
5. **`learning.py`** -> Agent Apprentissage + Feedback loop

### 3.3 Flux de Donnees

**Actuel**:
```
User -> CLI -> File System -> Response
```

**Cible v7.0**:
```
User -> API/CLI -> Orchestrator -> Message Bus (Redis)
                        |
    +-------------------+-------------------+
    |         |         |         |         |
  Agent1   Agent2   Agent3   AgentN   LLM Server
    |         |         |         |         |
    +-------------------+-------------------+
                        |
              State Store (PostgreSQL)
```

---

## 4. Ce qui doit etre CREE (nouveau)

### 4.1 Infrastructure

| Composant | Description | Priorite |
|-----------|-------------|----------|
| `docker-compose.yml` | Orchestration services | P0 |
| `install.sh` | Installation one-click | P0 |
| PostgreSQL | Base etat persistant | P0 |
| Redis | Message bus + cache | P0 |
| Ollama | LLM server local | P0 |

### 4.2 Agents a Creer

| Agent | Role | Priorite |
|-------|------|----------|
| `orchestrator` | Hub central, routing | P0 |
| `dev` | Generation code | P0 |
| `mcp` | Checkpoints, rollback | P0 |
| `approbation` | Validation humaine | P0 |
| `pertinence` | Evaluation pertinence | P1 |
| `research_codebase` | Analyse codebase | P1 |
| `research_web` | Recherche web | P1 |
| `verif_syntax` | Validation syntaxe | P1 |
| `verif_security` | Scan securite | P1 |
| `tests` | Generation/execution tests | P1 |
| `code_review` | Review qualite | P1 |
| `documentation` | Maj documentation | P2 |
| `indexation` | Embeddings RAG | P2 |
| `refacto` | Refactoring code | P2 |
| `build` | Build projet | P2 |
| `deploy` | Deploiement | P2 |
| `monitoring` | Surveillance swarm | P2 |
| `architecture` | Analyse archi | P3 |
| `verif_performance` | Profiling | P3 |
| `apprentissage` | Feedback loop | P3 |

### 4.3 Shared Components

| Composant | Description |
|-----------|-------------|
| `llm_client.py` | Abstraction LLM (Ollama, vLLM, OpenAI) |
| `message_bus.py` | Redis Pub/Sub wrapper |
| `state_store.py` | SQLAlchemy ORM PostgreSQL |
| `vector_store.py` | FAISS/Milvus pour RAG |
| `base_agent.py` | Classe abstraite agent |

### 4.4 Interfaces

| Interface | Description |
|-----------|-------------|
| API FastAPI | REST endpoints |
| CLI Typer | Interface terminal |
| VS Code Extension | Integration IDE |

---

## 5. Risques et Points d'Attention

### 5.1 Risques Techniques

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Complexite Docker multi-services | Moyen | Documentation + healthchecks |
| Performance LLM local sans GPU | Haut | Supporter mode CPU (lent mais fonctionnel) |
| Synchronisation agents | Moyen | Redis Streams + timeouts |
| Migration donnees existantes | Bas | Script migration optionnel |

### 5.2 Points Critiques

1. **Compatibilite ascendante**: Conserver possibilite CLI standalone
2. **Installation one-click**: Doit fonctionner meme sans Docker (mode degrade)
3. **Offline-first**: Tout doit marcher sans internet apres setup initial
4. **Performances**: LLM 7B doit tourner sur machine 16GB RAM

---

## 6. Recommandations

### 6.1 Stack Technologique Recommandee

| Composant | Recommandation | Alternative |
|-----------|----------------|-------------|
| LLM local | Qwen 2.5 7B | DeepSeek Coder, Llama 3.1 |
| LLM server | Ollama | vLLM (si GPU avancee) |
| Orchestration | Custom Python + Redis | LangGraph, Celery |
| Message Bus | Redis Streams | RabbitMQ |
| Database | PostgreSQL 16 | SQLite (mode simple) |
| API | FastAPI | Flask |
| CLI | Typer | Click |
| IDE Plugin | VS Code d'abord | JetBrains plus tard |

### 6.2 Strategie de Migration

```
Phase 0: Analyse (CURRENT) ✓
Phase 1: Architecture + Structure
Phase 2: Infrastructure Docker
Phase 3: Core Components (shared + base_agent)
Phase 4: Orchestrator
Phase 5: API + CLI
Phase 6: Documentation + Tests E2E
```

---

## 7. Questions de Clarification

Avant de commencer Phase 1, j'ai besoin de validation sur les points suivants:

### Q1: LLM Local par Defaut
**Options:**
- A) Qwen 2.5 7B (recommande, bon equilibre)
- B) Llama 3.1 8B (Meta, tres populaire)
- C) DeepSeek Coder 6.7B (specialise code)
- D) Mistral 7B (francophone)

### Q2: Stack d'Orchestration
**Options:**
- A) Custom Python + Redis Pub/Sub (simple, controle total)
- B) LangGraph (framework LangChain, plus structure)
- C) Celery + Redis (battle-tested, complexe)

### Q3: Integrations IDE Prioritaires
**Options:**
- A) VS Code uniquement (Phase 1)
- B) VS Code + JetBrains (Phase 1)
- C) Aucune IDE (CLI/API seulement Phase 1)

### Q4: Mode Installation
**Options:**
- A) Docker obligatoire (simplifie setup)
- B) Docker + mode natif Python fallback
- C) Mode natif Python principal, Docker optionnel

### Q5: Niveau Documentation
**Options:**
- A) Debutant (pas a pas detaille)
- B) Intermediaire (concepts + exemples)
- C) Expert (reference technique)

### Q6: Conservation Code Existant
**Options:**
- A) Migration complete (refactoring total)
- B) Conserver odin/ comme mode "lite" + nouveau v7
- C) Fork: garder v6.1 sur branch, v7 sur main

---

## 8. Prochaines Etapes

En attente de validation:

1. [ ] Reponses aux questions Q1-Q6
2. [ ] Validation de ce document ANALYSIS.md
3. [ ] Autorisation de proceder a Phase 1

**Checkpoint**: `cp_000_analysis_complete`

---

*Document genere par Claude Code - Phase 0 ODIN v7.0*
