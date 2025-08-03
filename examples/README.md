# 🧪 ODIN v6.0 - Projets d'Exemple pour Tests End-to-End

Ce dossier contient trois projets d'exemple complets pour tester les capacités autonomes d'ODIN v6.0 :

## 📁 Structure des Projets

### 1. **React Application** (`react_app/`)
- **Framework** : React 18.2.0 avec hooks modernes
- **Dépendances** : Axios, Lodash (version volontairement obsolète pour tests DepGuard)
- **Fonctionnalités** :
  - Gestion d'état avec useState/useEffect
  - Appels API avec axios
  - Recherche en temps réel avec debounce
  - Calculs statistiques
  - Interface responsive

### 2. **Flask Application** (`flask_app/`)
- **Framework** : Flask 2.3.2 avec SQLAlchemy
- **Base de données** : SQLite (peut être configurée avec PostgreSQL/MySQL)
- **Fonctionnalités** :
  - API REST complète
  - Modèles User/Post avec relations
  - Validation de données
  - Gestion d'erreurs
  - Interface web intégrée

### 3. **FiveM Server** (`fivem_server/`)
- **Platform** : FiveM (GTA V Modding)
- **Langage** : Lua
- **Fonctionnalités** :
  - Resource personnalisée complète
  - Gestion des joueurs
  - Base de données (MySQL/SQLite)
  - Commandes administratives
  - Interface NUI (HTML/CSS/JS)

## 🎯 Matrice de Tests ODIN v6.0

### Test 1: Initialisation et Audit Initial
```bash
cd examples/react_app
odin init
# ✅ Scaffold automatique + audit initial réussi
```

### Test 2: Détection SIH (Semantic Integrity Hash)
```bash
# Modification délibérée du code
# Exemple : changer calculateUserStats() dans React
odin audit
# ✅ ODIN doit détecter le delta SIH
```

### Test 3: DepGuard - Vulnérabilités de Dépendances
```bash
# Introduction de dépendance vulnérable
# Exemple : lodash@4.17.20 (CVE connu)
odin audit --deps
# ✅ DepGuard doit signaler la vulnérabilité
```

### Test 4: Auto-Rollback sur Échec de Tests
```bash
# Simulation d'un test qui échoue
# Modification cassant la logique métier
odin test --auto-rollback
# ✅ ODIN doit auto-rollback sur échec
```

## 📊 Métriques Collectées

Les résultats des tests sont automatiquement attachés à `audit_report.md` :

- **Temps de réponse** : Init, Audit, TestGen, Rollback
- **Couverture de tests** : Pourcentage par projet
- **Détection SIH** : Précision et temps de calcul  
- **DepGuard** : Vulnérabilités détectées vs. base CVE
- **Succès d'auto-rollback** : Fiabilité et intégrité

## 🚀 Utilisation Rapide

### Prérequis
```bash
# Node.js pour React
node --version  # v18+

# Python pour Flask
python --version  # 3.9+
pip install -r flask_app/requirements.txt

# FiveM Server (optionnel)
# Télécharger depuis https://runtime.fivem.net/artifacts/fivem/build_server_windows/master/
```

### Lancement des Tests
```bash
# Test complet automatisé
odin test --matrix --all-projects

# Test individuel
odin test --project=react_app
odin test --project=flask_app  
odin test --project=fivem_server
```

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
# Flask
export DATABASE_URL="postgresql://user:pass@localhost/odin_test"
export SECRET_KEY="votre-clé-secrète"

# React
export REACT_APP_API_URL="http://localhost:5000"

# FiveM
export FIVEM_LICENSE_KEY="votre-licence-fivem"
```

### Personnalisation ODIN
```json
// .odin/config.json
{
  "test_matrix": {
    "parallel_execution": true,
    "timeout_per_test": 300,
    "auto_rollback_on_failure": true,
    "generate_coverage_report": true
  }
}
```

## 📈 Résultats Attendus

| Métrique | React App | Flask App | FiveM Server |
|----------|-----------|-----------|--------------|
| Init Time | < 30s | < 45s | < 60s |
| Test Coverage | > 85% | > 90% | > 75% |
| SIH Detection | < 5s | < 8s | < 10s |
| Rollback Success | 100% | 100% | 100% |

## 🐛 Dépannage

### Erreurs Communes
- **Node modules manquants** : `npm install` dans react_app/
- **Python dependencies** : `pip install -r requirements.txt`
- **Permissions FiveM** : Vérifier les ACE/Principal
- **Base de données** : Vérifier la connectivité DB

### Logs ODIN
```bash
tail -f .odin/learning_log.json
tail -f .odin/audit_report.md
```

## 🏆 Objectifs de Validation

✅ **Autonomie Complète** : ODIN gère l'intégralité du cycle de vie  
✅ **0% Régression** : Aucune casse grâce à SIH + TestGen  
✅ **100% Traçabilité** : Logs, checkpoints, signatures UUID  
✅ **Multi-Langages** : JS, Python, Lua supportés  
✅ **Mode Hors-Ligne** : Aucune dépendance Internet  
✅ **Feedback Utilisateur** : Évaluation contextuelle  
✅ **Sécurité Dépendances** : DepGuard actif  
✅ **Qualité Code** : Audit + lint automatique  

---

**Copyright © 2025 Make With Passion by Krigs**  
**License : MIT**  
**ODIN Version : 6.0.0-COMPLETE**
