from database.schema.users import User, UserQueries, UserRepository, UserCreate
from database.schema.tasks import Task, TaskQueries, TaskRepository, TaskCreate
from mcp_server import (
    connect_to_tidb,
    insert_user,
)
import datetime as dt

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
        base.create_table(conn, Task.__tablename__, TaskQueries.sql_create_table)
        print()

        # UserRepository.delete_user(conn, 30001)

        # 3. Ajouter quelques utilisateurs
        # user = UserRepository.create_user(
        #     conn,
        #     UserCreate(
        #         email="yanis.lazreq@gmail.com",
        #         password="password123",
        #         first_name="Yanis",
        #         last_name="Lazreq",
        #         phone="0123456789",
        #         is_active=True,
        #         is_admin=False,
        #         role="technician",
        #         specialization="plumber",
        #     ),
        # )
        # user2 = UserRepository.create_user(
        #     conn,
        #     UserCreate(
        #         email="ylianeGenteleme@gmail.com",
        #         first_name="Yliane",
        #         last_name="GEntelemnt",
        #         password="password123",
        #         phone="0123456789",
        #         role="admin",
        #         specialization="electrician",
        #         is_active=True,
        #         is_admin=False,
        #     ),
        # )
        # user3 = UserRepository.create_user(
        #     conn,
        #     UserCreate(
        #         email="renault@example.com",
        #         first_name="jean",
        #         last_name="grodo",
        #         password="password123",
        #         phone="0123456789",
        #         role="admin",
        #         specialization="electrician",
        #         is_active=True,
        #         is_admin=False,
        #     ),
        # )
        # # print(user)

        # 4. Afficher tous les utilisateurs
        UserRepository.get_all_users(conn)
        print()

        # # 5. Créer 3 tâches avec valeurs aléatoires
        task1 = TaskRepository.create_task(
            conn,
            TaskCreate(
                title="Réparation plomberie urgente",
                description="Fuite importante dans la salle de bain principale, intervention immédiate requise.",
                assigned_to=1,
                status="in_progress",
                priority=3,
                start_date=dt.datetime.now(),
                due_date=dt.datetime.now() + dt.timedelta(days=2),
                created_by=2,
                completion_percentage=20,
                estimated_time=120,
            ),
        )
        print(task1)
        # task2 = TaskRepository.create_task(
        #     conn,
        #     TaskCreate(
        #         title="Installation électrique bureau",
        #         description="Mise en place du réseau électrique complet pour le nouveau bureau au 3ème étage.",
        #         assigned_to=2,
        #         status="pending",
        #         priority=2,
        #         start_date=dt.datetime.now(),
        #         due_date=dt.datetime.now() + dt.timedelta(days=2),
        #         created_by=1,
        #         completion_percentage=50,
        #         estimated_time=90,
        #     ),
        # )
        # task3 = TaskRepository.create_task(
        #     conn,
        #     TaskCreate(
        #         title="Maintenance préventive chauffage",
        #         description="Contrôle annuel et nettoyage du système de chauffage central avant l'hiver.",
        #         assigned_to=2,
        #         status="pending",
        #         priority=1,
        #         start_date=dt.datetime.now(),
        #         due_date=dt.datetime.now() + dt.timedelta(days=2),
        #         created_by=3,
        #         completion_percentage=50,
        #         estimated_time=90,
        #     ),
        # )

        TaskRepository.update_task(
            conn,
            TaskCreate(
                title="nananinananère",
            ),
            task_id=1,
        )

        print(TaskRepository.get_task_by_id(conn, 1))

        # Tas.get_all_users(conn)
        # print()
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
