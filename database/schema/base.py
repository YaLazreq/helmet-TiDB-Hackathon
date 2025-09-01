from datetime import datetime
from typing import Optional

import pymysql
from sqlalchemy import DateTime, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


class Base(DeclarativeBase):
    """Base class for all database models"""

    # Common columns for all tables
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


def drop_all_tables(connection: pymysql.Connection):
    """Supprimer toutes les tables dans l'ordre inverse des dépendances"""
    tables_to_drop = [
        "tasks",  # Références users
        "products",  # Références suppliers, orders, sites
        "orders",  # Références suppliers, users
        "sites",  # Références users
        "suppliers",  # Aucune dépendance
        "users",  # Aucune dépendance
    ]

    try:
        with connection.cursor() as cursor:
            # Désactiver les contraintes de clés étrangères temporairement
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            for table_name in tables_to_drop:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    print(f"🗑️  Table '{table_name}' supprimée")
                except Exception as e:
                    print(f"⚠️  Impossible de supprimer la table '{table_name}': {e}")

            # Réactiver les contraintes de clés étrangères
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            connection.commit()
            print("✅ Toutes les tables ont été nettoyées !")

    except Exception as e:
        connection.rollback()
        print(f"❌ Erreur lors du nettoyage des tables : {e}")


def create_table(
    connection: pymysql.Connection,
    sql_table_name: str,
    sql_command: str,
    sql_indexes: Optional[list[str]] = None,
):
    """Créer une table users basée sur le schéma SQLAlchemy"""
    try:
        with connection.cursor() as cursor:
            # SQL généré à partir du modèle User SQLAlchemy
            create_table_sql = sql_command
            cursor.execute(create_table_sql)

            # Créer les index définis dans le modèle User
            if sql_indexes:
                for index_sql in sql_indexes:
                    cursor.execute(index_sql)
                    print(
                        f"✅ Index créés pour optimiser les performances sur la table '{sql_table_name}'"
                    )

            connection.commit()
            print(f"✅ Table '{sql_table_name}' créée avec le schéma SQLAlchemy !")

    except Exception as e:
        connection.rollback()
        print(f"❌ Erreur lors de la création de table : {e}")
