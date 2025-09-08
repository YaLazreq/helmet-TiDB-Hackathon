from langchain_community.utilities import SQLDatabase
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Singleton pattern - connexion partagée
_db_connection = None


def create_database_connection():
    global _db_connection

    # Si connexion déjà créée, la retourner
    if _db_connection is not None:
        return _db_connection

    host = os.getenv("TIDB_HOST")
    port = int(os.getenv("TIDB_PORT", 4000))
    user = os.getenv("TIDB_USER")
    password = os.getenv("TIDB_PASSWORD")
    database = os.getenv("TIDB_DATABASE")
    ssl_ca = os.getenv("TIDB_SSL_CA", "./ca_tidb.pem")

    password_encoded = quote_plus(password)

    connection_string = (
        f"mysql+pymysql://{user}:{password_encoded}@{host}:{port}/{database}"
    )

    engine = create_engine(
        connection_string,
        connect_args={
            "ssl": {
                "ssl_ca": ssl_ca,
                "ssl_disabled": False,
                "ssl_verify_cert": True,
                "ssl_verify_identity": False,
            }
        },
        echo=False,
    )

    try:
        with engine.connect() as conn:
            # Connexion testée avec succès (message supprimé pour éviter le spam)
            pass
    except Exception as e:
        print(f"❌ Erreur de connexion SQLAlchemy: {e}")
        raise

    db = SQLDatabase(engine)

    # Sauvegarder la connexion pour réutilisation
    _db_connection = db

    return db


# def get_table_schema():
#     """
#     Get table schema using MCP database tools
#     """
#     try:
#         # Import requests to call MCP server
#         import requests
#         import os

#         # Get MCP server port from environment (default 8080)
#         mcp_port = os.getenv("MCP_PORT", "8080")
#         mcp_url = f"http://localhost:{mcp_port}"

#         # Call the MCP get_table_schemas tool
#         response = requests.post(
#             f"{mcp_url}/call_tool",
#             json={
#                 "name": "get_table_schemas",
#                 "arguments": {}
#             },
#             timeout=10
#         )

#         if response.status_code == 200:
#             result = response.json()
#             return result.get("content", [{}])[0].get("text", "No schema found")
#         else:
#             return f"MCP server error: {response.status_code}"

#     except Exception as e:
#         # Fallback to simple schema if MCP server is not available
#         return """    - users:
#         id int pk auto_increment
#         first_name varchar(100)
#         last_name varchar(100)
#         email varchar(255)
#         role enum('worker','team_leader','supervisor','site_manager')
#     - tasks:
#         id int pk auto_increment
#         title varchar(255)
#         description text
#         status enum('pending','in_progress','completed','blocked')"""

# # Use the dynamic function to get the schema
# table_schema = get_table_schema()
