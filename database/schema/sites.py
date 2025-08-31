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
from src.models.enums.enums import OrderStatus


class Site(Base):
    __tablename__ = "sites"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by: Mapped[int] = mapped_column()

    # Index for call optimization
    __table_args__ = (Index("idx_name", "name"),)  # Recherche par nom

    @classmethod
    def from_dict(cls, data_dict):
        """Create a Task instance from a dictionary"""
        user = cls()
        for key, value in data_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user


class SiteQueries:
    sql_create_table: str = f"""
        CREATE TABLE IF NOT EXISTS {Site.__tablename__} (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            name VARCHAR(100) UNIQUE NOT NULL,
            location VARCHAR(255) NOT NULL,
            created_by INT NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """

    sql_create_site: str = f"""
    INSERT INTO {Site.__tablename__} ({{}}) VALUES ({{}})"""

    sql_get_all_sites: str = f"SELECT * FROM {Site.__tablename__}"
    sql_get_site_by_id: str = f"SELECT * FROM {Site.__tablename__} WHERE id = %s"
    sql_update_site: str = f"UPDATE {Site.__tablename__} SET {{}} WHERE id = %s"
    sql_delete_site: str = f"DELETE FROM {Site.__tablename__} WHERE id = %s"


# =============================================================================
# Pydantic Schemas for API/Data Validation
# =============================================================================


class SiteCreate(BaseModel):
    """Schema for creating a new site"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    location: str
    created_by: int


class SiteUpdate(BaseModel):
    """Return site data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    location: Optional[str] = None
    created_by: Optional[int] = None


class SiteResponse(BaseModel):
    """Return site data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    created_by: int
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Repository Pattern - CRUD Operations
# =============================================================================


class SiteRepository:
    @staticmethod
    def create_site(
        connection: pymysql.Connection, site: SiteCreate
    ) -> Optional[SiteResponse]:
        """Create a new site and return its ID"""
        try:
            with connection.cursor() as cursor:
                create_data = site.model_dump(exclude_unset=True, exclude_none=True)

                if not create_data:
                    print("❌ Aucune données pour créer un site")
                    return None

                # Séparer les noms de colonnes et les valeurs
                field_names = list(create_data.keys())
                field_values = list(create_data.values())

                # Construire les parties de la requête
                columns = ", ".join(field_names)
                placeholders = ", ".join(["%s"] * len(field_values))

                # Formatage standard : INSERT INTO table (col1, col2) VALUES (%s, %s)
                create_sql = SiteQueries.sql_create_site.format(columns, placeholders)

                print(f"SQL: {create_sql}")
                print(f"Values: {field_values}")

                cursor.execute(create_sql, tuple(field_values))
                connection.commit()
                new_id = cursor.lastrowid

                print(f"✅ Site créé avec l'ID : {new_id}")
                return SiteRepository.get_site_by_id(connection, new_id)

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la création du site : {e}")
            return None

    @staticmethod
    def get_all_sites(connection: pymysql.Connection) -> list[SiteResponse]:
        """Get all sites"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(SiteQueries.sql_get_all_sites)
                results = cursor.fetchall()

                # Convert in SiteResponse
                sites = [SiteResponse(**row) for row in results]

                print(f"✅ {len(sites)} site(s) récupéré(s)")
                for site in sites:
                    print(f"  - {site.name} (ID: {site.id})")

                return sites

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return []

    @staticmethod
    def get_site_by_id(
        connection: pymysql.Connection, site_id: int
    ) -> Optional[SiteResponse]:
        """Get a site by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(SiteQueries.sql_get_site_by_id, (site_id,))
                result = cursor.fetchone()
                site = SiteResponse(**result) if result else None

                return site

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return None

    @staticmethod
    def update_site(
        connection: pymysql.Connection, site: SiteCreate, site_id: int
    ) -> bool:
        """Update a site using Site Create schema"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                updates = []
                values = []

                # Récupérer seulement les champs non-None du SiteCreate
                update_data = site.model_dump(exclude_unset=True, exclude_none=True)

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

                # updated_at est géré automatiquement par la DB avec ON UPDATE CURRENT_TIMESTAMP
                values.append(site_id)

                # Construire et exécuter la requête
                set_clause = ", ".join(updates)
                update_sql = SiteQueries.sql_update_site.format(set_clause)

                cursor.execute(update_sql, tuple(values))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Site {site_id} mis à jour ({len(updates)-1} champs)")
                    return True
                else:
                    print("❌ Aucun site trouvé avec cet ID")
                    return False

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la mise à jour : {e}")
            return False

    @staticmethod
    def delete_site(connection: pymysql.Connection, site_id: int):
        """Delete a site by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(SiteQueries.sql_delete_site, (site_id,))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Site {site_id} supprimé")
                else:
                    print("❌ Aucun site trouvé avec cet ID")

        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return None
