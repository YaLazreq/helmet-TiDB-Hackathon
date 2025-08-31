"""
Configuration et fixtures partagées pour les tests
"""

import pytest
import pymysql
from database.schema.users import User, UserQueries
from database.schema.tasks import Task, TaskQueries
from mcp_server import connect_to_tidb
import database.config as config


@pytest.fixture(scope="session")
def db_connection():
    """Fixture pour la connexion à la base de données de test"""
    conn = connect_to_tidb()
    if not conn:
        pytest.skip("Impossible de se connecter à la base de données")

    yield conn

    # Cleanup
    conn.close()


@pytest.fixture(scope="function")
def clean_tables(db_connection):
    """Nettoie les tables avant chaque test"""
    with db_connection.cursor() as cursor:
        # Désactiver les contraintes FK temporairement
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # Vider les tables
        cursor.execute(f"TRUNCATE TABLE {Task.__tablename__}")
        cursor.execute(f"TRUNCATE TABLE {User.__tablename__}")

        # Réactiver les contraintes FK
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        db_connection.commit()

    yield db_connection


@pytest.fixture
def sample_user_data():
    """Données d'exemple pour un utilisateur"""
    return {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "0123456789",
        "role": "technician",
        "specialization": "plumber",
        "is_active": True,
        "is_admin": False,
    }


@pytest.fixture
def sample_task_data():
    """Données d'exemple pour une tâche"""
    return {
        "title": "Test Task",
        "description": "Une tâche de test",
        "assigned_to": 1,
        "status": "pending",
        "priority": 2,
        "created_by": 1,
        "completion_percentage": 0,
        "estimated_time": 60,
    }
