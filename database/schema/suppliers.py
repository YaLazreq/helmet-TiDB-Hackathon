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


class Supplier(Base):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255), default="")
    phone: Mapped[Optional[str]] = mapped_column(String(20), default="")
    email: Mapped[Optional[str]] = mapped_column(String(100), default="")
    type: Mapped[Optional[str]] = mapped_column(String(50), default="")

    # Index for call optimization
    __table_args__ = (
        Index("idx_name", "name"),  # Recherche par nom
        Index("idx_type", "type"),  # Filtrage par type
    )

    @classmethod
    def from_dict(cls, data_dict):
        """Create a Task instance from a dictionary"""
        user = cls()
        for key, value in data_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user


class SupplierQueries:
    sql_create_table: str = f"""
        CREATE TABLE IF NOT EXISTS {Supplier.__tablename__} (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            name VARCHAR(100) UNIQUE NOT NULL,
            address VARCHAR(255),
            phone VARCHAR(20),
            email VARCHAR(100),
            type VARCHAR(50)
        )
        """

    sql_create_supplier: str = f"""
    INSERT INTO {Supplier.__tablename__} ({{}}) VALUES ({{}})"""

    sql_get_all_suppliers: str = f"SELECT * FROM {Supplier.__tablename__}"
    sql_get_supplier_by_id: str = f"SELECT * FROM {Supplier.__tablename__} WHERE id = %s"
    sql_update_supplier: str = f"UPDATE {Supplier.__tablename__} SET {{}} WHERE id = %s"
    sql_delete_supplier: str = f"DELETE FROM {Supplier.__tablename__} WHERE id = %s"


# =============================================================================
# Pydantic Schemas for API/Data Validation
# =============================================================================


class SupplierCreate(BaseModel):
    """Schema for creating a new supplier"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None


class SupplierUpdate(BaseModel):
    """Return supplier data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None


class SupplierResponse(BaseModel):
    """Return supplier data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Repository Pattern - CRUD Operations
# =============================================================================


class SupplierRepository:
    @staticmethod
    def create_supplier(
        connection: pymysql.Connection, supplier: SupplierCreate
    ) -> Optional[SupplierResponse]:
        """Create a new supplier and return its ID"""
        try:
            with connection.cursor() as cursor:
                create_data = supplier.model_dump(exclude_unset=True, exclude_none=True)

                if not create_data:
                    print("❌ Aucune données pour créer un fournisseur")
                    return None

                # Séparer les noms de colonnes et les valeurs
                field_names = list(create_data.keys())
                field_values = list(create_data.values())

                # Construire les parties de la requête
                columns = ", ".join(field_names)
                placeholders = ", ".join(["%s"] * len(field_values))

                # Formatage standard : INSERT INTO table (col1, col2) VALUES (%s, %s)
                create_sql = SupplierQueries.sql_create_supplier.format(
                    columns, placeholders
                )

                print(f"SQL: {create_sql}")
                print(f"Values: {field_values}")

                cursor.execute(create_sql, tuple(field_values))
                connection.commit()
                new_id = cursor.lastrowid

                print(f"✅ Fournisseur créé avec l'ID : {new_id}")
                return SupplierRepository.get_supplier_by_id(connection, new_id)

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la création du fournisseur : {e}")
            return None

    @staticmethod
    def get_all_suppliers(connection: pymysql.Connection) -> list[SupplierResponse]:
        """Get all suppliers"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(SupplierQueries.sql_get_all_suppliers)
                results = cursor.fetchall()

                # Convert in SupplierResponse
                suppliers = [SupplierResponse(**row) for row in results]

                print(f"✅ {len(suppliers)} fournisseur(s) récupéré(s)")
                for supplier in suppliers:
                    print(f"  - {supplier.name} (ID: {supplier.id})")

                return suppliers

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return []

    @staticmethod
    def get_supplier_by_id(
        connection: pymysql.Connection, supplier_id: int
    ) -> Optional[SupplierResponse]:
        """Get a supplier by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(SupplierQueries.sql_get_supplier_by_id, (supplier_id,))
                result = cursor.fetchone()
                supplier = SupplierResponse(**result) if result else None

                return supplier

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return None

    @staticmethod
    def update_supplier(
        connection: pymysql.Connection, supplier: SupplierCreate, supplier_id: int
    ) -> bool:
        """Update a supplier using Supplier Create schema"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                updates = []
                values = []

                # Récupérer seulement les champs non-None du SupplierCreate
                update_data = supplier.model_dump(exclude_unset=True, exclude_none=True)

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
                values.append(supplier_id)

                # Construire et exécuter la requête
                set_clause = ", ".join(updates)
                update_sql = SupplierQueries.sql_update_supplier.format(set_clause)

                cursor.execute(update_sql, tuple(values))
                connection.commit()

                if cursor.rowcount > 0:
                    print(
                        f"✅ Fournisseur {supplier_id} mise à jour ({len(updates)-1} champs)"
                    )
                    return True
                else:
                    print("❌ Aucun fournisseur trouvé avec cet ID")
                    return False

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la mise à jour : {e}")
            return False

    @staticmethod
    def delete_supplier(connection: pymysql.Connection, supplier_id: int):
        """Delete a supplier by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(SupplierQueries.sql_delete_supplier, (supplier_id,))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Fournisseur {supplier_id} supprimé")
                else:
                    print("❌ Aucun fournisseur trouvé avec cet ID")

        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return None
