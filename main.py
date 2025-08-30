from database.schema.users import User, UserQueries, UserRepository, UserCreate
from server.mcp_server import (
    connect_to_tidb,
    insert_user,
)

import database.schema.base as base


def main():
    """Fonction principale pour tester tout"""
    print("🚀 Démarrage du test TiDB simple\n")

    # 1. Se connecter
    conn = connect_to_tidb()
    if not conn:
        print("Impossible de continuer sans connexion")
        return

    try:
        # 2. Créer la table
        base.create_table(conn, User.__tablename__, UserQueries.sql_create_table)
        print()

        # 3. Ajouter quelques utilisateurs
        user = UserRepository.create_user(
            conn,
            UserCreate(
                email="google2@example.com",
                first_name="Goo",
                last_name="Gle",
                password="password123",
            ),
        )
        print(user)

        # 4. Afficher tous les utilisateurs
        UserRepository.get_all_users(conn)
        print()

        # # 5. Chercher un utilisateur spécifique
        # print("🔍 Recherche de l'utilisateur avec l'ID 1...")
        # UserRepository.get_user_by_id(conn, 1)
        # print()

        # # 6. Mettre à jour un utilisateur
        # print("✏️  Mise à jour de l'utilisateur 1...")
        # UserRepository.update_user(conn, UserCreate(email="", first_name="Ninis"), 1)
        # UserRepository.get_user_by_id(conn, 1)
        # print()

        # # 7. Afficher tous les utilisateurs après modification
        # print("📋 État final de tous les utilisateurs :")
        # UserRepository.get_all_users(conn)
        # print()

        # # 8. Supprimer un utilisateur
        # print("🗑️  Suppression de l'utilisateur 2...")
        # UserRepository.delete_user(conn, 2)
        # UserRepository.get_all_users(conn)

    except Exception as e:
        print(f"❌ Erreur dans le programme principal : {e}")

    finally:
        # 9. Fermer la connexion
        conn.close()
        print("\n🔒 Connexion fermée")


if __name__ == "__main__":
    main()
