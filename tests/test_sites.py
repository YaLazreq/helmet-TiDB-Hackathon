import pytest
from unittest.mock import Mock, MagicMock
from database.schema.sites import Site, SiteCreate, SiteUpdate, SiteResponse, SiteRepository
from datetime import datetime


class TestSiteModel:
    def test_site_from_dict(self):
        data = {
            "name": "Site Principal",
            "location": "Paris, France",
            "created_by": 1
        }
        site = Site.from_dict(data)
        assert site.name == "Site Principal"
        assert site.location == "Paris, France"
        assert site.created_by == 1

    def test_site_from_dict_with_invalid_field(self):
        data = {
            "name": "Site Test",
            "location": "Lyon, France", 
            "created_by": 1,
            "invalid_field": "should be ignored"
        }
        site = Site.from_dict(data)
        assert site.name == "Site Test"
        assert site.location == "Lyon, France"
        assert site.created_by == 1
        assert not hasattr(site, "invalid_field")


class TestSiteSchemas:
    def test_site_create_valid_data(self):
        data = {
            "name": "Entrepôt Nord",
            "location": "Lille, France",
            "created_by": 1
        }
        site_create = SiteCreate(**data)
        assert site_create.name == "Entrepôt Nord"
        assert site_create.location == "Lille, France"
        assert site_create.created_by == 1

    def test_site_create_missing_required_field(self):
        with pytest.raises(ValueError):
            SiteCreate(location="Test Location")

    def test_site_update_partial_data(self):
        data = {"name": "Nouveau Nom"}
        site_update = SiteUpdate(**data)
        assert site_update.name == "Nouveau Nom"
        assert site_update.location is None
        assert site_update.created_by is None

    def test_site_response_complete_data(self):
        data = {
            "id": 1,
            "name": "Site Test",
            "location": "Test Location",
            "created_by": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        site_response = SiteResponse(**data)
        assert site_response.id == 1
        assert site_response.name == "Site Test"
        assert site_response.location == "Test Location"
        assert site_response.created_by == 1


class TestSiteRepository:
    def test_create_site_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        site_data = SiteCreate(
            name="Site Test",
            location="Test Location",
            created_by=1
        )

        with pytest.patch.object(SiteRepository, 'get_site_by_id') as mock_get:
            mock_get.return_value = SiteResponse(
                id=1,
                name="Site Test",
                location="Test Location", 
                created_by=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            result = SiteRepository.create_site(mock_connection, site_data)
            
            mock_cursor.execute.assert_called_once()
            mock_connection.commit.assert_called_once()
            assert result is not None
            assert result.id == 1

    def test_create_site_empty_data(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        site_data = Mock()
        site_data.model_dump.return_value = {}

        result = SiteRepository.create_site(mock_connection, site_data)
        assert result is None

    def test_create_site_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        site_data = SiteCreate(
            name="Site Test",
            location="Test Location",
            created_by=1
        )

        result = SiteRepository.create_site(mock_connection, site_data)
        
        mock_connection.rollback.assert_called_once()
        assert result is None

    def test_get_all_sites_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "name": "Site 1",
                "location": "Location 1",
                "created_by": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": 2,
                "name": "Site 2", 
                "location": "Location 2",
                "created_by": 1,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]

        result = SiteRepository.get_all_sites(mock_connection)
        
        assert len(result) == 2
        assert all(isinstance(site, SiteResponse) for site in result)
        assert result[0].name == "Site 1"
        assert result[1].name == "Site 2"

    def test_get_all_sites_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = SiteRepository.get_all_sites(mock_connection)
        
        assert result == []

    def test_get_site_by_id_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "name": "Site Test",
            "location": "Test Location",
            "created_by": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = SiteRepository.get_site_by_id(mock_connection, 1)
        
        assert result is not None
        assert isinstance(result, SiteResponse)
        assert result.id == 1
        assert result.name == "Site Test"

    def test_get_site_by_id_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = SiteRepository.get_site_by_id(mock_connection, 999)
        
        assert result is None

    def test_update_site_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        site_data = SiteCreate(name="Nouveau Nom")

        result = SiteRepository.update_site(mock_connection, site_data, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        assert result is True

    def test_update_site_no_changes(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        site_data = Mock()
        site_data.model_dump.return_value = {}

        result = SiteRepository.update_site(mock_connection, site_data, 1)
        
        assert result is False

    def test_update_site_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        site_data = SiteCreate(name="Nouveau Nom")

        result = SiteRepository.update_site(mock_connection, site_data, 999)
        
        assert result is False

    def test_delete_site_success(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = SiteRepository.delete_site(mock_connection, 1)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_site_not_found(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        result = SiteRepository.delete_site(mock_connection, 999)
        
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    def test_delete_site_database_error(self):
        mock_connection = Mock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = SiteRepository.delete_site(mock_connection, 1)
        
        assert result is None