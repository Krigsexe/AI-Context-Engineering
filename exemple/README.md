# 🇫🇷 Exemple d'utilisation ODIN / 🇬🇧 ODIN Usage Example

Ce dossier contient un exemple concret de l'application du framework ODIN. Il illustre comment l'agent IA interagit avec le projet, comment il apprend, et comment il maintient son état.

This folder contains a concrete example of the ODIN framework in action. It illustrates how the AI agent interacts with a project, how it learns, and how it maintains its state.

---

## 📂 Contenu du dossier / Folder Contents

-   **`AI_CHECKPOINT.json`**: Le fichier d'état principal de l'IA. Il contient la dernière action, le dernier feedback, ainsi que les patterns et anti-patterns appris par l'agent. C'est la mémoire vive de l'IA.
-   **`AI_CHECKPOINT.bak.json`**: Une copie de sauvegarde du checkpoint principal, créée automatiquement pour permettre une restauration en cas d'erreur ou de corruption.
-   **`learning_log.json`**: Le journal d'apprentissage détaillé. Chaque interaction (succès ou échec) y est consignée, permettant de suivre la progression de l'IA et de comprendre son processus de décision.
-   **`README.md`**: Ce fichier.

---

## 🤖 Procédure autonome ODIN / ODIN Autonomous Procedure

Le framework ODIN est basé sur une boucle de feedback et d'apprentissage continu. Voici comment les fichiers de cet exemple illustrent ce processus :

1.  **Action & Feedback**: L'agent IA effectue une action. L'utilisateur fournit un feedback binaire :
    -   `"Faux"`: L'action a échoué.
    -   `"Parfait"`: L'action a réussi.

2.  **Apprentissage et Correction**:
    -   En cas de **"Faux"**, l'agent analyse l'erreur (voir `error_analysis` dans `learning_log.json`), l'ajoute à ses `anti_patterns`, et tente une nouvelle approche.
    -   En cas de **"Parfait"**, l'agent sauvegarde la séquence d'actions comme un `pattern` de réussite pour une utilisation future.

3.  **Maintien de l'état**:
    -   Après chaque interaction, l'état de l'IA est sauvegardé dans `AI_CHECKPOINT.json`.
    -   L'historique complet est tracé dans `learning_log.json`.

Ce système permet à l'IA de devenir de plus en plus fiable et performante au fil du temps, en apprenant de ses propres expériences au sein du projet.

---

*Pour plus de détails sur comment démarrer avec ODIN, veuillez consulter le [README.md](../../README.md) principal.*

*For more details on how to get started with ODIN, please see the main [README.md](../../README.md).* 