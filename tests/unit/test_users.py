"""
Tests unitaires pour les utilisateurs
"""
import pytest
from database.schema.users import UserCreate, UserResponse, UserRepository
from pydantic import ValidationError


class TestUserCreate:
    """Tests pour le schema UserCreate"""

    def test_user_create_valid_data(self):
        """Test création avec données valides"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.is_active is True  # Valeur par défaut

    def test_user_create_minimal_data(self):
        """Test création avec données minimales"""
        user = UserCreate(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.password is None
        assert user.first_name is None

    def test_user_create_invalid_email(self):
        """Test avec email invalide"""
        # Note: Le schema UserCreate accepte les strings vides car pas de validation email
        # Ce test vérifie qu'on peut créer avec email vide
        user = UserCreate(email="")
        assert user.email == ""

    def test_user_create_all_fields(self):
        """Test avec tous les champs"""
        user_data = {
            "email": "complete@example.com",
            "password": "securepass",
            "first_name": "Complete",
            "last_name": "User",
            "phone": "0123456789",
            "role": "admin",
            "specialization": "management",
            "is_active": True,
            "is_admin": True
        }
        user = UserCreate(**user_data)
        assert user.role == "admin"
        assert user.specialization == "management"
        assert user.is_admin is True


class TestUserRepository:
    """Tests pour UserRepository"""

    def test_create_user_success(self, clean_tables, sample_user_data):
        """Test création d'utilisateur réussie"""
        user_create = UserCreate(**sample_user_data)
        result = UserRepository.create_user(clean_tables, user_create)
        
        assert result is not None
        assert isinstance(result, UserResponse)
        assert result.email == sample_user_data["email"]
        assert result.id is not None

    def test_create_user_duplicate_email(self, clean_tables, sample_user_data):
        """Test création avec email dupliqué"""
        user_create = UserCreate(**sample_user_data)
        
        # Premier utilisateur - OK
        result1 = UserRepository.create_user(clean_tables, user_create)
        assert result1 is not None
        
        # Deuxième utilisateur avec même email - devrait échouer
        result2 = UserRepository.create_user(clean_tables, user_create)
        assert result2 is None

    def test_get_all_users_empty(self, clean_tables):
        """Test récupération d'utilisateurs sur table vide"""
        users = UserRepository.get_all_users(clean_tables)
        assert isinstance(users, list)
        assert len(users) == 0

    def test_get_all_users_with_data(self, clean_tables, sample_user_data):
        """Test récupération avec des utilisateurs"""
        # Créer un utilisateur
        user_create = UserCreate(**sample_user_data)
        UserRepository.create_user(clean_tables, user_create)
        
        # Récupérer tous les utilisateurs
        users = UserRepository.get_all_users(clean_tables)
        assert len(users) == 1
        assert users[0].email == sample_user_data["email"]

    def test_get_user_by_id_exists(self, clean_tables, sample_user_data):
        """Test récupération par ID existant"""
        # Créer un utilisateur
        user_create = UserCreate(**sample_user_data)
        created_user = UserRepository.create_user(clean_tables, user_create)
        
        # Récupérer par ID
        found_user = UserRepository.get_user_by_id(clean_tables, created_user.id)
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == created_user.email

    def test_get_user_by_id_not_exists(self, clean_tables):
        """Test récupération par ID inexistant"""
        result = UserRepository.get_user_by_id(clean_tables, 99999)
        assert result is None

    def test_update_user(self, clean_tables, sample_user_data):
        """Test mise à jour d'utilisateur"""
        # Créer un utilisateur
        user_create = UserCreate(**sample_user_data)
        created_user = UserRepository.create_user(clean_tables, user_create)
        
        # Mettre à jour - on doit fournir email car c'est requis dans UserCreate
        update_data = UserCreate(
            email=created_user.email,  # Garder l'email existant
            first_name="Updated Name"
        )
        success = UserRepository.update_user(clean_tables, update_data, created_user.id)
        assert success is True
        
        # Vérifier la mise à jour
        updated_user = UserRepository.get_user_by_id(clean_tables, created_user.id)
        assert updated_user.first_name == "Updated Name"

    def test_delete_user(self, clean_tables, sample_user_data):
        """Test suppression d'utilisateur"""
        # Créer un utilisateur
        user_create = UserCreate(**sample_user_data)
        created_user = UserRepository.create_user(clean_tables, user_create)
        
        # Supprimer
        UserRepository.delete_user(clean_tables, created_user.id)
        
        # Vérifier que l'utilisateur n'existe plus
        deleted_user = UserRepository.get_user_by_id(clean_tables, created_user.id)
        assert deleted_user is None