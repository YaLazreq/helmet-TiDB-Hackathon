#!/usr/bin/env python3
"""
Script amélioré pour exécuter le fichier create_tables.sql
Gère mieux le parsing des requêtes SQL multiples
"""

import os
import sys
import re
from pathlib import Path

# Add the src directory to Python path to import db_client
current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

try:
    from src.mcp.mcp_db.mcp_init import get_db_connection
except ImportError:
    print("❌ Erreur : Impossible d'importer get_db_connection")
    print("Assurez-vous que le module db_client est accessible")
    sys.exit(1)


def parse_sql_statements(sql_content: str) -> list:
    """
    Parse le contenu SQL en instructions individuelles
    Gère les commentaires et les requêtes multi-lignes
    """
    # Supprimer les commentaires SQL (-- commentaire)
    lines = []
    for line in sql_content.split("\n"):
        # Enlever les commentaires en fin de ligne
        if "--" in line:
            line = line[: line.index("--")]
        line = line.strip()
        if line:
            lines.append(line)

    # Rejoindre toutes les lignes
    clean_sql = " ".join(lines)

    # Diviser par les points-virgules, mais pas ceux dans les chaînes
    statements = []
    current_statement = ""
    in_string = False
    escape_next = False
    quote_char = None

    for i, char in enumerate(clean_sql):
        if escape_next:
            current_statement += char
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            current_statement += char
            continue

        if not in_string and char in ["'", '"']:
            in_string = True
            quote_char = char
            current_statement += char
        elif in_string and char == quote_char:
            in_string = False
            quote_char = None
            current_statement += char
        elif not in_string and char == ";":
            # Fin d'instruction
            current_statement = current_statement.strip()
            if current_statement and current_statement.upper() != "COMMIT":
                statements.append(current_statement)
            current_statement = ""
        else:
            current_statement += char

    # Ajouter la dernière instruction si elle n'est pas vide
    current_statement = current_statement.strip()
    if current_statement and current_statement.upper() != "COMMIT":
        statements.append(current_statement)

    return statements


def execute_sql_file(file_path: str) -> bool:
    """
    Exécute un fichier SQL avec un parsing amélioré
    """
    if not os.path.exists(file_path):
        print(f"❌ Erreur : Fichier {file_path} introuvable")
        return False

    # Lire le fichier SQL
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            sql_content = file.read()
    except Exception as e:
        print(f"❌ Erreur lecture fichier : {e}")
        return False

    # Parser les instructions SQL
    try:
        statements = parse_sql_statements(sql_content)
        print(f"📝 Trouvé {len(statements)} requêtes SQL à exécuter...")

        # Afficher un aperçu des requêtes trouvées
        for i, stmt in enumerate(statements[:5], 1):
            stmt_type = stmt.split()[0].upper()
            print(f"   {i}. {stmt_type} - {stmt[:50]}...")

        if len(statements) > 5:
            print(f"   ... et {len(statements) - 5} autres requêtes")

    except Exception as e:
        print(f"❌ Erreur parsing SQL : {e}")
        return False

    # Connexion à la base de données
    db = get_db_connection()
    if not db:
        print("❌ Erreur : Impossible de se connecter à la base de données")
        return False

    cursor = db.cursor(buffered=True)
    success_count = 0
    error_count = 0

    try:
        # Exécuter chaque requête individuellement
        for i, statement in enumerate(statements, 1):
            try:
                print(f"⏳ Exécution requête {i}/{len(statements)}...")

                # Debug : afficher la requête si elle est courte
                if len(statement) < 200:
                    print(f"   SQL: {statement}")

                cursor.execute(statement)
                db.commit()  # Commit après chaque requête

                # Analyser le type de requête et afficher un message approprié
                stmt_upper = statement.upper().strip()

                if stmt_upper.startswith("CREATE TABLE"):
                    table_name = re.search(
                        r"CREATE TABLE (?:IF NOT EXISTS )?([^\s(]+)", stmt_upper
                    )
                    table_name = table_name.group(1) if table_name else "table"
                    print(f"✅ Requête {i} : Table {table_name} créée")

                elif stmt_upper.startswith("CREATE VIEW"):
                    view_name = re.search(r"CREATE VIEW ([^\s(]+)", stmt_upper)
                    view_name = view_name.group(1) if view_name else "view"
                    print(f"✅ Requête {i} : Vue {view_name} créée")

                elif stmt_upper.startswith("INSERT"):
                    affected_rows = cursor.rowcount
                    print(f"✅ Requête {i} : {affected_rows} lignes insérées")

                elif stmt_upper.startswith("CREATE INDEX"):
                    print(f"✅ Requête {i} : Index créé")

                else:
                    print(f"✅ Requête {i} : Exécutée avec succès")

                success_count += 1

            except Exception as e:
                print(f"⚠️  Erreur requête {i} : {e}")
                print(f"   SQL: {statement[:200]}...")
                error_count += 1

                # Arrêter en cas d'erreur critique (ex: table manquante)
                if (
                    "doesn't exist" in str(e).lower()
                    or "unknown table" in str(e).lower()
                ):
                    print("❌ Erreur critique détectée - arrêt de l'exécution")
                    break

                continue

        print(f"\n📊 Résumé : {success_count} succès, {error_count} erreurs")
        return error_count == 0

    except Exception as e:
        print(f"❌ Erreur générale : {e}")
        db.rollback()
        return False

    finally:
        cursor.close()


def main():
    """Fonction principale"""
    print("🚀 Script d'exécution du schéma de base de données")
    print("=" * 50)

    # Chemin vers le fichier SQL
    sql_file_path = "src/mcp/mcp_db/schema/create_tables.sql"

    if not os.path.exists(sql_file_path):
        print(f"❌ Fichier {sql_file_path} introuvable")
        print(f"Répertoire courant : {os.getcwd()}")
        return

    print(f"📁 Fichier SQL : {sql_file_path}")

    # Demander confirmation
    confirm = (
        input("\n❓ Voulez-vous exécuter ce fichier SQL ? (y/n) : ").lower().strip()
    )

    if confirm not in ["y", "yes", "o", "oui"]:
        print("❌ Opération annulée")
        return

    # Exécuter le fichier
    success = execute_sql_file(sql_file_path)

    if success:
        print("\n✅ Le schéma de base de données a été créé avec succès !")
        print("\n📊 Vous pouvez maintenant utiliser les outils MCP pour :")
        print("  • Créer des tâches")
        print("  • Rechercher des tâches")
        print("  • Mettre à jour des tâches")
        print("  • Consulter les vues (active_tasks, overdue_tasks, etc.)")
    else:
        print("\n❌ Erreurs lors de l'exécution du schéma")


if __name__ == "__main__":
    main()
