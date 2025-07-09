# 🇫🇷 Exemple d'utilisation ODIN / 🇬🇧 ODIN Usage Example

---

## 🇫🇷 Démarrer un projet ODIN

1. Clonez le dépôt principal ODIN et ouvrez-le dans votre IDE (VSCode, Cursor, etc.).
2. Créez un nouveau dossier projet (ex: `mon_projet/`).
3. Copiez le prompt de base depuis `/prompts/AUTONOMOUS_AI_PROMPT_ENGINEERING.md` dans votre projet ou référencez-le.
4. Ajoutez un fichier de contexte (ex: `context.md`) décrivant votre idée ou besoin.
5. Lancez votre agent LLM local ou connectez-vous à votre plateforme IA préférée.
6. Utilisez le prompt ODIN pour guider l'IA :
   - L'IA validera vos données, refusera toute tâche ambiguë, et documentera chaque action.

### Exemple de structure minimale :

```
mon_projet/
├── context.md           # Votre idée, besoin ou cahier des charges
├── prompt.md            # Copie ou lien vers le prompt ODIN
└── resultats.md         # L'IA documente ici chaque étape
```

---

## 🇬🇧 Start an ODIN Project

1. Clone the main ODIN repo and open it in your IDE (VSCode, Cursor, etc.).
2. Create a new project folder (e.g., `my_project/`).
3. Copy the base prompt from `/prompts/AUTONOMOUS_AI_PROMPT_ENGINEERING.md` into your project or reference it.
4. Add a context file (e.g., `context.md`) describing your idea or need.
5. Launch your local LLM agent or connect to your favorite AI platform.
6. Use the ODIN prompt to guide the AI:
   - The AI will validate your data, refuse any ambiguous task, and document every action.

### Minimal structure example:

```
my_project/
├── context.md           # Your idea, need, or requirements
├── prompt.md            # Copy or link to the ODIN prompt
└── results.md           # The AI documents each step here
```

---

## 🇫🇷 Astuce :
- Utilisez le feedback "Faux/Parfait" pour améliorer l'apprentissage de l'IA.
- Toute action est documentée automatiquement pour garantir la traçabilité.

## 🇬🇧 Tip:
- Use "Faux/Parfait" feedback to improve AI learning.
- Every action is automatically documented for traceability.

---

## 🇫🇷 Procédure autonome ODIN / 🇬🇧 ODIN Autonomous Procedure

### 🇫🇷 Fonctionnement général
- **Checkpoints IA (`AI_CHECKPOINT.json`)** : Sauvegarde automatique de l'état, des feedbacks, des patterns de réussite et d'échec, et du contexte courant.
- **Backup régulier (`AI_CHECKPOINT.bak.json`)** : Copie de sécurité automatique pour restaurer l'état en cas de problème.
- **Journal d'apprentissage (`learning_log.json`)** : Historique détaillé de chaque session, feedback utilisateur ("Faux" ou "Parfait"), actions prises, analyse d'erreur, patterns appris.
- **Feedback binaire** : Après chaque action, l'utilisateur donne un feedback "Faux" (correction immédiate, apprentissage) ou "Parfait" (validation, documentation, passage à l'étape suivante).
- **Auto-correction** : En cas de "Faux", l'IA analyse l'erreur, applique une correction, et met à jour ses patterns.
- **Documentation automatique** : Chaque action, correction, ou rollback est tracé dans les logs.

### 🇬🇧 General workflow
- **AI checkpoints (`AI_CHECKPOINT.json`)**: Automatic save of state, feedback, success/failure patterns, and current context.
- **Regular backup (`AI_CHECKPOINT.bak.json`)**: Automatic backup copy to restore state if needed.
- **Learning log (`learning_log.json`)**: Detailed history of each session, user feedback ("Faux" or "Parfait"), actions taken, error analysis, learned patterns.
- **Binary feedback**: After each action, user gives "Faux" (immediate correction, learning) or "Parfait" (validation, documentation, next step).
- **Self-correction**: On "Faux", the AI analyzes the error, applies a correction, and updates its patterns.
- **Automatic documentation**: Every action, correction, or rollback is logged.

---

### 🇫🇷 Exemple de fichiers générés / 🇬🇧 Example of generated files

- `AI_CHECKPOINT.json` : Checkpoint principal (voir exemple dans ce dossier)
- `AI_CHECKPOINT.bak.json` : Backup automatique
- `learning_log.json` : Journal d'apprentissage détaillé

---

*Pour plus de détails, voir la documentation principale ODIN.*
*For more details, see the main ODIN documentation.* 