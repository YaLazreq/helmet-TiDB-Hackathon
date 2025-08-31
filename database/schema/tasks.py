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


class Task(Base):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), default="")
    estimated_time: Mapped[Optional[int]] = mapped_column(default=0)  # in minutes
    start_date: Mapped[Optional[datetime]] = mapped_column()
    due_date: Mapped[Optional[datetime]] = mapped_column()
    priority: Mapped[Optional[int]] = mapped_column(default=3)  # 1 (high) to 5 (low)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="pending")
    completion_percentage: Mapped[Optional[int]] = mapped_column(default=0)  # 0 to 100
    assigned_to: Mapped[Optional[int]] = mapped_column()  # user_id
    created_by: Mapped[Optional[int]] = mapped_column()  # user_id

    # Index for call optimization
    __table_args__ = (
        Index("idx_status", "status"),  # Filtrage par status
        Index("idx_priority", "priority"),  # Filtrage par priorité
        Index("idx_assigned_to", "assigned_to"),  # Recherche par user assigné
        Index("idx_due_date", "due_date"),  # Filtrage par date d'échéance
    )

    @classmethod
    def from_dict(cls, data_dict):
        """Create a Task instance from a dictionary"""
        user = cls()
        for key, value in data_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user


class TaskQueries:
    sql_create_table: str = f"""
        CREATE TABLE IF NOT EXISTS {Task.__tablename__} (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            title VARCHAR(200) NOT NULL,
            description VARCHAR(1000),
            estimated_time INT DEFAULT 0,
            start_date TIMESTAMP,
            due_date TIMESTAMP,
            priority INT DEFAULT 3,
            status VARCHAR(50) DEFAULT 'pending',
            completion_percentage INT DEFAULT 0,
            assigned_to INT,
            created_by INT,
            FOREIGN KEY (assigned_to) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """

    sql_create_task: str = f"""
    INSERT INTO {Task.__tablename__} ({{}}) VALUES ({{}})"""

    sql_get_all_tasks: str = f"SELECT * FROM {Task.__tablename__}"
    sql_get_task_by_id: str = f"SELECT * FROM {Task.__tablename__} WHERE id = %s"
    sql_update_task: str = f"UPDATE {Task.__tablename__} SET {{}} WHERE id = %s"
    sql_delete_task: str = f"DELETE FROM {Task.__tablename__} WHERE id = %s"


# =============================================================================
# Pydantic Schemas for API/Data Validation
# =============================================================================


class TaskCreate(BaseModel):
    """Schema pour créer un utilisateur via API"""

    model_config = ConfigDict(from_attributes=True)

    title: str
    description: Optional[str] = None
    estimated_time: Optional[int] = 0  # in minutes
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = 3  # 1 (high) to 5 (low)
    status: Optional[str] = "pending"
    completion_percentage: Optional[int] = 0  # 0 to 100
    assigned_to: Optional[int] = None  # user_id
    created_by: Optional[int] = None  # user_id


class TaskUpdate(BaseModel):
    """Return task data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)

    title: str
    description: Optional[str]
    estimated_time: Optional[int]
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    priority: Optional[int]
    status: Optional[str]
    completion_percentage: Optional[int]
    assigned_to: Optional[int]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime


class TaskResponse(BaseModel):
    """Return task data via API without sensitive info"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    estimated_time: Optional[int]
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    priority: Optional[int]
    status: Optional[str]
    completion_percentage: Optional[int]
    assigned_to: Optional[int]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime


# =============================================================================
# Repository Pattern - CRUD Operations
# =============================================================================


class TaskRepository:
    @staticmethod
    def create_task(
        connection: pymysql.Connection, task: TaskCreate
    ) -> Optional[TaskResponse]:
        """Create a new task and return its ID"""
        try:
            with connection.cursor() as cursor:
                create_data = task.model_dump(exclude_unset=True, exclude_none=True)

                if not create_data:
                    print("❌ Aucune données pour créer une tâche")
                    return None

                # Séparer les noms de colonnes et les valeurs
                field_names = list(create_data.keys())
                field_values = list(create_data.values())

                # Construire les parties de la requête
                columns = ", ".join(field_names)
                placeholders = ", ".join(["%s"] * len(field_values))

                # Formatage standard : INSERT INTO table (col1, col2) VALUES (%s, %s)
                create_sql = TaskQueries.sql_create_task.format(columns, placeholders)

                print(f"SQL: {create_sql}")
                print(f"Values: {field_values}")

                cursor.execute(create_sql, tuple(field_values))
                connection.commit()
                new_id = cursor.lastrowid

                print(f"✅ Tâche créée avec l'ID : {new_id}")
                return TaskRepository.get_task_by_id(connection, new_id)

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la création de la tâche : {e}")
            return None

    @staticmethod
    def get_all_tasks(connection: pymysql.Connection) -> list[TaskResponse]:
        """Get all tasks"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(TaskQueries.sql_get_all_tasks)
                results = cursor.fetchall()

                # Convert in TaskResponse
                tasks = [TaskResponse(**row) for row in results]

                print(f"✅ {len(tasks)} tâche(s) récupérée(s)")
                for task in tasks:
                    print(f"  - {task.title} (ID: {task.id})")

                return tasks

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return []

    @staticmethod
    def get_task_by_id(
        connection: pymysql.Connection, task_id: int
    ) -> Optional[TaskResponse]:
        """Get a task by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(TaskQueries.sql_get_task_by_id, (task_id,))
                result = cursor.fetchone()
                task = TaskResponse(**result) if result else None

                return task

        except Exception as e:
            print(f"❌ Erreur lors de la lecture : {e}")
            return None

    @staticmethod
    def update_task(
        connection: pymysql.Connection, task: TaskCreate, task_id: int
    ) -> bool:
        """Update a task using Task Create schema"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                updates = []
                values = []

                # Récupérer seulement les champs non-None du TaskCreate
                update_data = task.model_dump(exclude_unset=True, exclude_none=True)

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
                values.append(task_id)

                # Construire et exécuter la requête
                set_clause = ", ".join(updates)
                update_sql = TaskQueries.sql_update_task.format(set_clause)

                cursor.execute(update_sql, tuple(values))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Tâche {task_id} mise à jour ({len(updates)-1} champs)")
                    return True
                else:
                    print("❌ Aucune tâche trouvée avec cet ID")
                    return False

        except Exception as e:
            connection.rollback()
            print(f"❌ Erreur lors de la mise à jour : {e}")
            return False

    @staticmethod
    def delete_task(connection: pymysql.Connection, task_id):
        """Delete a task by ID"""
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(TaskQueries.sql_delete_task, (task_id,))
                connection.commit()

                if cursor.rowcount > 0:
                    print(f"✅ Tâche {task_id} supprimée")
                else:
                    print("❌ Aucune tâche trouvée avec cet ID")

        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return None
