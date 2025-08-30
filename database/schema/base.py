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
