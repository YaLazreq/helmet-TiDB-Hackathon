#!/usr/bin/env python3
"""
Script to populate TiDB vector tables from existing JSON vectors in tasks and users tables.
This bridges the gap between JSON storage and vector search functionality.
"""

import sys
import os
import json

# Add the path to access the MCP modules
sys.path.append("/Users/yan/Development/TiDB/tiDB-Hackathon/src/mcp/mcp_db")
sys.path.append("/Users/yan/Development/TiDB/tiDB-Hackathon/src/mcp/mcp_db/tools/embedding")

from mcp_init import get_db_connection
from vector import TiDBVectorManager


def get_all_tasks_with_vectors():
    """Get all tasks from database with their requirement vectors"""
    db = get_db_connection()
    if not db:
        print("❌ Database connection failed")
        return []

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute(
            """
            SELECT id, title, description, skill_requirements, trade_category, 
                   requirements_vector
            FROM tasks 
            WHERE requirements_vector IS NOT NULL
            ORDER BY id
        """
        )

        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        tasks = []
        for row in results:
            task_dict = {}
            for i, value in enumerate(row):
                column_name = columns[i]
                if column_name == "skill_requirements" and value:
                    try:
                        task_dict[column_name] = (
                            json.loads(value) if isinstance(value, str) else value or []
                        )
                    except json.JSONDecodeError:
                        task_dict[column_name] = []
                else:
                    task_dict[column_name] = value

            tasks.append(task_dict)

        return tasks

    except Exception as e:
        print(f"❌ Error fetching tasks: {e}")
        return []
    finally:
        cursor.close()


def get_all_users_with_vectors():
    """Get all users from database with their skills vectors"""
    db = get_db_connection()
    if not db:
        print("❌ Database connection failed")
        return []

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute(
            """
            SELECT id, first_name, last_name, role_description,
                   primary_skills, secondary_skills, trade_categories, 
                   skills_vector
            FROM users 
            WHERE skills_vector IS NOT NULL
            ORDER BY id
        """
        )

        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        users = []
        for row in results:
            user_dict = {}
            for i, value in enumerate(row):
                column_name = columns[i]
                if (
                    column_name
                    in ["primary_skills", "secondary_skills", "trade_categories"]
                    and value
                ):
                    try:
                        user_dict[column_name] = (
                            json.loads(value) if isinstance(value, str) else value or []
                        )
                    except json.JSONDecodeError:
                        user_dict[column_name] = []
                else:
                    user_dict[column_name] = value

            users.append(user_dict)

        return users

    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return []
    finally:
        cursor.close()


def build_task_searchable_text(task):
    """Build searchable text for a task using the specified fields"""
    components = []
    
    # Title
    if task.get("title"):
        components.append(f"Title: {task['title']}")
    
    # Description
    if task.get("description"):
        components.append(f"Description: {task['description']}")
    
    # Skill requirements
    if task.get("skill_requirements"):
        if isinstance(task["skill_requirements"], list):
            components.append(f"Skills required: {', '.join(task['skill_requirements'])}")
        else:
            components.append(f"Skills required: {task['skill_requirements']}")
    
    # Trade category
    if task.get("trade_category"):
        components.append(f"Trade category: {task['trade_category']}")
    
    return " | ".join(components)


def build_user_searchable_text(user):
    """Build searchable text for a user using the specified fields"""
    components = []
    
    # Name (though not in your list, keeping for context)
    name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
    if name:
        components.append(f"Name: {name}")
    
    # Role description
    if user.get("role_description"):
        components.append(f"Role: {user['role_description']}")
    
    # Primary skills
    if user.get("primary_skills"):
        components.append(f"Primary skills: {', '.join(user['primary_skills'])}")
    
    # Secondary skills
    if user.get("secondary_skills"):
        components.append(f"Secondary skills: {', '.join(user['secondary_skills'])}")
    
    # Trade categories
    if user.get("trade_categories"):
        components.append(f"Trade categories: {', '.join(user['trade_categories'])}")
    
    return " | ".join(components)


def populate_task_vectors():
    """Populate the TiDB task_vectors table from existing task vectors"""
    print("🔍 Fetching tasks with requirement vectors...")
    tasks = get_all_tasks_with_vectors()
    
    if not tasks:
        print("❌ No tasks with vectors found")
        return 0
    
    print(f"📋 Found {len(tasks)} tasks with vectors")
    
    try:
        vector_manager = TiDBVectorManager()
        vector_client = vector_manager.get_tasks_vector_client()
        
        success_count = 0
        error_count = 0
        
        for task in tasks:
            try:
                # Parse the stored vector
                vector_json = task["requirements_vector"]
                if isinstance(vector_json, str):
                    vector = json.loads(vector_json)
                else:
                    vector = vector_json
                
                # Build searchable text
                searchable_text = build_task_searchable_text(task)
                
                # Document ID
                doc_id = f"task_{task['id']}"
                
                print(f"  📝 Task {task['id']}: {task['title'][:50]}...")
                
                # Insert into vector table
                vector_client.insert(
                    ids=[doc_id],
                    texts=[searchable_text],
                    embeddings=[vector],
                    metadatas=[{
                        "task_id": task['id'],
                        "title": task.get('title', ''),
                        "trade_category": task.get('trade_category', ''),
                        "priority": 0,  # Default, could be enhanced
                        "status": "pending"  # Default, could be enhanced
                    }]
                )
                
                print(f"  ✅ Successfully populated task {task['id']}")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ Error populating task {task['id']}: {e}")
                error_count += 1
        
        print(f"\n📊 Task vectors: {success_count} successful, {error_count} errors")
        return success_count
        
    except Exception as e:
        print(f"❌ Error initializing task vector client: {e}")
        return 0


def populate_user_vectors():
    """Populate the TiDB user_vectors table from existing user vectors"""
    print("🔍 Fetching users with skills vectors...")
    users = get_all_users_with_vectors()
    
    if not users:
        print("❌ No users with vectors found")
        return 0
    
    print(f"📋 Found {len(users)} users with vectors")
    
    try:
        vector_manager = TiDBVectorManager()
        vector_client = vector_manager.get_users_vector_client()
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                # Parse the stored vector
                vector_json = user["skills_vector"]
                if isinstance(vector_json, str):
                    vector = json.loads(vector_json)
                else:
                    vector = vector_json
                
                # Build searchable text
                searchable_text = build_user_searchable_text(user)
                
                # Document ID
                doc_id = f"user_{user['id']}"
                
                name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                print(f"  👤 User {user['id']}: {name}")
                
                # Insert into vector table
                vector_client.insert(
                    ids=[doc_id],
                    texts=[searchable_text],
                    embeddings=[vector],
                    metadatas=[{
                        "user_id": user['id'],
                        "name": name,
                        "role": user.get('role_description', ''),
                        "primary_skills": user.get('primary_skills', []),
                        "trade_categories": user.get('trade_categories', []),
                        "experience_years": 0  # Default, could be enhanced
                    }]
                )
                
                print(f"  ✅ Successfully populated user {user['id']}")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ Error populating user {user['id']}: {e}")
                error_count += 1
        
        print(f"\n📊 User vectors: {success_count} successful, {error_count} errors")
        return success_count
        
    except Exception as e:
        print(f"❌ Error initializing user vector client: {e}")
        return 0


def main():
    """Main function to populate both vector tables"""
    print("🚀 Starting vector table population...\n")
    
    # Populate task vectors
    print("=" * 60)
    print("📋 POPULATING TASK VECTORS")
    print("=" * 60)
    task_count = populate_task_vectors()
    
    print("\n")
    
    # Populate user vectors
    print("=" * 60)
    print("👥 POPULATING USER VECTORS")
    print("=" * 60)
    user_count = populate_user_vectors()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"✅ Tasks populated: {task_count}")
    print(f"✅ Users populated: {user_count}")
    print("=" * 60)
    
    if task_count > 0 and user_count > 0:
        print("\n🎉 Vector tables are now ready for search operations!")
        print("You can now use find_best_workers_for_task() and search_similar_tasks()!")
    else:
        print("\n⚠️  Some vector tables may be empty. Check the logs above.")


if __name__ == "__main__":
    main()