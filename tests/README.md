# Tests TiDB Application

Structure des tests pour l'application TiDB avec Users et Tasks.

## Structure

```
tests/
├── __init__.py                 # Package tests
├── conftest.py                # Configuration globale et fixtures
├── README.md                  # Documentation
├── unit/                      # Tests unitaires
│   ├── __init__.py
│   ├── test_database_connection.py  # Tests connexion DB
│   ├── test_users.py               # Tests Users (schemas + repository)
│   └── test_tasks.py               # Tests Tasks (schemas + repository)
├── integration/               # Tests d'intégration
│   ├── __init__.py
│   └── test_workflow.py           # Tests workflows complets
└── fixtures/                  # Données de test
    ├── __init__.py
    └── sample_data.py             # Données d'exemple réutilisables
```

## Installation des dépendances

```bash
pip install pytest pytest-cov
```

## Lancer les tests

### Tous les tests
```bash
pytest tests/
```

### Tests unitaires seulement
```bash
pytest tests/unit/
```

### Tests d'intégration seulement
```bash
pytest tests/integration/
```

### Tests avec couverture
```bash
pytest tests/ --cov=database --cov=server
```

### Tests verbeux
```bash
pytest tests/ -v
```

## Configuration requise

1. **Base de données de test** : Assurez-vous d'avoir une base TiDB accessible
2. **Variables d'environnement** : Configurez votre `.env` avec les bonnes connexions
3. **Tables** : Les tests nettoient automatiquement les tables avant chaque test

## Types de tests

### Tests unitaires (`unit/`)
- **test_database_connection.py** : Teste la connexion et configuration DB
- **test_users.py** : Teste les schemas Pydantic et repository Users
- **test_tasks.py** : Teste les schemas Pydantic et repository Tasks

### Tests d'intégration (`integration/`)
- **test_workflow.py** : Teste les workflows complets (créer user → créer tasks → update → delete)

### Fixtures (`fixtures/`)
- **sample_data.py** : Données réutilisables pour tous les tests

## Fixtures disponibles

### Dans `conftest.py`
- `db_connection` : Connexion à la DB pour la session
- `clean_tables` : Nettoie les tables avant chaque test
- `sample_user_data` : Données utilisateur de base
- `sample_task_data` : Données tâche de base

### Dans `sample_data.py`
- `SampleUsers` : Utilisateurs prédéfinis (admin, plumber, electrician, etc.)
- `SampleTasks` : Tâches prédéfinies par spécialité

## Bonnes pratiques

1. **Isolation** : Chaque test nettoie la DB avant de commencer
2. **Données réalistes** : Utilise des données proches de la production
3. **Tests complets** : Couvre les cas normaux ET les cas d'erreur
4. **Assertions claires** : Messages d'erreur compréhensibles
5. **Setup/Teardown** : Création et nettoyage automatiques

## Exemples d'utilisation

### Test simple avec fixture
```python
def test_create_user(clean_tables, sample_user_data):
    user = UserRepository.create_user(clean_tables, UserCreate(**sample_user_data))
    assert user is not None
    assert user.email == sample_user_data["email"]
```

### Test avec données personnalisées
```python
def test_workflow(clean_tables):
    # Créer admin
    admin = UserRepository.create_user(clean_tables, UserCreate(**SampleUsers.ADMIN))
    
    # Créer technicien  
    tech = UserRepository.create_user(clean_tables, UserCreate(**SampleUsers.PLUMBER))
    
    # Admin crée tâche pour technicien
    task_data = {"title": "Fix leak", "assigned_to": tech.id, "created_by": admin.id}
    task = TaskRepository.create_task(clean_tables, TaskCreate(**task_data))
    
    assert task.assigned_to == tech.id
```