#!/usr/bin/env python3
"""
Script pour recréer tous les vecteurs après avoir refait la database
"""

import asyncio
import sys
import os

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.mcp_db.tools.embedding.vector import TiDBVectorManager
from src.mcp.db_client import connect_db_mcp, get_db_mcp_tools


async def rebuild_all_vectors():
    """Recrée tous les vecteurs pour users et tasks"""
    
    print("🔄 Connexion à MCP DB...")
    await connect_db_mcp()
    
    # Obtenir les outils MCP
    tools = get_db_mcp_tools(["get_users", "get_tasks"])
    get_users_tool = None
    get_tasks_tool = None
    
    for tool in tools:
        if tool.name == "get_users":
            get_users_tool = tool
        elif tool.name == "get_tasks":
            get_tasks_tool = tool
    
    if not get_users_tool or not get_tasks_tool:
        print("❌ Erreur: Outils MCP non trouvés")
        return
    
    print("🔄 Initialisation du gestionnaire de vecteurs...")
    vector_manager = TiDBVectorManager()
    
    # 1. Recréer les vecteurs des utilisateurs
    print("\n📊 Récupération des utilisateurs...")
    users_result = get_users_tool.invoke({})
    print(f"Users result type: {type(users_result)}")
    
    if isinstance(users_result, str):
        import json
        try:
            users_data = json.loads(users_result)
            if users_data.get("success") and "users" in users_data:
                users = users_data["users"]
                print(f"✅ {len(users)} utilisateurs trouvés")
                
                for user in users:
                    try:
                        user_id = user.get("id")
                        if user_id:
                            print(f"🔄 Création vecteur pour utilisateur {user_id}: {user.get('first_name', '')} {user.get('last_name', '')}")
                            doc_id = vector_manager.create_user_vector(user_id, user)
                            print(f"✅ Vecteur créé: {doc_id}")
                        else:
                            print(f"⚠️  Utilisateur sans ID: {user}")
                    except Exception as e:
                        print(f"❌ Erreur création vecteur utilisateur {user_id}: {e}")
            else:
                print(f"❌ Erreur dans les données utilisateurs: {users_data}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON utilisateurs: {e}")
    else:
        print(f"❌ Format inattendu pour les utilisateurs: {type(users_result)}")
    
    # 2. Recréer les vecteurs des tâches
    print("\n📊 Récupération des tâches...")
    tasks_result = get_tasks_tool.invoke({})
    
    if isinstance(tasks_result, str):
        try:
            tasks_data = json.loads(tasks_result)
            if tasks_data.get("success") and "tasks" in tasks_data:
                tasks = tasks_data["tasks"]
                print(f"✅ {len(tasks)} tâches trouvées")
                
                for task in tasks:
                    try:
                        task_id = task.get("id")
                        if task_id:
                            print(f"🔄 Création vecteur pour tâche {task_id}: {task.get('title', 'Sans titre')}")
                            doc_id = vector_manager.create_task_vector(task_id, task)
                            print(f"✅ Vecteur créé: {doc_id}")
                        else:
                            print(f"⚠️  Tâche sans ID: {task}")
                    except Exception as e:
                        print(f"❌ Erreur création vecteur tâche {task_id}: {e}")
            else:
                print(f"❌ Erreur dans les données tâches: {tasks_data}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON tâches: {e}")
    else:
        print(f"❌ Format inattendu pour les tâches: {type(tasks_result)}")
    
    print("\n🎉 Reconstruction des vecteurs terminée!")


async def test_vector_search():
    """Test la recherche vectorielle après reconstruction"""
    print("\n🔍 Test de recherche vectorielle...")
    
    vector_manager = TiDBVectorManager()
    
    # Test recherche de tâches similaires
    print("🔍 Recherche de tâches similaires à 'electrical installation'...")
    similar_tasks = vector_manager.search_similar_tasks("electrical installation", k=3)
    print(f"✅ {len(similar_tasks)} tâches similaires trouvées")
    for i, task in enumerate(similar_tasks, 1):
        print(f"  {i}. Tâche ID: {task.metadata.get('task_id')} - Score: {(1-task.distance)*100:.1f}% - {task.metadata.get('title', 'Sans titre')}")
    
    # Test recherche d'utilisateurs similaires
    print("\n🔍 Recherche d'utilisateurs avec compétences électriques...")
    similar_users = vector_manager.search_similar_users("electrical installation experience", k=3)
    print(f"✅ {len(similar_users)} utilisateurs similaires trouvés")
    for i, user in enumerate(similar_users, 1):
        print(f"  {i}. User ID: {user.metadata.get('user_id')} - Score: {(1-user.distance)*100:.1f}% - {user.metadata.get('name', 'Sans nom')}")


if __name__ == "__main__":
    print("🚀 Démarrage de la reconstruction des vecteurs...")
    
    asyncio.run(rebuild_all_vectors())
    asyncio.run(test_vector_search())
    
    print("\n✅ Script terminé!")