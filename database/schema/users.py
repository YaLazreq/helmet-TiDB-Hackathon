# Model definitions
from typing import Optional
import pymysql.cursors
from datetime import datetime

from sqlalchemy import Boolean, Index, String
from database.schema.base import Base
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

# Pydantic schemas for validation
from pydantic import BaseModel, ConfigDict


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(50), default="")
    last_name: Mapped[Optional[str]] = mapped_column(String(50), default="")
    phone: Mapped[Optional[str]] = mapped_column(String(20), default="")
    role: Mapped[Optional[str]] = mapped_column(String(20), default="")
    specialization: Mapped[Optional[str]] = mapped_column(String(50), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Index for call optimization
    __table_args__ = (
        # Index("idx_username", "username"),  # Recherche par login
        Index("idx_email", "email"),  # Recherche par email
        Index("idx_active", "is_active"),  # Filtrage users actifs
    )

    @classmethod
    def from_dict(cls, data_dict):
        """Create a User instance from a dictionary"""
        user = cls()
        for key, value in data_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user


class UserQueries:
    sql_create_table: str = f"""
        CREATE TABLE IF NOT EXISTS {User.__tablename__} (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255),
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            phone VARCHAR(20),
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            role VARCHAR(20),
            specialization VARCHAR(50)
        )
        """

    sql_create_user: str = f"""
    INSERT INTO {User.__tablename__} ({{}}) VALUES ({{}})"""

    sql_get_all_users: str = f"SELECT * FROM {User.__tablename__}"

    sql_get_user_by_id: str = f"SELECT * FROM {User.__tablename__} WHERE id = %s"
    sql_update_user: str = f"UPDATE {User.__tablename__} SET {{}} WHERE id = %s"
    sql_delete_user: str = f"DELETE FROM {User.__tablename__} WHERE id = %s"


# =============================================================================
# Pydantic Schemas for API/Data Validation
# =============================================================================


class UserCreate(BaseModel):
    """Schema pour créer un utilisateur via API"""

    email: str
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False
    role: Optional[str] = None
    specialization: Optional[str] = None


class UserUpdate(BaseModel):
    """Return user data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: Optional[str]
    specialization: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    """Return user data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_admin: bool
    role: Optional[str] = None
    specialization: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Repository Pattern - CRUD Operations
# =============================================================================


class UserRepository:
    @staticmethod
    def create_user(
        connection: pymysql.Connection, user: UserCreate
    ) -> Optional[UserResponse]:
        """Create a new user and return its ID"""
        try:
            with connection.cursor() as cursor:
                create_data = user.model_dump(exclude_unset=True, exclude_none=True)

                if not create_data:
                    print("❌ Aucune données pour créer un utilisateur")
                    return None

                # Séparer les noms de colonnes et les valeurs
                field_names = list(create_data.keys())
                field_values = list(create_data.values())

                # Construire les parties de la requête
                columns = ", ".join(field_names)
                placeholders = ", ".join(["%s"] * len(field_values))

                # Formatage standard : INSERT INTO table (col1, col2) VALUES (%s, %s)
                create_sql = UserQueries.sql_create_user.format(columns, placeholders)

                print(f"SQL: {create_sql}")
                print(f"Values: {field_values}")

                cursor.execute(create_sql, tuple(field_values))
                connection.commit()
                new_id = cursor.lastrowid

                print(f"✅ Utilisateur créé avec l'ID : {new_id}")
                return UserResponse(id=new_id, **create_data)

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la création de l'utilisateur : {e}")
            return None

    @staticmethod
    def get_all_users(connection: pymysql.Connection) -> list[UserResponse]:
        """Get all users"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(UserQueries.sql_get_all_users)
                results = cursor.fetchall()  # Maintenant c'est des dicts !

                # Convert in UserResponse
                users = [UserResponse(**row) for row in results]

                print(f"✅ {len(users)} utilisateur(s) récupéré(s)")
                for user in users:
                    print(f"  - {user.first_name} ({user.email})")

                return users

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return []

    @staticmethod
    def get_user_by_id(connection: pymysql.Connection, user_id):
        """Get a user by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(UserQueries.sql_get_user_by_id, (user_id,))
                result = cursor.fetchone()
                user = UserResponse(**result) if result else None
                print(
                    f"  - {user.first_name or 'N/A'} ({user.email or 'N/A'})"
                    if user
                    else "Utilisateur non trouvé"
                )

                return user

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return None

    @staticmethod
    def update_user(connection: pymysql.Connection, user: UserCreate, user_id: int):
        """Update a user using UserCreate schema"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                updates = []
                values = []

                # Récupérer seulement les champs non-None du UserCreate
                update_data = user.model_dump(exclude_unset=True, exclude_none=True)

                # Loop sur les champs à mettre à jour
                for field_name, field_value in update_data.items():
                    if field_name not in [
                        "id",
                        "created_at",
                    ]:  # Exclure les champs non-modifiables
                        updates.append(f"{field_name} = %s")
                        values.append(field_value)

                if not updates:
                    print("❌ Aucun champ à mettre à jour")
                    return False

                # Ajouter updated_at automatiquement
                updates.append("updated_at = NOW()")
                values.append(user_id)

                # Construire et exécuter la requête
                set_clause = ", ".join(updates)
                update_sql = UserQueries.sql_update_user.format(set_clause)

                cursor.execute(update_sql, tuple(values))
                connection.commit()

                if cursor.rowcount > 0:
                    print(
                        f"✅ Utilisateur {user_id} mis à jour ({len(updates)-1} champs)"
                    )
                    return True
                else:
                    print("❌ Aucun utilisateur trouvé avec cet ID")
                    return False

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la mise à jour : {e}")
            return False

    @staticmethod
    def delete_user(connection: pymysql.Connection, user_id):
        """Delete a user by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(UserQueries.sql_delete_user, (user_id,))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Utilisateur {user_id} supprimé")
                else:
                    print("❌ Aucun utilisateur trouvé avec cet ID")

        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return None
