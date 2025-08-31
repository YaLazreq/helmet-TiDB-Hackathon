# Model definitions
import json
from typing import Optional
import pymysql.cursors
from datetime import datetime

from sqlalchemy import Boolean, Float, Index, String
from database.schema.base import Base
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

# Pydantic schemas for validation
from pydantic import BaseModel, ConfigDict
from src.models.enums.enums import OrderStatus
from sqlalchemy import JSON


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), default="")
    description: Mapped[Optional[str]] = mapped_column(String(255), default="")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, default=""
    )
    specifications: Mapped[Optional[dict]] = mapped_column(JSON, default={})
    supplier_id: Mapped[Optional[int]] = mapped_column(default=None)
    order_id: Mapped[Optional[int]] = mapped_column(default=None)
    stock_site_id: Mapped[Optional[int]] = mapped_column(default=None)

    # Index for call optimization
    __table_args__ = (
        Index("idx_name", "name"),  # Recherche par nom
        Index("idx_brand", "brand"),  # Filtrage par marque
        Index("idx_price", "price"),  # Filtrage par prix
    )

    @classmethod
    def from_dict(cls, data_dict):
        """Create a Task instance from a dictionary"""
        user = cls()
        for key, value in data_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user


class ProductQueries:
    sql_create_table: str = f"""
        CREATE TABLE IF NOT EXISTS {Product.__tablename__} (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            name VARCHAR(100) NOT NULL,
            brand VARCHAR(100),
            description VARCHAR(255),
            price FLOAT NOT NULL,
            reference VARCHAR(50),
            specifications JSON,
            supplier_id INT,
            order_id INT,
            stock_site_id INT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (stock_site_id) REFERENCES stock_sites(id)
        )
        """

    sql_create_product: str = f"""
    INSERT INTO {Product.__tablename__} ({{}}) VALUES ({{}})"""

    sql_get_all_products: str = f"SELECT * FROM {Product.__tablename__}"
    sql_get_product_by_id: str = f"SELECT * FROM {Product.__tablename__} WHERE id = %s"
    sql_update_product: str = f"UPDATE {Product.__tablename__} SET {{}} WHERE id = %s"
    sql_delete_product: str = f"DELETE FROM {Product.__tablename__} WHERE id = %s"


# =============================================================================
# Pydantic Schemas for API/Data Validation
# =============================================================================


class ProductCreate(BaseModel):
    """Schema for creating a new product"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    price: float
    reference: Optional[str] = None
    specifications: Optional[dict] = None
    supplier_id: Optional[int] = None
    order_id: Optional[int] = None
    stock_site_id: Optional[int] = None


class ProductUpdate(BaseModel):
    """Return product data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    reference: Optional[str] = None
    specifications: Optional[dict] = None
    supplier_id: Optional[int] = None
    order_id: Optional[int] = None
    stock_site_id: Optional[int] = None


class ProductResponse(BaseModel):
    """Return product data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    reference: Optional[str] = None
    specifications: Optional[dict] = None
    supplier_id: Optional[int] = None
    order_id: Optional[int] = None
    stock_site_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Repository Pattern - CRUD Operations
# =============================================================================


class ProductRepository:
    @staticmethod
    def create_product(
        connection: pymysql.Connection, product: ProductCreate
    ) -> Optional[ProductResponse]:
        """Create a new product and return its ID"""
        try:
            with connection.cursor() as cursor:
                create_data = product.model_dump(exclude_unset=True, exclude_none=True)

                if not create_data:
                    print("❌ Aucune données pour créer un produit")
                    return None

                # Séparer les noms de colonnes et les valeurs
                field_names = list(create_data.keys())
                field_values = list(create_data.values())

                # Construire les parties de la requête
                columns = ", ".join(field_names)
                placeholders = ", ".join(["%s"] * len(field_values))

                # Formatage standard : INSERT INTO table (col1, col2) VALUES (%s, %s)
                create_sql = ProductQueries.sql_create_product.format(
                    columns, placeholders
                )

                print(f"SQL: {create_sql}")
                print(f"Values: {field_values}")

                cursor.execute(create_sql, tuple(field_values))
                connection.commit()
                new_id = cursor.lastrowid

                print(f"✅ Produit créé avec l'ID : {new_id}")
                return ProductRepository.get_product_by_id(connection, new_id)

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la création du produit : {e}")
            return None

    @staticmethod
    def get_all_products(connection: pymysql.Connection) -> list[ProductResponse]:
        """Get all products"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(ProductQueries.sql_get_all_products)
                results = cursor.fetchall()

                # Convert in ProductResponse
                products = [ProductResponse(**row) for row in results]

                print(f"✅ {len(products)} produit(s) récupéré(s)")
                for product in products:
                    print(f"  - {product.name} (ID: {product.id})")

                return products

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return []

    @staticmethod
    def get_product_by_id(
        connection: pymysql.Connection, product_id: int
    ) -> Optional[ProductResponse]:
        """Get a product by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(ProductQueries.sql_get_product_by_id, (product_id,))
                result = cursor.fetchone()
                product = ProductResponse(**result) if result else None

                return product

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return None

    @staticmethod
    def update_product(
        connection: pymysql.Connection, product: ProductCreate, product_id: int
    ) -> bool:
        """Update a product using Product Create schema"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                updates = []
                values = []

                # Récupérer seulement les champs non-None du ProductCreate
                update_data = product.model_dump(exclude_unset=True, exclude_none=True)

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
                values.append(product_id)

                # Construire et exécuter la requête
                set_clause = ", ".join(updates)
                update_sql = ProductQueries.sql_update_product.format(set_clause)

                cursor.execute(update_sql, tuple(values))
                connection.commit()

                if cursor.rowcount > 0:
                    print(
                        f"✅ Produit {product_id} mise à jour ({len(updates)-1} champs)"
                    )
                    return True
                else:
                    print("❌ Aucun produit trouvé avec cet ID")
                    return False

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la mise à jour : {e}")
            return False

    @staticmethod
    def delete_product(connection: pymysql.Connection, product_id: int):
        """Delete a product by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(ProductQueries.sql_delete_product, (product_id,))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Produit {product_id} supprimé")
                else:
                    print("❌ Aucun produit trouvé avec cet ID")

        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return None
