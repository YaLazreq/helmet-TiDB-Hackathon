#!/usr/bin/env python3
"""
Test script pour tester l'agent db_agent pour mettre à jour un utilisateur dans la base de données
"""

import asyncio
from src.agents.db_016 import db_agent, db_agent_creation


def test_update_user():
    """Test de mise à jour d'un utilisateur avec db_agent"""

    print("🔧 Test de mise à jour d'un utilisateur avec db_agent")
    print("-" * 60)

    # Test 1: Mettre à jour le téléphone d'un utilisateur
    print("📞 Test 1: Mise à jour du téléphone de l'utilisateur ID 2 (Jean Dupont)")
    try:
        request1 = "Update user with ID 2, set phone to '0123456999'"
        result1 = db_agent(request1)
        print(f"✅ Résultat 1: {result1}")
    except Exception as e:
        print(f"❌ Erreur 1: {e}")

    # print("\n" + "-" * 60)

    # # Test 2: Mettre à jour la spécialisation d'un utilisateur
    # print(
    #     "🔧 Test 2: Mise à jour de la spécialisation de l'utilisateur ID 3 (Marie Martin)"
    # )
    # try:
    #     request2 = "Update user with ID 3, set specialization to 'security_systems'"
    #     result2 = db_agent(request2)
    #     print(f"✅ Résultat 2: {result2}")
    # except Exception as e:
    #     print(f"❌ Erreur 2: {e}")

    # print("\n" + "-" * 60)

    # # Test 3: Mettre à jour plusieurs champs d'un utilisateur
    # print("👤 Test 3: Mise à jour multiple pour l'utilisateur ID 6 (Lucas Moreau)")
    # try:
    #     request3 = "Update user with ID 6, set phone to '0123456888' and specialization to 'hvac_expert'"
    #     result3 = db_agent(request3)
    #     print(f"✅ Résultat 3: {result3}")
    # except Exception as e:
    #     print(f"❌ Erreur 3: {e}")

    # print("\n" + "-" * 60)

    # # Test 4: Test avec un ID qui n'existe pas
    # print("❓ Test 4: Tentative de mise à jour d'un utilisateur inexistant (ID 999)")
    # try:
    #     request4 = "Update user with ID 999, set phone to '0000000000'"
    #     result4 = db_agent(request4)
    #     print(f"✅ Résultat 4: {result4}")
    # except Exception as e:
    #     print(f"❌ Erreur 4: {e}")


def test_update_task():
    """Test de mise à jour d'une tâche avec db_agent"""

    print("\n📋 Test de mise à jour d'une tâche avec db_agent")
    print("-" * 60)

    # Test: Mettre à jour l'heure de début d'une tâche
    print(
        "⏰ Test: Mise à jour de l'heure de début de la tâche ID 7 (Installation caméras)"
    )
    try:
        request = "Update task with ID 7, set start_date to '2025-09-04 15:00:00'"
        result = db_agent(request4)
        print(f"✅ Résultat: {result}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    print("🚀 Démarrage des tests db_agent...")
    print("=" * 80)

    try:
        # Test des mises à jour d'utilisateurs
        test_update_user()

        # Test des mises à jour de tâches
        # test_update_task()

        print("\n" + "=" * 80)
        print("✅ Tests db_agent terminés !")

    except Exception as e:
        print(f"💥 Erreur générale: {e}")
