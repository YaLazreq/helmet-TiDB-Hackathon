#!/usr/bin/env python3
"""
Script pour synchroniser les vecteurs avec les dernières données
Usage: python sync_vectors.py [--tasks] [--users] [--all]
"""

import asyncio
import sys
import os
import argparse

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.mcp_db.tools.embedding.vector import TiDBVectorManager
from src.mcp.db_client import connect_db_mcp, get_db_mcp_tools


async def sync_vectors(sync_tasks: bool = True, sync_users: bool = True):
    """Synchronise les vecteurs avec les données actuelles"""
    
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
    
    if sync_users:
        print("\n📊 Synchronisation des vecteurs utilisateurs...")
        users_result = get_users_tool.invoke({})
        
        if isinstance(users_result, str):
            import json
            try:
                users_data = json.loads(users_result)
                if users_data.get("success") and "users" in users_data:
                    users = users_data["users"]
                    print(f"✅ {len(users)} utilisateurs à synchroniser")
                    
                    for user in users:
                        try:
                            user_id = user.get("id")
                            if user_id:
                                print(f"🔄 Sync utilisateur {user_id}: {user.get('first_name', '')} {user.get('last_name', '')}")
                                doc_id = vector_manager.create_user_vector(user_id, user)
                                print(f"✅ Synchronisé: {doc_id}")
                        except Exception as e:
                            if "Duplicate entry" in str(e):
                                print(f"⚠️  Utilisateur {user_id} déjà vectorisé, ignoré")
                            else:
                                print(f"❌ Erreur sync utilisateur {user_id}: {e}")
                else:
                    print(f"❌ Erreur dans les données utilisateurs: {users_data}")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON utilisateurs: {e}")
    
    if sync_tasks:
        print("\n📊 Synchronisation des vecteurs tâches...")
        tasks_result = get_tasks_tool.invoke({})
        
        if isinstance(tasks_result, str):
            try:
                tasks_data = json.loads(tasks_result)
                if tasks_data.get("success") and "tasks" in tasks_data:
                    tasks = tasks_data["tasks"]
                    print(f"✅ {len(tasks)} tâches à synchroniser")
                    
                    for task in tasks:
                        try:
                            task_id = task.get("id")
                            if task_id:
                                print(f"🔄 Sync tâche {task_id}: {task.get('title', 'Sans titre')}")
                                doc_id = vector_manager.create_task_vector(task_id, task)
                                print(f"✅ Synchronisé: {doc_id}")
                        except Exception as e:
                            if "Duplicate entry" in str(e):
                                print(f"⚠️  Tâche {task_id} déjà vectorisée, ignorée")
                            else:
                                print(f"❌ Erreur sync tâche {task_id}: {e}")
                else:
                    print(f"❌ Erreur dans les données tâches: {tasks_data}")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur parsing JSON tâches: {e}")
    
    print("\n🎉 Synchronisation terminée!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchroniser les vecteurs")
    parser.add_argument("--tasks", action="store_true", help="Synchroniser uniquement les tâches")
    parser.add_argument("--users", action="store_true", help="Synchroniser uniquement les utilisateurs")
    parser.add_argument("--all", action="store_true", help="Synchroniser tout (par défaut)")
    
    args = parser.parse_args()
    
    # Par défaut, synchroniser tout
    if not args.tasks and not args.users:
        args.all = True
    
    sync_tasks = args.all or args.tasks
    sync_users = args.all or args.users
    
    print("🚀 Démarrage de la synchronisation des vecteurs...")
    print(f"📋 Tâches: {'✅' if sync_tasks else '❌'}")
    print(f"👥 Utilisateurs: {'✅' if sync_users else '❌'}")
    
    asyncio.run(sync_vectors(sync_tasks, sync_users))