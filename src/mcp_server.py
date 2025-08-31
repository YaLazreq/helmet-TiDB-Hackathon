# Connexion TiDB ultra-simple pour débuter
# Juste les concepts de base sans complications

import pymysql
from datetime import datetime
import database.config as config

# from database.schema.users import


# =============================================================================
# 2. FONCTION DE CONNEXION SIMPLE
# =============================================================================


def connect_to_tidb():
    """Se connecter à TiDB - version simple"""
    try:
        connection = pymysql.connect(**config.DB_CONFIG)
        print("✅ Connexion à TiDB réussie !")
        return connection
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return None


# =============================================================================
# 3. CRÉER UNE TABLE SIMPLE
# =============================================================================


def create_simple_table(connection: pymysql.Connection, sql_command: str):
    """Créer une table users basée sur le schéma SQLAlchemy"""
    try:
        with connection.cursor() as cursor:
            # SQL généré à partir du modèle User SQLAlchemy
            create_table_sql = sql_command
            cursor.execute(create_table_sql)

            # Créer les index définis dans le modèle User
            # indexes = [
            #     "CREATE INDEX IF NOT EXISTS idx_username ON users (username)",
            #     "CREATE INDEX IF NOT EXISTS idx_email ON users (email)",
            #     "CREATE INDEX IF NOT EXISTS idx_active ON users (is_active)",
            # ]

            # for index_sql in indexes:
            #     cursor.execute(index_sql)

            connection.commit()
            print("✅ Table 'users' créée avec le schéma SQLAlchemy !")
            print("✅ Index créés pour optimiser les performances")
    except Exception as e:
        print(f"❌ Erreur lors de la création de table : {e}")


# =============================================================================
# 4. INSÉRER DES DONNÉES SIMPLES
# =============================================================================


def insert_user(connection, name, email, password):
    """Ajouter un utilisateur"""
    try:
        with connection.cursor() as cursor:
            # SQL pour insérer
            insert_sql = "INSERT INTO users (first_name, email, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(insert_sql, (name, email, password))
            connection.commit()

            # Récupérer l'ID du nouvel utilisateur
            new_id = cursor.lastrowid
            print(f"✅ Utilisateur ajouté avec l'ID : {new_id}")
            return new_id
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion : {e}")
        return None

    # =============================================================================
    # 5. LIRE DES DONNÉES SIMPLES
    # =============================================================================

    # def get_all_users(connection):
    """Récupérer tous les utilisateurs"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()

            print(f"\n📋 {len(results)} utilisateur(s) trouvé(s) :")
            for row in results:
                print(f"  ID: {row[0]}, Nom: {row[1]}, Email: {row[2]}, Créé: {row[3]}")

            return results
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return []


# def get_user_by_id(connection, user_id):
#     """Récupérer un utilisateur par son ID"""
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
#             result = cursor.fetchone()

#             if result:
#                 print(f"👤 Utilisateur trouvé : {result[1]} ({result[2]})")
#             else:
#                 print("❌ Aucun utilisateur trouvé avec cet ID")

#             return result
#     except Exception as e:
#         print(f"❌ Erreur lors de la recherche : {e}")
#         return None


# =============================================================================
# 6. METTRE À JOUR DES DONNÉES
# =============================================================================


# def update_user(connection, user_id, new_name=None, new_email=None):
#     """Modifier un utilisateur"""
#     try:
#         with connection.cursor() as cursor:
#             updates = []
#             values = []

#             if new_name:
#                 updates.append("name = %s")
#                 values.append(new_name)

#             if new_email:
#                 updates.append("email = %s")
#                 values.append(new_email)

#             if not updates:
#                 print("❌ Rien à mettre à jour")
#                 return

#             # Ajouter l'ID à la fin des valeurs
#             values.append(user_id)

#             update_sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
#             cursor.execute(update_sql, values)
#             connection.commit()

#             if cursor.rowcount > 0:
#                 print(f"✅ Utilisateur {user_id} mis à jour")
#             else:
#                 print("❌ Aucun utilisateur trouvé avec cet ID")

#     except Exception as e:
#         print(f"❌ Erreur lors de la mise à jour : {e}")


# =============================================================================
# 7. SUPPRIMER DES DONNÉES
# =============================================================================


# def delete_user(connection, user_id):
#     """Supprimer un utilisateur"""
#     try:
#         with connection.cursor(pymysql.cursors.DictCursor) as cursor:
#             cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
#             connection.commit()

#             if cursor.rowcount > 0:
#                 print(f"✅ Utilisateur {user_id} supprimé")
#             else:
#                 print("❌ Aucun utilisateur trouvé avec cet ID")

#     except Exception as e:
#         print(f"❌ Erreur lors de la suppression : {e}")


# =============================================================================
# 9. FONCTIONS D'AIDE POUR COMPRENDRE
# =============================================================================


# def explain_concepts():
#     """Expliquer les concepts de base"""
#     print(
#         """
#     🎓 CONCEPTS DE BASE EXPLIQUÉS :

#     1. CONNEXION :
#        - pymysql.connect() ouvre une connexion à TiDB
#        - Comme ouvrir une porte vers la base de données

#     2. CURSOR :
#        - connection.cursor() crée un "curseur"
#        - C'est comme un pointeur pour exécuter des commandes SQL

#     3. SQL :
#        - CREATE TABLE = créer une nouvelle table
#        - INSERT = ajouter des données
#        - SELECT = lire/récupérer des données
#        - UPDATE = modifier des données existantes
#        - DELETE = supprimer des données

#     4. COMMIT :
#        - connection.commit() sauvegarde les changements
#        - Comme appuyer sur "Sauvegarder" dans un document

#     5. PARAMÈTRES (%s) :
#        - Les %s évitent les injections SQL
#        - Plus sécurisé que de coller directement les valeurs
#     """
#     )


# def test_connection_only():
#     """Juste tester la connexion sans rien faire d'autre"""
#     print("🧪 Test de connexion simple...")

#     conn = connect_to_tidb()
#     if conn:
#         try:
#             with conn.cursor() as cursor:
#                 cursor.execute("SELECT 1 as test")
#                 result = cursor.fetchone()
#                 print(f"✅ Test réussi ! Résultat : {result[0]}")
#         except Exception as e:
#             print(f"❌ Test échoué : {e}")
#         finally:
#             conn.close()
#             print("🔒 Connexion de test fermée")
#     else:
#         print("❌ Impossible de se connecter")
