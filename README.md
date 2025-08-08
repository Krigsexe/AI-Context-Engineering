ODIN v6.1 — Autonomous AI Codebase Assistant (Offline‑First)

FR + EN • Zero‑Regression • Anti‑Hallucination • Fully Auditable • No Cloud Dependency

Version: 6.1.0  •  License: MIT  •  Author: Make With Passion by Krigs

🇫🇷 Résumé (pour tous)

ODIN est un cadre open‑source qui sécurise l’usage d’un LLM (agent ou non) pour qu’un non‑développeur puisse concrétiser un projet sans régressions, sans hallucinations, et avec une traçabilité complète.

Idée centrale : Patch n’importe quel LLM grâce à des garde‑fous (CBI, Grounded‑Only, SIH, TestGen, Rollback, Audit), de sorte que le modèle ne puisse pas dériver en dehors du contexte validé.

Atouts clés

✅ CBI — Clarify‑Before‑Iterate : si un point est ambigu, ODIN pose des questions et attend votre OK avant d’agir.

✅ Grounded‑Only : le modèle ne s’appuie que sur des sources locales vérifiées (code, docs MCP en cache, feedback validé).

✅ Offline‑First : pas d’Internet en exécution standard → reproductible, auditable, souverain.

✅ Anti‑régression : backups atomiques + rollback automatique en cas d’échec.

✅ Intégrité forte : SHA‑256 + SIH (Semantic Integrity Hash basé AST) → la structure logique est garantie.

✅ TestGen : génération de tests (unitaires/intégration) pour fiabiliser chaque évolution.

✅ Audit : rapport clair de l’état du projet et de ses empreintes de contrôle.

Pour qui ?

Créateurs solo, PM, no‑code/low‑code, TPE/PME : livrer des features sans surprises.

Équipes techniques : cadre de sûreté pour intégrer un LLM sans risque de dérive.

🇬🇧 TL;DR (for everyone)

ODIN is an open‑source framework that hardens any LLM (agentic or not) so non‑developers can ship features without regressions, without hallucinations, and with full auditability.

Highlights

✅ CBI — Clarify‑Before‑Iterate: if something’s unclear, ODIN asks first and waits for approval.

✅ Grounded‑Only: model only uses verified local sources (codebase, cached MCP docs, validated feedback).

✅ Offline‑First: no Internet at runtime → reproducible, auditable, sovereign.

✅ Zero‑regression mindset: atomic backups + automatic rollback on failures.

✅ Strong integrity: SHA‑256 + SIH (AST‑based semantic hashing).

✅ TestGen: unit/integration tests generated to secure changes.

✅ Audit: clear health report and integrity fingerprints.

🧠 Principes & Garanties / Principles & Guarantees

CBI — Clarify‑Before‑Iterate (règle prioritaire)

Si une consigne est ambiguë, risquée ou impacte l’historique, ODIN liste les inconnues, pose des questions fermées, puis attend la validation explicite (✅/⚠️/❌) avant toute itération.

Grounded‑Only (Sources bornées)

Exécution standard sans Internet. Sources autorisées : code local, docs officielles MCP en cache, retours utilisateurs validés.

Intégrité & Réversibilité

Double vérification : SHA‑256 + SIH.

Backups atomiques avant modification, rollback auto si tests/feedback négatifs.

Traçabilité & Transparence

AI_CHECKPOINT.json (état), learning_log.json (journal), audit_report.md (rapport), commits signés/horodatés.

Instance unique & Liaisons complètes

.odin/odin.lock pour empêcher les instances multiples.

Validation des liaisons : chaînes d’appels, endpoints/handlers, modèles DB, variables d’env, intégrations.

🧩 Architecture (monorepo)

.odin/
  ├─ AI_CHECKPOINT.json      # état courant & intégrité
  ├─ config.json             # paramètres (SLO, router, policies)
  ├─ learning_log.json       # journal d’apprentissage
  ├─ audit_report.md         # rapport d’audit
  ├─ backups/                # sauvegardes atomiques
  └─ docs_cache/             # docs officielles MCP hors‑ligne
odin/
  ├─ cli.py                  # CLI (init, audit, rollback)
  ├─ integrity.py            # SHA‑256 + SIH (AST)
  ├─ audit_engine.py         # génération du rapport
  ├─ checkpoint.py           # scaffold + fichiers d’état
  └─ utils.py                # utilitaires
plugins/                     # extensions (ex: DepGuard, ContextGuard)
tests/                       # tests unitaires / intégration
README.md, LICENSE, CHANGELOG.md, SECURITY.md, pyproject.toml

🚀 Démarrage rapide (FR)

Prérequis : Python 3.10+ (recommandé 3.11)

# 1) Installer ODIN localement
pip install -e .

# 2) Vérifier la version
odin --version

# 3) Initialiser le projet (crée backup + fichiers .odin)
odin init

# 4) Lancer un audit d’intégrité
odin audit --full    # ou: odin audit

# 5) Créer votre demande dans TASKS.md (exemple)
echo "Ajouter une fonction validate_email() + tests" >> TASKS.md

# 6) Laisser ODIN poser ses QUESTIONS (CBI)… puis répondez ✅/⚠️/❌

Exemple concret (non‑développeur)

Vous décrivez en une phrase ce que vous voulez (ex.: « Ajoute une validation d’email avec tests unitaires »).

ODIN pose 3–5 questions simples (format attendu, lib acceptées, cas limites…).

Vous répondez par oui/non ou choix A/B.

ODIN crée un backup, modifie le code, génère des tests, exécute, puis documente.

En cas d’échec → rollback immédiat et rapport clair.

🚀 Quick Start (EN)

Requirements: Python 3.10+ (preferably 3.11)

pip install -e .
odin --version
odin init
odin audit --full    # or: odin audit

echo "Add validate_email() with unit tests" >> TASKS.md
# ODIN will ask CBI questions → answer and approve before execution

🛠️ CLI (v6.1, minimal)

odin init            # crée le scaffold .odin + premier backup
odin audit [--full]  # calcule les empreintes (SHA‑256 + SIH) et produit .odin/audit_report.md
odin rollback        # restaure le dernier backup atomique

D’autres sous‑commandes (TestGen, DepGuard, ContextGuard, Router…) peuvent exister selon votre version.

⚙️ Configuration (.odin/config.json)

{
  "version": "6.1.0",
  "slo": { "hallucination_max_rate": 0.005 },
  "router": {
    "low":  { "reasoning_effort": "minimal",  "double_pass": false, "grounded_only": true },
    "med":  { "reasoning_effort": "standard", "double_pass": true,  "grounded_only": true },
    "high": { "reasoning_effort": "max",      "double_pass": true,  "grounded_only": true }
  },
  "allowed_tools": ["local_rag","unit_tests","integrity_check"],
  "schema_guard": { "enabled": true }
}

slo.hallucination_max_rate : objectif de taux d’hallucination (SLO) visé.

router : profils d’effort de raisonnement (double‑pass, grounded_only).

allowed_tools : outils autorisés localement.

schema_guard : validation de schémas/contrats (si applicable).

🧪 Tests

python -m pytest -q

Astuce: créez un requirements-dev.txt avec pytest (et pytest-cov si besoin) pour standardiser l’installation.

🔐 Anti‑Hallucination & Anti‑Régression — Comment ça marche ?

Grounded‑Only : ODIN ne produit que ce qu’il peut justifier par des sources validées (code/doc cache/feedback).

CBI : ODIN s’arrête et questionne dès qu’une ambiguïté/risk est détectée.

SIH (AST) : deux codes logiquement identiques → même hash, même intégrité.

TestGen : les chemins critiques sont couverts par des tests.

Backups + Rollback : si un test échoue, retour état n‑1 immédiat.

Audit : état, empreintes, recommandations → tout est traçable.

🧭 Bonnes pratiques (FR/EN)

Décrivez votre demande en langage simple, en listant 3 critères d’acceptation.

Répondez aux questions CBI sans ambigüité (oui/non, A/B, valeurs concrètes).

Validez chaque jalon. N’avancez pas si un doute persiste.

Conservez le dépôt offline tant que possible pour la reproductibilité.

❓ FAQ

Q. Puis‑je utiliser Internet ?R. En mode standard, non. ODIN est offline‑first. Vous pouvez autoriser ponctuellement une consultation officielle (docs langage/framework), qui sera mise en cache.

Q. Et si je ne suis pas développeur ?R. C’est l’objectif d’ODIN : vous décrivez ce que vous voulez, ODIN pose les questions, sécurise, teste, documente et revient en arrière si nécessaire.

Q. Et si tout casse ?R. Rollback automatique au dernier backup + rapport d’audit pour comprendre pourquoi.

🤝 Contribuer

Issues : bugs, idées, questions.

PRs : tests inclus, documentation à jour, aucune régression.

Respectez CBI et la charte de contribution (à venir).

🗺️ Roadmap (extrait)

v6.1.x : durcissement CBI, packs de tests, exemples guided‑mode (non‑dev).

v6.2 : Adjudicator/Double‑Pass, Router étendu, TestGen enrichi, plugins DepGuard/ContextGuard par défaut.

📚 Glossaire

CBI : Clarify‑Before‑Iterate (poser des questions avant d’agir).

Grounded‑Only : pas de sources non vérifiées.

SIH : Semantic Integrity Hash (hash de l’AST pour garantir la logique).

TestGen : génération automatique de tests.

MCP cache : documentation officielle stockée hors‑ligne.

📄 Licence

MIT © 2025 Make With Passion by Krigs
