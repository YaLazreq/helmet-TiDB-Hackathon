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


class Order(Base):
    __tablename__ = "orders"

    nbr_items: Mapped[Optional[int]] = mapped_column(default=0)
    status: Mapped[Optional[str]] = mapped_column(
        String(50), default=OrderStatus.PENDING.value
    )
    invoice_url: Mapped[Optional[str]] = mapped_column(String(255), default="")
    supplier_id: Mapped[Optional[int]] = mapped_column()  # user_id
    description: Mapped[Optional[str]] = mapped_column(String(1000), default="")
    price: Mapped[Optional[float]] = mapped_column(default=0.0)
    created_by: Mapped[Optional[int]] = mapped_column()  # user_id

    # Index for call optimization
    __table_args__ = (
        Index("idx_status", "status"),  # Filtrage par status
        Index("idx_supplier", "supplier_id"),  # Filtrage par fournisseur
        Index("idx_created_by", "created_by"),  # Filtrage par créateur
    )

    @classmethod
    def from_dict(cls, data_dict):
        """Create a Task instance from a dictionary"""
        user = cls()
        for key, value in data_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user


class OrderQueries:
    sql_create_table: str = f"""
        CREATE TABLE IF NOT EXISTS {Order.__tablename__} (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            nbr_items INT DEFAULT 0,
            status VARCHAR(50) DEFAULT '{OrderStatus.PENDING.value}',
            invoice_url VARCHAR(255),
            supplier_id INT,
            description VARCHAR(1000),
            price FLOAT DEFAULT 0.0,
            created_by INT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """

    sql_create_order: str = f"""
    INSERT INTO {Order.__tablename__} ({{}}) VALUES ({{}})"""

    sql_get_all_orders: str = f"SELECT * FROM {Order.__tablename__}"
    sql_get_order_by_id: str = f"SELECT * FROM {Order.__tablename__} WHERE id = %s"
    sql_update_order: str = f"UPDATE {Order.__tablename__} SET {{}} WHERE id = %s"
    sql_delete_order: str = f"DELETE FROM {Order.__tablename__} WHERE id = %s"


# =============================================================================
# Pydantic Schemas for API/Data Validation
# =============================================================================


class OrderCreate(BaseModel):
    """Schema for creating a new order"""

    model_config = ConfigDict(from_attributes=True)

    nbr_items: Optional[int] = 0
    status: Optional[str] = OrderStatus.PENDING.value
    invoice_url: Optional[str] = ""
    supplier_id: Optional[int] = None  # user_id
    description: Optional[str] = ""
    price: Optional[float] = 0.0
    created_by: Optional[int] = None  # user_id


class OrderUpdate(BaseModel):
    """Return order data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    nbr_items: Optional[int] = None
    status: Optional[str] = None
    invoice_url: Optional[str] = None
    supplier_id: Optional[int] = None  # user_id
    description: Optional[str] = None
    price: Optional[float] = None
    created_by: Optional[int] = None  # user_id


class OrderResponse(BaseModel):
    """Return order data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nbr_items: Optional[int] = None
    status: Optional[str] = None
    invoice_url: Optional[str] = None
    supplier_id: Optional[int] = None  # user_id
    description: Optional[str] = None
    price: Optional[float] = None
    created_by: Optional[int] = None  # user_id
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Repository Pattern - CRUD Operations
# =============================================================================


class OrderRepository:
    @staticmethod
    def create_order(
        connection: pymysql.Connection, order: OrderCreate
    ) -> Optional[OrderResponse]:
        """Create a new order and return its ID"""
        try:
            with connection.cursor() as cursor:
                create_data = order.model_dump(exclude_unset=True, exclude_none=True)

                if not create_data:
                    print("❌ Aucune données pour créer une commande")
                    return None

                # Séparer les noms de colonnes et les valeurs
                field_names = list(create_data.keys())
                field_values = list(create_data.values())

                # Construire les parties de la requête
                columns = ", ".join(field_names)
                placeholders = ", ".join(["%s"] * len(field_values))

                # Formatage standard : INSERT INTO table (col1, col2) VALUES (%s, %s)
                create_sql = OrderQueries.sql_create_order.format(columns, placeholders)

                print(f"SQL: {create_sql}")
                print(f"Values: {field_values}")

                cursor.execute(create_sql, tuple(field_values))
                connection.commit()
                new_id = cursor.lastrowid

                print(f"✅ Commande créée avec l'ID : {new_id}")
                return OrderRepository.get_order_by_id(connection, new_id)

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la création de la commande : {e}")
            return None

    @staticmethod
    def get_all_orders(connection: pymysql.Connection) -> list[OrderResponse]:
        """Get all orders"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(OrderQueries.sql_get_all_orders)
                results = cursor.fetchall()

                # Convert in OrderResponse
                orders = [OrderResponse(**row) for row in results]

                print(f"✅ {len(orders)} commande(s) récupérée(s)")
                for order in orders:
                    print(f"  - {order.description} (ID: {order.id})")

                return orders

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return []

    @staticmethod
    def get_order_by_id(
        connection: pymysql.Connection, order_id: int
    ) -> Optional[OrderResponse]:
        """Get an order by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(OrderQueries.sql_get_order_by_id, (order_id,))
                result = cursor.fetchone()
                order = OrderResponse(**result) if result else None

                return order

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return None

    @staticmethod
    def update_order(
        connection: pymysql.Connection, order: OrderCreate, order_id: int
    ) -> bool:
        """Update an order using Order Create schema"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                updates = []
                values = []

                # Récupérer seulement les champs non-None du OrderCreate
                update_data = order.model_dump(exclude_unset=True, exclude_none=True)

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
                values.append(order_id)

                # Construire et exécuter la requête
                set_clause = ", ".join(updates)
                update_sql = OrderQueries.sql_update_order.format(set_clause)

                cursor.execute(update_sql, tuple(values))
                connection.commit()

                if cursor.rowcount > 0:
                    print(
                        f"✅ Commande {order_id} mise à jour ({len(updates)-1} champs)"
                    )
                    return True
                else:
                    print("❌ Aucune commande trouvée avec cet ID")
                    return False

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la mise à jour : {e}")
            return False

    @staticmethod
    def delete_order(connection: pymysql.Connection, order_id: int):
        """Delete an order by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(OrderQueries.sql_delete_order, (order_id,))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Commande {order_id} supprimée")
                else:
                    print("❌ Aucune commande trouvée avec cet ID")

        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return None
