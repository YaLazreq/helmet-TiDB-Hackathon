"""
Tests unitaires pour la connexion à la base de données
"""

import pytest
import pymysql
from mcp_server import connect_to_tidb
import database.config as config


class TestDatabaseConnection:
    """Tests pour la connexion à la base de données"""

    def test_connection_config_exists(self):
        """Test que la configuration DB existe"""
        assert hasattr(config, "DB_CONFIG")
        assert isinstance(config.DB_CONFIG, dict)
        assert "host" in config.DB_CONFIG
        assert "port" in config.DB_CONFIG
        assert "user" in config.DB_CONFIG

    def test_database_connection_success(self, db_connection):
        """Test que la connexion à la DB fonctionne"""
        assert db_connection is not None
        assert isinstance(db_connection, pymysql.Connection)

    def test_database_ping(self, db_connection):
        """Test que la connexion est active"""
        db_connection.ping(reconnect=True)
        # Si pas d'exception, la connexion est OK

    def test_basic_query(self, db_connection):
        """Test d'une requête SQL basique"""
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_show_tables(self, db_connection):
        """Test pour lister les tables"""
        with db_connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            # Vérifier que nos tables existent
            table_names = [table[0] for table in tables]
            assert "users" in table_names
            assert "tasks" in table_names

    def test_connection_charset(self, db_connection):
        """Test que le charset est correct"""
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT @@character_set_connection")
            charset = cursor.fetchone()[0]
            assert charset in ["utf8mb4", "utf8"]
