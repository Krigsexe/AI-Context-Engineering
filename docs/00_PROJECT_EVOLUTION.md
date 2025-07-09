# ODIN – Agent IA Autonome pour la Connaissance Universelle / Autonomous AI Agent for Universal Knowledge
**Par / By Julien Gelee aka Krigs**

---

## 🇫🇷 Présentation / 🇬🇧 Introduction

> **ODIN** (pour "connaissance universelle") est un projet open source né de 6 mois de travail intensif (parfois 17h/jour !), pensé, codé et documenté par moi, **Julien Gelee aka Krigs**. Son but : rendre l’IA accessible à tous, même sans savoir coder, en injectant un système de prompts hybrides et de gestion de contexte directement dans l’IDE.
>
> **ODIN** (for "universal knowledge") is an open-source project born from 6 months of intense work (sometimes 17h/day!), designed, coded, and documented by me, **Julien Gelee aka Krigs**. Its goal: make AI accessible to everyone, even non-coders, by injecting a hybrid prompt and context system directly into the IDE.
>
> **ODIN** est une boîte à outils pour structurer, fiabiliser et documenter n’importe quel projet IA, tout en neutralisant les dérives, les erreurs et les biais implicites des modèles. Si ce travail vous inspire, **laissez une étoile sur GitHub** ⭐️ !
>
> **ODIN** is a toolbox to structure, secure, and document any AI project, while neutralizing model drifts, errors, and implicit biases. If you appreciate this work, **leave a star on GitHub** ⭐️!

---

## 🇫🇷 Pourquoi ODIN ? / 🇬🇧 Why ODIN?

- **Référence à la connaissance universelle** : ODIN, dieu de la sagesse, symbolise l’ambition de rendre le savoir et la puissance de l’IA accessibles à tous.
- **Hybrid Prompt & Context** : Un système qui combine prompts structurés et gestion contextuelle pour guider l’IA, éviter les dérives, et garantir la cohérence du projet.
- **Pensé pour l’IDE** : ODIN s’intègre à la racine de n’importe quel projet, dans n’importe quel IDE, pour servir de socle à vos interactions IA.
- **Partage sincère** : Ce projet est le fruit d’un travail de terrain, sans promesse miracle, mais avec une exigence de robustesse, de documentation et d’accessibilité.

- **Reference to universal knowledge**: ODIN, god of wisdom, symbolizes the ambition to make knowledge and AI power accessible to all.
- **Hybrid Prompt & Context**: A system combining structured prompts and contextual management to guide AI, avoid drifts, and ensure project coherence.
- **IDE-centric**: ODIN integrates at the root of any project, in any IDE, as a foundation for your AI interactions.
- **Sincere sharing**: This project is the result of hands-on work, with no miracle promises, but with a demand for robustness, documentation, and accessibility.

---

## 🇫🇷 Genèse et Philosophie / 🇬🇧 Genesis and Philosophy

> Pendant 6 mois, j’ai exploré toutes les failles possibles de l’IA générative : dérives logiques, boucles, hallucinations, désynchronisations, perte de contexte… J’ai conçu ODIN pour que l’IA puisse s’auto-corriger, s’auto-documenter, et refuser toute action risquée ou ambiguë. L’objectif : permettre à des créatifs, entrepreneurs, ou passionnés, même sans bagage technique, de concrétiser leurs idées grâce à l’IA.
>
> For 6 months, I explored every possible flaw of generative AI: logical drifts, loops, hallucinations, desynchronizations, context loss... I designed ODIN so that AI can self-correct, self-document, and refuse any risky or ambiguous action. The goal: empower creatives, entrepreneurs, or enthusiasts, even without technical background, to bring their ideas to life with AI.

---

## 🇫🇷 Fonctionnalités Clés / 🇬🇧 Key Features

- **Prompts structurés et multirègles** (anti-biais, anti-hallucination, rollback, synchronisation doc/code)
- **Gestion avancée du contexte** (mémoire persistante, pruning, validation contextuelle)
- **Auto-correction et apprentissage** (logs, patterns, anti-patterns, feedback "Faux/Parfait")
- **Extension Chrome** (injection de prompts dans ChatGPT, Gemini, Claude…)
- **Sécurité & RGPD** (aucune donnée externe, logs locaux, conformité)
- **Documentation automatique** (toutes les actions tracées, synchronisation obligatoire)
- **Prêt à l’emploi pour non-développeurs** (aucune compétence technique requise pour démarrer)

- **Structured, multi-rule prompts** (anti-bias, anti-hallucination, rollback, doc/code sync)
- **Advanced context management** (persistent memory, pruning, contextual validation)
- **Self-correction and learning** (logs, patterns, anti-patterns, "Faux/Parfait" feedback)
- **Chrome extension** (prompt injection into ChatGPT, Gemini, Claude…)
- **Security & GDPR** (no external data, local logs, compliance)
- **Automatic documentation** (all actions traced, mandatory sync)
- **Ready for non-developers** (no technical skills required to start)

---

## 🇫🇷 6 Mois de Développement en Détail / 🇬🇧 6 Months of Development in Detail

### 1. **Idée de base / Core Idea**
- Canaliser l’IA dès la racine du projet, pour garantir robustesse, accessibilité, et cohérence.
- Make AI the backbone of any project, ensuring robustness, accessibility, and coherence.

### 2. **Exploration des dérives IA / Exploring AI Drifts**
- Étude des zones d’imaginaire, des boucles, des pertes de contexte, des rétroactions erronées.
- Studied hallucinations, loops, context loss, faulty feedback.

### 3. **Conception du système / System Design**
- Prompts hybrides, validation systématique, refus explicite en cas d’ambiguïté.
- Hybrid prompts, systematic validation, explicit refusal in case of ambiguity.

### 4. **Tests sur le terrain / Field Testing**
- 3 projets concrets livrés :
  - Site e-commerce web hosting auto-adaptatif
  - Serveur GTA RP piloté par prompts
  - Convertisseur Python → Blueprint pour Unreal Engine 5
- 3 real-world projects delivered:
  - Adaptive web hosting e-commerce site
  - GTA RP server fully prompt-driven
  - Python → Blueprint converter for Unreal Engine 5

### 5. **Itérations et supervision continue / Iterations and Continuous Supervision**
- Vibe coding, ajustements constants, documentation rigoureuse.
- Vibe coding, constant adjustments, rigorous documentation.

### 6. **Finalisation et ouverture open source / Finalization and Open Source Release**
- Publication sur GitHub pour aider la communauté, en particulier les non-développeurs.
- Released on GitHub to help the community, especially non-developers.

---

## 🇫🇷 Étude du dossier `/prompts` / 🇬🇧 `/prompts` Folder Study

### **Structure et Règles (FR/EN)**

- **ANTI-BIAIS & ANTI-HALLUCINATION**
  - Aucune réponse sans source vérifiable (projet ou utilisateur)
  - No answer without a verifiable source (project or user)
- **SYNCHRONISATION DOC/CODE**
  - Toute modification de code déclenche une vérification documentaire
  - Any code change triggers documentation sync
- **ISOLATION DES ARTEFACTS IA**
  - Checkpoints, logs, patterns, anti-patterns, auto-backup
  - Checkpoints, logs, patterns, anti-patterns, auto-backup
- **AUTO-CORRECTION & FEEDBACK**
  - Feedback binaire "Faux/Parfait" pour apprentissage
  - Binary feedback "Faux/Parfait" for learning
- **ROLLBACK & SÉCURITÉ**
  - Rollback instantané en cas d’erreur, logs détaillés
  - Instant rollback on error, detailed logs
- **VALIDATION UI/UX**
  - Tests visuels, feedback utilisateur, non-régression perceptuelle
  - Visual tests, user feedback, perceptual non-regression
- **GESTION DES DEMANDES AMBIGUËS**
  - Blocage et demande de clarification systématique
  - Systematic blocking and clarification request

### **Algorithmes et Méthodologies (FR/EN)**

- **UNIVERSAL_AI_PRODUCTION_READY**
  - Validation, analyse contextuelle, exécution atomique, apprentissage, archivage, feedback
  - Validation, contextual analysis, atomic execution, learning, archiving, feedback
- **AI_CHECKPOINT_MANAGER**
  - Sauvegarde/restaure l’état IA, fusion intelligente, purge automatique
  - Save/restore AI state, smart merge, auto-purge
- **ANTI_DERIVE_DOCUMENTAIRE_MANAGER**
  - Détection de doublons, audit documentaire, synchronisation obligatoire
  - Duplicate detection, doc audit, mandatory sync

---

## 🇫🇷 Esprit du projet (extrait du mail) / 🇬🇧 Project spirit (from the email)

> Ce projet n’est ni une promesse, ni une solution miracle. C’est le fruit d’un travail de terrain, en solitaire, que je souhaite partager sans prétention. L’idée : permettre à l’IA de fonctionner quasi seule, de s’auto-corriger, s’auto-documenter, et de minimiser ses erreurs via une boucle de vérification systématique.
>
> This project is neither a promise nor a miracle solution. It’s the result of hands-on, solitary work that I wish to share humbly. The idea: let AI work almost autonomously, self-correct, self-document, and minimize errors through a systematic verification loop.

---

## 🇫🇷 Structure du dépôt / 🇬🇧 Repository Structure

```
/
├── agent/             # Scripts pour l'agent local (cryptage, etc.) / Local agent scripts (encryption, etc.)
├── docs/              # Documentation détaillée / Detailed documentation
├── extension/         # Extension Chrome / Chrome extension
├── prompts/           # Prompts structurés / Structured prompts
│   ├── economic_models/ # Modèles économiques / Economic models
├── .gitignore         # Fichiers ignorés / Ignored files
├── LICENSE            # Licence / License
└── README.md          # Présentation générale / General overview
```

---

## 🇫🇷 Comment démarrer ? / 🇬🇧 Getting Started

1. **Clonez le dépôt / Clone the repo**  
   `git clone [URL_DU_REPO_GITHUB]`
2. **Ouvrez dans votre IDE / Open in your IDE**  
   VSCode, Cursor, etc.
3. **(Optionnel) Installez l’extension Chrome / (Optional) Install the Chrome extension**
4. **Utilisez les prompts du dossier `/prompts` / Use the `/prompts` folder prompts**
5. **Laissez une étoile si ce travail vous aide ! / Leave a star if this work helps you!** ⭐️

---

## 🇫🇷 Licence / 🇬🇧 License

MIT – 2025 Make With Passion by Krigs

---

## 🇫🇷 Remerciements / 🇬🇧 Acknowledgements

Merci à tous ceux qui croient au partage sincère, à la robustesse, et à l’accessibilité de l’IA pour tous.  
Thanks to all who believe in sincere sharing, robustness, and AI accessibility for everyone.

---

**Prêt à être glissé-déposé sur GitHub.**  
**Ready to drag-and-drop to GitHub.**

---

**Si ce projet vous inspire, laissez une étoile !**  
**If this project inspires you, leave a star!** ⭐️

---

*Julien Gelee aka Krigs – 2025*

