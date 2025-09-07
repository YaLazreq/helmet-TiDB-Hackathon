#!/usr/bin/env python3
"""
Version simple pour exécuter create_tables.sql
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from mcp.mcp_db.mcp_init import get_db_connection


def execute_schema():
    """Exécute le fichier create_tables.sql"""

    # Lire le fichier SQL
    with open("create_tables.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Connexion DB
    db = get_db_connection()
    if not db:
        print("❌ Connexion DB échouée")
        return False

    cursor = db.cursor(buffered=True)

    try:
        # Exécuter le contenu SQL
        # Utiliser multi=True pour exécuter plusieurs requêtes
        results = cursor.execute(sql_content)

        # Parcourir tous les résultats
        for result in results:
            if result.with_rows:
                result.fetchall()  # Consommer les résultats

        db.commit()
        print("✅ Schéma créé avec succès !")

        # Vérifier que la table existe
        cursor.execute("SHOW TABLES LIKE 'tasks'")
        if cursor.fetchone():
            print("✅ Table 'tasks' créée")

            cursor.execute("SELECT COUNT(*) FROM tasks")
            count = cursor.fetchone()[0]
            print(f"✅ {count} tâches d'exemple insérées")

        return True

    except Exception as e:
        print(f"❌ Erreur : {e}")
        db.rollback()
        return False

    finally:
        cursor.close()


if __name__ == "__main__":
    execute_schema()
