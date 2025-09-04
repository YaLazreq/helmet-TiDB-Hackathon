from langchain_community.utilities import SQLDatabase
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Singleton pattern - connexion partagée
_db_connection = None


def create_database_connection():
    global _db_connection

    # Si connexion déjà créée, la retourner
    if _db_connection is not None:
        return _db_connection

    host = os.getenv("TIDB_HOST")
    port = int(os.getenv("TIDB_PORT", 4000))
    user = os.getenv("TIDB_USER")
    password = os.getenv("TIDB_PASSWORD")
    database = os.getenv("TIDB_DATABASE")
    ssl_ca = os.getenv("TIDB_SSL_CA", "./ca_tidb.pem")

    password_encoded = quote_plus(password)

    connection_string = (
        f"mysql+pymysql://{user}:{password_encoded}@{host}:{port}/{database}"
    )

    engine = create_engine(
        connection_string,
        connect_args={
            "ssl": {
                "ssl_ca": ssl_ca,
                "ssl_disabled": False,
                "ssl_verify_cert": True,
                "ssl_verify_identity": False,
            }
        },
        echo=False,
    )

    try:
        with engine.connect() as conn:
            # Connexion testée avec succès (message supprimé pour éviter le spam)
            pass
    except Exception as e:
        print(f"❌ Erreur de connexion SQLAlchemy: {e}")
        raise

    db = SQLDatabase(engine)

    # Sauvegarder la connexion pour réutilisation
    _db_connection = db

    return db


table_schema = """
    - users:
        id string pk
        email string
        password string
        first_name string
        last_name string
        phone string
        role enum ('worker', 'chief', 'manager', 'admin')
        specialization string ('electrician', 'plumber' etc.)
        created_at timestamp
        updated_at timestamp
        is_active boolean 
    - tasks: 
        id string pk
        title string
        description text
        assigned_to int fk
        estimated_hours decimal
        start_date date
        due_date date
        priority integer enum('low', 'medium', 'high', 'urgent')
        status string enum('not_started', 'in_progress', 'blocked', 'completed', 'cancelled')
        completion_percentage integer default 0
        created_by int fk
        created_at timestamp
        updated_at timestamp
"""
