"""
Données de test réutilisables
"""
from datetime import datetime, timedelta
from database.schema.users import UserCreate
from database.schema.tasks import TaskCreate


class SampleUsers:
    """Données d'exemple pour les utilisateurs"""
    
    ADMIN = {
        "email": "admin@tidb-app.com",
        "password": "admin_secure_123",
        "first_name": "Admin",
        "last_name": "System",
        "role": "admin",
        "specialization": "management",
        "is_active": True,
        "is_admin": True
    }
    
    PLUMBER = {
        "email": "plumber@tidb-app.com",
        "password": "plumber_pass_456",
        "first_name": "Jean",
        "last_name": "Dupont",
        "phone": "0123456789",
        "role": "technician",
        "specialization": "plumber",
        "is_active": True,
        "is_admin": False
    }
    
    ELECTRICIAN = {
        "email": "electrician@tidb-app.com",
        "password": "electric_pass_789",
        "first_name": "Marie",
        "last_name": "Martin",
        "phone": "0987654321",
        "role": "technician", 
        "specialization": "electrician",
        "is_active": True,
        "is_admin": False
    }
    
    INACTIVE_USER = {
        "email": "inactive@tidb-app.com",
        "password": "inactive_pass",
        "first_name": "Inactive",
        "last_name": "User",
        "is_active": False,
        "is_admin": False
    }

    @classmethod
    def get_all_users(cls):
        """Retourne tous les utilisateurs d'exemple"""
        return [
            UserCreate(**cls.ADMIN),
            UserCreate(**cls.PLUMBER),
            UserCreate(**cls.ELECTRICIAN),
            UserCreate(**cls.INACTIVE_USER)
        ]


class SampleTasks:
    """Données d'exemple pour les tâches"""
    
    @staticmethod
    def get_plumbing_tasks(plumber_id: int, admin_id: int):
        """Tâches de plomberie"""
        base_date = datetime.now()
        
        return [
            TaskCreate(
                title="Réparation fuite salle de bain",
                description="Fuite importante sous le lavabo de la salle de bain principale",
                assigned_to=plumber_id,
                created_by=admin_id,
                status="pending",
                priority=3,
                start_date=base_date,
                due_date=base_date + timedelta(days=1),
                estimated_time=180,
                completion_percentage=0
            ),
            TaskCreate(
                title="Installation nouveau robinet cuisine",
                description="Remplacement du robinet de cuisine par un modèle plus moderne",
                assigned_to=plumber_id,
                created_by=admin_id,
                status="in_progress", 
                priority=2,
                start_date=base_date - timedelta(days=1),
                due_date=base_date + timedelta(days=2),
                estimated_time=120,
                completion_percentage=45
            ),
            TaskCreate(
                title="Maintenance préventive canalisations",
                description="Contrôle et nettoyage des canalisations du bâtiment",
                assigned_to=plumber_id,
                created_by=admin_id,
                status="completed",
                priority=1,
                start_date=base_date - timedelta(days=5),
                due_date=base_date - timedelta(days=2),
                estimated_time=240,
                completion_percentage=100
            )
        ]
    
    @staticmethod
    def get_electrical_tasks(electrician_id: int, admin_id: int):
        """Tâches électriques"""
        base_date = datetime.now()
        
        return [
            TaskCreate(
                title="Installation éclairage LED bureau",
                description="Remplacement de tous les éclairages du bureau par des LED",
                assigned_to=electrician_id,
                created_by=admin_id,
                status="pending",
                priority=2,
                due_date=base_date + timedelta(days=7),
                estimated_time=300,
                completion_percentage=0
            ),
            TaskCreate(
                title="Réparation prise défectueuse",
                description="Prise électrique de la cuisine ne fonctionne plus",
                assigned_to=electrician_id,
                created_by=admin_id,
                status="in_progress",
                priority=3,
                start_date=base_date,
                due_date=base_date + timedelta(hours=4),
                estimated_time=60,
                completion_percentage=20
            )
        ]

    @staticmethod
    def get_urgent_task(assigned_to: int, created_by: int):
        """Tâche urgente"""
        return TaskCreate(
            title="URGENCE - Panne électrique totale",
            description="Panne électrique complète du bâtiment principal",
            assigned_to=assigned_to,
            created_by=created_by,
            status="pending",
            priority=5,  # Priorité maximale
            start_date=datetime.now(),
            due_date=datetime.now() + timedelta(hours=2),
            estimated_time=30,
            completion_percentage=0
        )