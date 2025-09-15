# 🚧 TiDB Hackathon - Système de Gestion de Tâches Intelligentes

Un système multi-agents utilisant LangGraph pour la gestion automatisée de tâches de construction avec base de données TiDB.

## 🎯 Vue d'ensemble

Ce projet implémente un système intelligent de gestion de tâches pour l'industrie de la construction, utilisant :
- **TiDB** comme base de données vectorielle distribuée
- **LangGraph** pour l'orchestration d'agents IA
- **MCP (Model Context Protocol)** pour l'intégration base de données
- **LangSmith** pour le monitoring et traçage des agents

## ✨ Fonctionnalités principales

### 🤖 Agents Intelligents
- **Supervisor** : Orchestration centrale des tâches et délégation
- **Planning** : Planification et programmation des tâches
- **Conflict** : Détection et résolution des conflits de ressources
- **Team Builder** : Allocation intelligente des équipes
- **Notifier** : Notifications et alertes automatisées
- **Executor** : Exécution et suivi des tâches

### 🎲 Spécialités du Code
- **Architecture multi-agents** avec LangGraph pour des workflows complexes
- **Base de données vectorielle** TiDB pour recherche sémantique avancée
- **Protocole MCP** pour interaction sécurisée avec la base de données
- **Traçage intelligent** avec LangSmith pour monitoring en temps réel
- **Gestion des conflits** automatisée pour optimisation des ressources
- **API RESTful** avec FastAPI pour intégration externe
- **Support multilingue** (français/anglais) dans les interactions

## 🚀 Installation et Configuration

### Prérequis
- Python 3.11+
- Base de données TiDB Cloud (ou instance locale)
- Compte LangSmith pour le monitoring
- Clé API Anthropic (Claude) ou XAI

### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2. Configuration de la base de données TiDB

#### 2.1 Configurer le fichier .env
Créez un fichier `.env` à la racine du projet avec vos informations TiDB :

```env
# TiDB Connection Settings
TIDB_HOST=your-tidb-host.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=your-username.root
TIDB_PASSWORD=your-password
TIDB_DATABASE=your-database-name

# AI API Keys
ANTHROPIC_API_KEY=sk-ant-api03-your-key
XAI_API_KEY=xai-your-key

# LangSmith Configuration (pour monitoring)
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=lsv2_pt_your-langsmith-key
LANGSMITH_PROJECT="your-project-name"
```

#### 2.2 Initialiser le schéma de base de données
```bash
python src/mcp/mcp_db/schema/execute_schema.py
```

Ce script va :
- Se connecter à votre base TiDB
- Créer toutes les tables nécessaires (users, tasks, projects, etc.)
- Initialiser les vues pour les requêtes optimisées

#### 2.3 Vérifier la création des tables
Connectez-vous à votre interface TiDB et vérifiez que les tables suivantes ont été créées :
- `users` : Gestion des utilisateurs et travailleurs
- `tasks` : Tâches avec géolocalisation et compétences
- `projects` : Projets de construction
- `task_assignments` : Assignations de tâches
- `notifications` : Système de notifications
- Vues : `active_tasks`, `overdue_tasks`, `worker_workload`

### 3. Configuration LangSmith (Monitoring)

LangSmith vous permettra de voir en temps réel :
- ⏱️ **Temps d'exécution** de chaque agent
- 🔢 **Nombre de tokens** utilisés
- 🔍 **Exécution détaillée** des communications inter-agents
- 📊 **Métriques de performance** globales

Créez un compte sur [LangSmith](https://smith.langchain.com/) et ajoutez vos clés dans le `.env`.

## 🎮 Utilisation

### 1. Lancer le serveur MCP de base de données
```bash
make mcp-db
```
Ce serveur doit tourner en arrière-plan pour permettre aux agents d'accéder à la base de données.

### 2. Configurer le message de test
Dans `main.py`, ligne 28, remplacez le message par celui de votre worker :
```python
message = "[User ID: 2 - Message Date: Sun. 10 September 2025]: Votre message ici"
```

### 3. Exécuter l'application principale
```bash
make main
```

### 4. Observer l'exécution dans LangSmith
1. Connectez-vous à votre interface LangSmith
2. Sélectionnez votre projet configuré dans `.env`
3. Observez en temps réel l'exécution des agents, leurs communications et performances

## 📁 Structure du projet

```
├── main.py                     # Point d'entrée principal
├── src/
│   ├── agents/                 # Agents intelligents
│   │   ├── supervisor.py       # Orchestrateur principal
│   │   ├── planning.py         # Agent de planification
│   │   ├── conflict.py         # Résolution des conflits
│   │   ├── team_builder.py     # Allocation d'équipes
│   │   ├── notifier.py         # Notifications
│   │   └── executor.py         # Exécution des tâches
│   ├── mcp/                    # Protocoles MCP
│   │   ├── db_client.py        # Client base de données
│   │   └── mcp_db/            # Serveur MCP TiDB
│   │       ├── mcp_server.py   # Serveur principal
│   │       └── schema/         # Schémas de base
│   ├── config/                 # Configuration
│   └── tools/                  # Outils utilitaires
├── server/                     # API REST
├── Makefile                    # Commandes de développement
└── requirements.txt            # Dépendances Python
```

## 🔧 Commandes disponibles

```bash
# Lancer l'application principale
make main

# Démarrer le serveur MCP de base de données
make mcp-db

# Initialiser le schéma de base de données
python src/mcp/mcp_db/schema/execute_schema.py
```

## 🧪 Exemples d'utilisation

### Messages de test pour les agents

```python
# Assignation de tâche
"[User ID: 2]: Can you assign me another task please?"

# Mise à jour de contact
"[User ID: 1]: Update Michael Rodriguez's phone: +1-711-123-4567"

# Urgence sur site
"[User ID: 3]: Container blocking main entrance needs urgent removal"

# Retard de projet
"[User ID: 3]: Restaurant Foundation Excavation on RETAIL Building is delayed"
```

## 📊 Monitoring avec LangSmith

Une fois configuré, LangSmith vous donnera accès à :

- **Dashboard en temps réel** : Visualisation des agents actifs
- **Traces détaillées** : Chaque décision et communication inter-agents
- **Métriques de coût** : Tokens utilisés par agent et par session
- **Historique complet** : Toutes les exécutions passées avec détails
- **Alertes performance** : Détection des agents lents ou en erreur

## ⚡ Fonctionnalités avancées

- **Recherche vectorielle** : Recherche sémantique dans les tâches et documents
- **Géolocalisation intelligente** : Optimisation des déplacements d'équipes
- **Détection de conflits** : Algorithmes de résolution automatique des conflits de ressources
- **Notifications push** : Système d'alertes en temps réel
- **Multi-tenancy** : Support de plusieurs projets simultanés

## 🤝 Support

Pour toute question ou problème :
1. Vérifiez que TiDB est accessible depuis votre réseau
2. Confirmez que toutes les tables sont créées dans l'interface TiDB
3. Vérifiez que LangSmith reçoit bien les traces
4. Consultez les logs du serveur MCP pour débugger les connexions

---

**Développé pour le TiDB Hackathon 2025** 🚀