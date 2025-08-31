import pytest
from unittest.mock import Mock, MagicMock
from database.schema.orders import Order, OrderCreate, OrderUpdate, OrderResponse, OrderRepository
from src.models.enums.enums import OrderStatus
from datetime import datetime


class TestOrderModel:
    def test_order_from_dict(self):
        data = {
            "nbr_items": 5,
            "status": OrderStatus.PENDING.value,
            "invoice_url": "https://example.com/invoice.pdf",
            "supplier_id": 1,
            "description": "Commande de fournitures bureau",
            "price": 250.50,
            "created_by": 1
        }
        order = Order.from_dict(data)
        assert order.nbr_items == 5
        assert order.status == OrderStatus.PENDING.value
        assert order.invoice_url == "https://example.com/invoice.pdf"
        assert order.supplier_id == 1
        assert order.description == "Commande de fournitures bureau"
        assert order.price == 250.50
        assert order.created_by == 1

    def test_order_from_dict_minimal(self):
        data = {
            "description": "Commande simple",
            "supplier_id": 1
        }
        order = Order.from_dict(data)
        assert order.description == "Commande simple"
        assert order.supplier_id == 1

    def test_order_from_dict_with_invalid_field(self):
        data = {
            "description": "Test Order",
            "supplier_id": 1,
            "invalid_field": "should be ignored"
        }
        order = Order.from_dict(data)
        assert order.description == "Test Order"
        assert order.supplier_id == 1
        assert not hasattr(order, "invalid_field")


class TestOrderSchemas:
    def test_order_create_complete_data(self):
        data = {
            "nbr_items": 10,
            "status": OrderStatus.CONFIRMED.value,
            "invoice_url": "https://example.com/invoice123.pdf",
            "supplier_id": 2,
            "description": "Commande matériel informatique",
            "price": 1500.00,
            "created_by": 1
        }
        order_create = OrderCreate(**data)
        assert order_create.nbr_items == 10
        assert order_create.status == OrderStatus.CONFIRMED.value
        assert order_create.invoice_url == "https://example.com/invoice123.pdf"
        assert order_create.supplier_id == 2
        assert order_create.description == "Commande matériel informatique"
        assert order_create.price == 1500.00
        assert order_create.created_by == 1

    def test_order_create_with_defaults(self):
        data = {}
        order_create = OrderCreate(**data)
        assert order_create.nbr_items == 0
        assert order_create.status == OrderStatus.PENDING.value
        assert order_create.invoice_url == ""
        assert order_create.supplier_id is None
        assert order_create.description == ""
        assert order_create.price == 0.0
        assert order_create.created_by is None

    def test_order_create_partial_data(self):
        data = {
            "description": "Commande urgente",
            "supplier_id": 3,
            "price": 750.25
        }
        order_create = OrderCreate(**data)
        assert order_create.description == "Commande urgente"
        assert order_create.supplier_id == 3
        assert order_create.price == 750.25
        assert order_create.nbr_items == 0  # default
        assert order_create.status == OrderStatus.PENDING.value  # default

    def test_order_update_partial_data(self):
        data = {
            "status": OrderStatus.DELIVERED.value,
            "price": 999.99
        }
        order_update = OrderUpdate(**data)
        assert order_update.status == OrderStatus.DELIVERED.value
        assert order_update.price == 999.99
        assert order_update.nbr_items is None
        assert order_update.description is None

    def test_order_response_complete_data(self):
        data = {
            "id": 1,
            "nbr_items": 5,
            "status": OrderStatus.PENDING.value,
            "invoice_url": "https://example.com/invoice.pdf",
            "supplier_id": 1,
            "description": "Test Order",
            "price": 100.00,
            "created_by": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        order_response = OrderResponse(**data)
        assert order_response.id == 1
        assert order_response.nbr_items == 5
        assert order_response.status == OrderStatus.PENDING.value
        assert order_response.description == "Test Order"
        assert order_response.price == 100.00


class TestOrderRepository:
    def test_create_order_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        order_data = OrderCreate(
            description="Test Order",
            supplier_id=1,
            price=150.00,
            created_by=1
        )

        with pytest.patch.object(OrderRepository, 'get_order_by_id') as mock_get:
            mock_get.return_value = OrderResponse(
                id=1,
                description="Test Order",
                supplier_id=1,
                price=150.00,
                created_by=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            result = OrderRepository.create_order(mock_connection, order_data)
            
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
            assert result is not None
            assert result.id == 1

    def test_create_order_empty_data(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        order_data = Mock()
        order_data.model_dump.return_value = {}

        result = OrderRepository.create_order(mock_connection, order_data)
        assert result is None

    def test_create_order_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        order_data = OrderCreate(
            description="Test Order",
            supplier_id=1,
            price=150.00
        )

        result = OrderRepository.create_order(mock_connection, order_data)
        
        mock_connection.rollback.assert_called_once()
        assert result is None

    def test_get_all_orders_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "nbr_items": 5,
                "status": OrderStatus.PENDING.value,
                "invoice_url": "https://example.com/invoice1.pdf",
                "supplier_id": 1,
                "description": "Order 1",
                "price": 100.00,
                "created_by": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 2,
                "nbr_items": 3,
                "status": OrderStatus.CONFIRMED.value,
                "invoice_url": "https://example.com/invoice2.pdf",
                "supplier_id": 2,
                "description": "Order 2",
                "price": 200.00,
                "created_by": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]

        result = OrderRepository.get_all_orders(mock_connection)
        
        assert len(result) == 2
        assert all(isinstance(order, OrderResponse) for order in result)
        assert result[0].description == "Order 1"
        assert result[1].description == "Order 2"

    def test_get_all_orders_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = OrderRepository.get_all_orders(mock_connection)
        
        assert result == []

    def test_get_order_by_id_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "nbr_items": 5,
            "status": OrderStatus.PENDING.value,
            "invoice_url": "https://example.com/invoice.pdf",
            "supplier_id": 1,
            "description": "Test Order",
            "price": 150.00,
            "created_by": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = OrderRepository.get_order_by_id(mock_connection, 1)
        
        assert result is not None
        assert isinstance(result, OrderResponse)
        assert result.id == 1
        assert result.description == "Test Order"

    def test_get_order_by_id_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = OrderRepository.get_order_by_id(mock_connection, 999)
        
        assert result is None

    def test_update_order_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        order_data = OrderCreate(
            status=OrderStatus.DELIVERED.value,
            price=250.00
        )

        result = OrderRepository.update_order(mock_connection, order_data, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        assert result is True

    def test_update_order_no_changes(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        order_data = Mock()
        order_data.model_dump.return_value = {}

        result = OrderRepository.update_order(mock_connection, order_data, 1)
        
        assert result is False

    def test_update_order_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        order_data = OrderCreate(status=OrderStatus.CANCELLED.value)

        result = OrderRepository.update_order(mock_connection, order_data, 999)
        
        assert result is False

    def test_update_order_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        order_data = OrderCreate(status=OrderStatus.DELIVERED.value)

        result = OrderRepository.update_order(mock_connection, order_data, 1)
        
        mock_connection.rollback.assert_called_once()
        assert result is False

    def test_delete_order_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = OrderRepository.delete_order(mock_connection, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_order_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        result = OrderRepository.delete_order(mock_connection, 999)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_order_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = OrderRepository.delete_order(mock_connection, 1)
        
        assert result is None

    def test_order_status_enum_values(self):
        order_data = OrderCreate(
            description="Test Order",
            status=OrderStatus.PENDING.value
        )
        assert order_data.status == "pending"
        
        order_data.status = OrderStatus.CONFIRMED.value
        assert order_data.status == "confirmed"
        
        order_data.status = OrderStatus.DELIVERED.value
        assert order_data.status == "delivered"

    def test_order_with_large_description(self):
        large_description = "A" * 1000  # 1000 characters
        order_data = OrderCreate(
            description=large_description,
            supplier_id=1
        )
        assert len(order_data.description) == 1000
        assert order_data.description == large_description