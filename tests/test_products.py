import pytest
from unittest.mock import Mock, MagicMock
from database.schema.products import Product, ProductCreate, ProductUpdate, ProductResponse, ProductRepository
from datetime import datetime


class TestProductModel:
    def test_product_from_dict(self):
        data = {
            "name": "iPhone 15",
            "brand": "Apple",
            "description": "Latest iPhone model",
            "price": 999.99,
            "reference": "IPHONE15-128",
            "specifications": {"storage": "128GB", "color": "Blue"},
            "supplier_id": 1,
            "order_id": 1,
            "stock_site_id": 1
        }
        product = Product.from_dict(data)
        assert product.name == "iPhone 15"
        assert product.brand == "Apple"
        assert product.description == "Latest iPhone model"
        assert product.price == 999.99
        assert product.reference == "IPHONE15-128"
        assert product.specifications == {"storage": "128GB", "color": "Blue"}
        assert product.supplier_id == 1
        assert product.order_id == 1
        assert product.stock_site_id == 1

    def test_product_from_dict_minimal(self):
        data = {
            "name": "Basic Product",
            "price": 10.0
        }
        product = Product.from_dict(data)
        assert product.name == "Basic Product"
        assert product.price == 10.0

    def test_product_from_dict_with_invalid_field(self):
        data = {
            "name": "Test Product",
            "price": 50.0,
            "invalid_field": "should be ignored"
        }
        product = Product.from_dict(data)
        assert product.name == "Test Product"
        assert product.price == 50.0
        assert not hasattr(product, "invalid_field")


class TestProductSchemas:
    def test_product_create_complete_data(self):
        data = {
            "name": "MacBook Pro",
            "brand": "Apple",
            "description": "Professional laptop",
            "price": 2499.99,
            "reference": "MBP-16-M3",
            "specifications": {"cpu": "M3 Max", "ram": "32GB"},
            "supplier_id": 1,
            "order_id": 2,
            "stock_site_id": 1
        }
        product_create = ProductCreate(**data)
        assert product_create.name == "MacBook Pro"
        assert product_create.brand == "Apple"
        assert product_create.description == "Professional laptop"
        assert product_create.price == 2499.99
        assert product_create.reference == "MBP-16-M3"
        assert product_create.specifications == {"cpu": "M3 Max", "ram": "32GB"}
        assert product_create.supplier_id == 1
        assert product_create.order_id == 2
        assert product_create.stock_site_id == 1

    def test_product_create_minimal_data(self):
        data = {
            "name": "Simple Product",
            "price": 29.99
        }
        product_create = ProductCreate(**data)
        assert product_create.name == "Simple Product"
        assert product_create.price == 29.99
        assert product_create.brand is None
        assert product_create.description is None

    def test_product_create_missing_required_fields(self):
        with pytest.raises(ValueError):
            ProductCreate(brand="Apple")
        
        with pytest.raises(ValueError):
            ProductCreate(name="Test Product")

    def test_product_update_partial_data(self):
        data = {
            "name": "Updated Product Name",
            "price": 199.99
        }
        product_update = ProductUpdate(**data)
        assert product_update.name == "Updated Product Name"
        assert product_update.price == 199.99
        assert product_update.brand is None
        assert product_update.description is None

    def test_product_response_complete_data(self):
        data = {
            "id": 1,
            "name": "Test Product",
            "brand": "Test Brand",
            "description": "Test Description",
            "price": 99.99,
            "reference": "TEST-001",
            "specifications": {"feature": "value"},
            "supplier_id": 1,
            "order_id": 1,
            "stock_site_id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        product_response = ProductResponse(**data)
        assert product_response.id == 1
        assert product_response.name == "Test Product"
        assert product_response.brand == "Test Brand"
        assert product_response.price == 99.99


class TestProductRepository:
    def test_create_product_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        product_data = ProductCreate(
            name="Test Product",
            price=49.99,
            brand="Test Brand"
        )

        with pytest.patch.object(ProductRepository, 'get_product_by_id') as mock_get:
            mock_get.return_value = ProductResponse(
                id=1,
                name="Test Product",
                price=49.99,
                brand="Test Brand",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            result = ProductRepository.create_product(mock_connection, product_data)
            
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
            assert result is not None
            assert result.id == 1

    def test_create_product_empty_data(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        product_data = Mock()
        product_data.model_dump.return_value = {}

        result = ProductRepository.create_product(mock_connection, product_data)
        assert result is None

    def test_create_product_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        product_data = ProductCreate(
            name="Test Product",
            price=49.99
        )

        result = ProductRepository.create_product(mock_connection, product_data)
        
        mock_connection.rollback.assert_called_once()
        assert result is None

    def test_get_all_products_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "name": "Product 1",
                "brand": "Brand 1",
                "description": "Description 1",
                "price": 99.99,
                "reference": "PROD-001",
                "specifications": {"feature": "value1"},
                "supplier_id": 1,
                "order_id": 1,
                "stock_site_id": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 2,
                "name": "Product 2",
                "brand": "Brand 2", 
                "description": "Description 2",
                "price": 149.99,
                "reference": "PROD-002",
                "specifications": {"feature": "value2"},
                "supplier_id": 2,
                "order_id": 2,
                "stock_site_id": 2,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]

        result = ProductRepository.get_all_products(mock_connection)
        
        assert len(result) == 2
        assert all(isinstance(product, ProductResponse) for product in result)
        assert result[0].name == "Product 1"
        assert result[1].name == "Product 2"

    def test_get_all_products_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = ProductRepository.get_all_products(mock_connection)
        
        assert result == []

    def test_get_product_by_id_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "name": "Test Product",
            "brand": "Test Brand",
            "description": "Test Description",
            "price": 99.99,
            "reference": "TEST-001",
            "specifications": {"feature": "value"},
            "supplier_id": 1,
            "order_id": 1,
            "stock_site_id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = ProductRepository.get_product_by_id(mock_connection, 1)
        
        assert result is not None
        assert isinstance(result, ProductResponse)
        assert result.id == 1
        assert result.name == "Test Product"

    def test_get_product_by_id_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = ProductRepository.get_product_by_id(mock_connection, 999)
        
        assert result is None

    def test_update_product_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        product_data = ProductCreate(name="Updated Product", price=199.99)

        result = ProductRepository.update_product(mock_connection, product_data, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        assert result is True

    def test_update_product_no_changes(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        product_data = Mock()
        product_data.model_dump.return_value = {}

        result = ProductRepository.update_product(mock_connection, product_data, 1)
        
        assert result is False

    def test_update_product_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        product_data = ProductCreate(name="Updated Product", price=199.99)

        result = ProductRepository.update_product(mock_connection, product_data, 999)
        
        assert result is False

    def test_update_product_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        product_data = ProductCreate(name="Updated Product", price=199.99)

        result = ProductRepository.update_product(mock_connection, product_data, 1)
        
        mock_connection.rollback.assert_called_once()
        assert result is False

    def test_delete_product_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = ProductRepository.delete_product(mock_connection, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_product_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        result = ProductRepository.delete_product(mock_connection, 999)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_product_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = ProductRepository.delete_product(mock_connection, 1)
        
        assert result is None

    def test_product_with_json_specifications(self):
        product_data = ProductCreate(
            name="Complex Product",
            price=299.99,
            specifications={"cpu": "Intel i7", "ram": "16GB", "storage": {"type": "SSD", "size": "512GB"}}
        )
        
        assert product_data.specifications["cpu"] == "Intel i7"
        assert product_data.specifications["storage"]["type"] == "SSD"