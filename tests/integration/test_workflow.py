"""
Tests d'intégration pour les workflows complets
"""

import pytest
from datetime import datetime, timedelta
from database.schema.users import UserCreate, UserRepository
from database.schema.tasks import TaskCreate, TaskRepository


class TestUserTaskWorkflow:
    """Tests d'intégration entre Users et Tasks"""

    def test_complete_user_task_workflow(self, clean_tables):
        """Test complet : créer utilisateur puis tâches"""
        # 1. Créer des utilisateurs
        admin_data = {
            "email": "admin@company.com",
            "password": "admin123",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "is_admin": True,
        }
        admin = UserRepository.create_user(clean_tables, UserCreate(**admin_data))
        assert admin is not None

        technician_data = {
            "email": "tech@company.com",
            "password": "tech123",
            "first_name": "Tech",
            "last_name": "User",
            "role": "technician",
            "specialization": "plumber",
        }
        technician = UserRepository.create_user(
            clean_tables, UserCreate(**technician_data)
        )
        assert technician is not None

        # 2. Admin crée des tâches et les assigne au technicien
        task_data = {
            "title": "Réparer fuite cuisine",
            "description": "Fuite sous l'évier de la cuisine",
            "assigned_to": technician.id,
            "created_by": admin.id,
            "status": "pending",
            "priority": 3,
            "due_date": datetime.now() + timedelta(days=2),
            "estimated_time": 120,
        }
        task = TaskRepository.create_task(clean_tables, TaskCreate(**task_data))
        assert task is not None
        assert task.assigned_to == technician.id

        # 3. Vérifier que la tâche apparaît dans les listes
        all_tasks = TaskRepository.get_all_tasks(clean_tables)
        assert len(all_tasks) == 1
        assert all_tasks[0].title == task_data["title"]

        # 4. Mise à jour du statut de la tâche
        update_data = TaskCreate(
            title=task.title,  # Garder le titre existant car requis
            status="in_progress", 
            completion_percentage=25
        )
        success = TaskRepository.update_task(clean_tables, update_data, task.id)
        assert success is True

        # 5. Vérifier la mise à jour
        updated_task = TaskRepository.get_task_by_id(clean_tables, task.id)
        assert updated_task.status == "in_progress"
        assert updated_task.completion_percentage == 25

        # 6. Compléter la tâche
        complete_data = TaskCreate(
            title=updated_task.title,  # Garder le titre existant car requis
            status="completed", 
            completion_percentage=100
        )
        TaskRepository.update_task(clean_tables, complete_data, task.id)

        completed_task = TaskRepository.get_task_by_id(clean_tables, task.id)
        assert completed_task.status == "completed"
        assert completed_task.completion_percentage == 100

    def test_multiple_users_multiple_tasks(self, clean_tables):
        """Test avec plusieurs utilisateurs et tâches"""
        # Créer 3 utilisateurs
        users = []
        for i in range(3):
            user_data = {
                "email": f"user{i+1}@test.com",
                "password": "password123",
                "first_name": f"User{i+1}",
                "last_name": "Test",
            }
            user = UserRepository.create_user(clean_tables, UserCreate(**user_data))
            users.append(user)

        # Créer 5 tâches assignées à différents utilisateurs
        tasks = []
        for i in range(5):
            assigned_user = users[i % len(users)]
            creator_user = users[(i + 1) % len(users)]

            task_data = {
                "title": f"Task {i+1}",
                "description": f"Description for task {i+1}",
                "assigned_to": assigned_user.id,
                "created_by": creator_user.id,
                "priority": (i % 3) + 1,  # Priority 1-3
                "status": ["pending", "in_progress", "completed"][i % 3],
            }
            task = TaskRepository.create_task(clean_tables, TaskCreate(**task_data))
            tasks.append(task)

        # Vérifications
        assert len(UserRepository.get_all_users(clean_tables)) == 3
        assert len(TaskRepository.get_all_tasks(clean_tables)) == 5

        # Vérifier que chaque utilisateur a au moins une tâche assignée
        for user in users:
            user_tasks = [t for t in tasks if t.assigned_to == user.id]
            assert len(user_tasks) >= 1

    def test_task_without_valid_user(self, clean_tables):
        """Test création de tâche avec utilisateur inexistant"""
        # Essayer de créer une tâche avec un ID utilisateur inexistant
        task_data = {
            "title": "Task with invalid user",
            "assigned_to": 99999,  # ID inexistant
            "created_by": 99998,  # ID inexistant
        }

        # Selon votre implémentation, ceci pourrait échouer
        # ou créer la tâche avec des FK nulles
        task = TaskRepository.create_task(clean_tables, TaskCreate(**task_data))

        # Le comportement dépend de vos contraintes FK
        # Si vous avez des contraintes, task devrait être None
        # Sinon, la tâche est créée avec des FK invalides
