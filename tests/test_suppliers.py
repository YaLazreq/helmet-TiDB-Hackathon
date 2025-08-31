import pytest
from unittest.mock import Mock, MagicMock
from database.schema.suppliers import Supplier, SupplierCreate, SupplierUpdate, SupplierResponse, SupplierRepository
from datetime import datetime


class TestSupplierModel:
    def test_supplier_from_dict(self):
        data = {
            "name": "TechSupply Corp",
            "address": "123 Tech Street, Paris 75001",
            "phone": "+33 1 23 45 67 89",
            "email": "contact@techsupply.com",
            "type": "Informatique"
        }
        supplier = Supplier.from_dict(data)
        assert supplier.name == "TechSupply Corp"
        assert supplier.address == "123 Tech Street, Paris 75001"
        assert supplier.phone == "+33 1 23 45 67 89"
        assert supplier.email == "contact@techsupply.com"
        assert supplier.type == "Informatique"

    def test_supplier_from_dict_minimal(self):
        data = {
            "name": "Simple Supplier"
        }
        supplier = Supplier.from_dict(data)
        assert supplier.name == "Simple Supplier"

    def test_supplier_from_dict_with_invalid_field(self):
        data = {
            "name": "Test Supplier",
            "address": "Test Address",
            "invalid_field": "should be ignored"
        }
        supplier = Supplier.from_dict(data)
        assert supplier.name == "Test Supplier"
        assert supplier.address == "Test Address"
        assert not hasattr(supplier, "invalid_field")


class TestSupplierSchemas:
    def test_supplier_create_complete_data(self):
        data = {
            "name": "Global Office Supplies",
            "address": "456 Business Avenue, Lyon 69000",
            "phone": "+33 4 78 90 12 34",
            "email": "orders@globalsupplies.fr",
            "type": "Fournitures Bureau"
        }
        supplier_create = SupplierCreate(**data)
        assert supplier_create.name == "Global Office Supplies"
        assert supplier_create.address == "456 Business Avenue, Lyon 69000"
        assert supplier_create.phone == "+33 4 78 90 12 34"
        assert supplier_create.email == "orders@globalsupplies.fr"
        assert supplier_create.type == "Fournitures Bureau"

    def test_supplier_create_minimal_data(self):
        data = {
            "name": "Minimal Supplier"
        }
        supplier_create = SupplierCreate(**data)
        assert supplier_create.name == "Minimal Supplier"
        assert supplier_create.address is None
        assert supplier_create.phone is None
        assert supplier_create.email is None
        assert supplier_create.type is None

    def test_supplier_create_missing_required_field(self):
        with pytest.raises(ValueError):
            SupplierCreate(address="Some Address")

    def test_supplier_update_partial_data(self):
        data = {
            "phone": "+33 1 11 22 33 44",
            "email": "new-contact@supplier.com"
        }
        supplier_update = SupplierUpdate(**data)
        assert supplier_update.phone == "+33 1 11 22 33 44"
        assert supplier_update.email == "new-contact@supplier.com"
        assert supplier_update.name is None
        assert supplier_update.address is None
        assert supplier_update.type is None

    def test_supplier_response_complete_data(self):
        data = {
            "id": 1,
            "name": "Test Supplier",
            "address": "Test Address",
            "phone": "+33 1 00 00 00 00",
            "email": "test@supplier.com",
            "type": "Test Type",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        supplier_response = SupplierResponse(**data)
        assert supplier_response.id == 1
        assert supplier_response.name == "Test Supplier"
        assert supplier_response.address == "Test Address"
        assert supplier_response.phone == "+33 1 00 00 00 00"
        assert supplier_response.email == "test@supplier.com"
        assert supplier_response.type == "Test Type"


class TestSupplierRepository:
    def test_create_supplier_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        supplier_data = SupplierCreate(
            name="Test Supplier",
            address="Test Address",
            phone="+33 1 00 00 00 00",
            email="test@supplier.com",
            type="Test Type"
        )

        with pytest.patch.object(SupplierRepository, 'get_supplier_by_id') as mock_get:
            mock_get.return_value = SupplierResponse(
                id=1,
                name="Test Supplier",
                address="Test Address",
                phone="+33 1 00 00 00 00",
                email="test@supplier.com",
                type="Test Type",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            result = SupplierRepository.create_supplier(mock_connection, supplier_data)
            
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
            assert result is not None
            assert result.id == 1

    def test_create_supplier_minimal_data(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        supplier_data = SupplierCreate(name="Minimal Supplier")

        with pytest.patch.object(SupplierRepository, 'get_supplier_by_id') as mock_get:
            mock_get.return_value = SupplierResponse(
                id=1,
                name="Minimal Supplier",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            result = SupplierRepository.create_supplier(mock_connection, supplier_data)
            
            assert result is not None
            assert result.name == "Minimal Supplier"

    def test_create_supplier_empty_data(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        supplier_data = Mock()
        supplier_data.model_dump.return_value = {}

        result = SupplierRepository.create_supplier(mock_connection, supplier_data)
        assert result is None

    def test_create_supplier_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        supplier_data = SupplierCreate(name="Test Supplier")

        result = SupplierRepository.create_supplier(mock_connection, supplier_data)
        
        mock_connection.rollback.assert_called_once()
        assert result is None

    def test_get_all_suppliers_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "name": "Supplier 1",
                "address": "Address 1",
                "phone": "+33 1 11 11 11 11",
                "email": "supplier1@example.com",
                "type": "Type 1",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 2,
                "name": "Supplier 2",
                "address": "Address 2",
                "phone": "+33 1 22 22 22 22",
                "email": "supplier2@example.com", 
                "type": "Type 2",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]

        result = SupplierRepository.get_all_suppliers(mock_connection)
        
        assert len(result) == 2
        assert all(isinstance(supplier, SupplierResponse) for supplier in result)
        assert result[0].name == "Supplier 1"
        assert result[1].name == "Supplier 2"

    def test_get_all_suppliers_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = SupplierRepository.get_all_suppliers(mock_connection)
        
        assert result == []

    def test_get_supplier_by_id_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "name": "Test Supplier",
            "address": "Test Address",
            "phone": "+33 1 00 00 00 00",
            "email": "test@supplier.com",
            "type": "Test Type",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = SupplierRepository.get_supplier_by_id(mock_connection, 1)
        
        assert result is not None
        assert isinstance(result, SupplierResponse)
        assert result.id == 1
        assert result.name == "Test Supplier"

    def test_get_supplier_by_id_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = SupplierRepository.get_supplier_by_id(mock_connection, 999)
        
        assert result is None

    def test_update_supplier_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        supplier_data = SupplierCreate(
            name="Updated Supplier",
            email="updated@supplier.com"
        )

        result = SupplierRepository.update_supplier(mock_connection, supplier_data, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        assert result is True

    def test_update_supplier_no_changes(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        supplier_data = Mock()
        supplier_data.model_dump.return_value = {}

        result = SupplierRepository.update_supplier(mock_connection, supplier_data, 1)
        
        assert result is False

    def test_update_supplier_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        supplier_data = SupplierCreate(name="Updated Supplier")

        result = SupplierRepository.update_supplier(mock_connection, supplier_data, 999)
        
        assert result is False

    def test_update_supplier_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        supplier_data = SupplierCreate(name="Updated Supplier")

        result = SupplierRepository.update_supplier(mock_connection, supplier_data, 1)
        
        mock_connection.rollback.assert_called_once()
        assert result is False

    def test_delete_supplier_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = SupplierRepository.delete_supplier(mock_connection, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_supplier_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        result = SupplierRepository.delete_supplier(mock_connection, 999)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_supplier_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = SupplierRepository.delete_supplier(mock_connection, 1)
        
        assert result is None

    def test_supplier_email_validation(self):
        supplier_data = SupplierCreate(
            name="Email Test Supplier",
            email="valid.email+test@domain.co.uk"
        )
        assert supplier_data.email == "valid.email+test@domain.co.uk"

    def test_supplier_phone_formats(self):
        phone_formats = [
            "+33 1 23 45 67 89",
            "01.23.45.67.89", 
            "0123456789",
            "+33123456789"
        ]
        
        for phone in phone_formats:
            supplier_data = SupplierCreate(
                name="Phone Test Supplier",
                phone=phone
            )
            assert supplier_data.phone == phone

    def test_supplier_type_categories(self):
        supplier_types = [
            "Informatique",
            "Fournitures Bureau",
            "Mobilier",
            "Maintenance",
            "Services"
        ]
        
        for supplier_type in supplier_types:
            supplier_data = SupplierCreate(
                name="Type Test Supplier",
                type=supplier_type
            )
            assert supplier_data.type == supplier_type