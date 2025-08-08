# ODIN v6.1 – Autonomous AI Codebase Assistant (Offline-First)

ODIN v6.1 renforce v6.0 avec : **Grounded-Only**, **Double-Pass + Adjudicator**, **TMS**, **SLO anti-hallucination**, **Schema Guard**, et **Router** (budgets de risque).

## Installation (dev)
```bash
pip install -e .
odin --version
```

## Quick Start
```bash
odin init
odin audit --full
```

## Principes clés

- Zéro dépendance réseau en exécution
- Intégrité : SHA-256 + SIH (hash sémantique AST)
- Réversibilité : backups atomiques + rollback
- Traçabilité : checkpoints + learning log + audit

### `.odin/config.json`
```json
{
  "version": "6.1.0",
  "slo": { "hallucination_max_rate": 0.005 },
  "router": {
    "low": { "reasoning_effort": "minimal", "double_pass": false, "grounded_only": true },
    "med": { "reasoning_effort": "standard", "double_pass": true,  "grounded_only": true },
    "high": { "reasoning_effort": "max",      "double_pass": true,  "grounded_only": true }
  },
  "allowed_tools": ["local_rag", "unit_tests", "integrity_check"],
  "schema_guard": { "enabled": true }
}
```
