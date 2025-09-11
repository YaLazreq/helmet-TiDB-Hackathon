"""
Utilitaires pour synchroniser automatiquement les vecteurs avec les données
"""

from typing import Dict, Any, Optional
import json
from .embedding.vector import TiDBVectorManager


class VectorSync:
    """Gestionnaire de synchronisation des vecteurs"""
    
    def __init__(self):
        self._vector_manager = None
    
    @property
    def vector_manager(self) -> TiDBVectorManager:
        """Initialise le gestionnaire de vecteur de manière lazy"""
        if self._vector_manager is None:
            self._vector_manager = TiDBVectorManager()
        return self._vector_manager
    
    def sync_task_vector(self, task_id: int, task_data: Dict[str, Any], action: str = "update") -> bool:
        """
        Synchronise le vecteur d'une tâche
        
        Args:
            task_id: ID de la tâche
            task_data: Données de la tâche
            action: "create", "update", "delete"
        
        Returns:
            bool: Succès de l'opération
        """
        try:
            if action == "delete":
                # TODO: Implémenter la suppression de vecteur
                print(f"⚠️  Suppression vecteur tâche {task_id} non implémentée")
                return True
            
            elif action in ["create", "update"]:
                # Créer/mettre à jour le vecteur
                doc_id = self.vector_manager.create_task_vector(task_id, task_data)
                print(f"✅ Vecteur tâche {task_id} synchronisé: {doc_id}")
                return True
                
        except Exception as e:
            print(f"❌ Erreur synchronisation vecteur tâche {task_id}: {e}")
            return False
        
        return False
    
    def sync_user_vector(self, user_id: int, user_data: Dict[str, Any], action: str = "update") -> bool:
        """
        Synchronise le vecteur d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            user_data: Données de l'utilisateur
            action: "create", "update", "delete"
        
        Returns:
            bool: Succès de l'opération
        """
        try:
            if action == "delete":
                # TODO: Implémenter la suppression de vecteur
                print(f"⚠️  Suppression vecteur utilisateur {user_id} non implémentée")
                return True
            
            elif action in ["create", "update"]:
                # Créer/mettre à jour le vecteur
                doc_id = self.vector_manager.create_user_vector(user_id, user_data)
                print(f"✅ Vecteur utilisateur {user_id} synchronisé: {doc_id}")
                return True
                
        except Exception as e:
            print(f"❌ Erreur synchronisation vecteur utilisateur {user_id}: {e}")
            return False
        
        return False


# Instance globale du synchroniseur
vector_sync = VectorSync()


def auto_sync_task_vector(task_id: int, task_data: Dict[str, Any], action: str = "update") -> None:
    """
    Fonction helper pour synchroniser automatiquement un vecteur de tâche
    Utilisée dans les outils MCP create_task et update_task
    """
    try:
        vector_sync.sync_task_vector(task_id, task_data, action)
    except Exception as e:
        # Ne pas faire échouer l'opération principale si la sync vectorielle échoue
        print(f"⚠️  Synchronisation vectorielle échouée pour tâche {task_id}: {e}")


def auto_sync_user_vector(user_id: int, user_data: Dict[str, Any], action: str = "update") -> None:
    """
    Fonction helper pour synchroniser automatiquement un vecteur d'utilisateur
    Utilisée dans les outils MCP create_user et update_user
    """
    try:
        vector_sync.sync_user_vector(user_id, user_data, action)
    except Exception as e:
        # Ne pas faire échouer l'opération principale si la sync vectorielle échoue
        print(f"⚠️  Synchronisation vectorielle échouée pour utilisateur {user_id}: {e}")