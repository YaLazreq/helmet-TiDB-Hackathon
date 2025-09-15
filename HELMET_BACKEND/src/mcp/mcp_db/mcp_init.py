from fastmcp import FastMCP
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    mcp = FastMCP("db-server")
except Exception as e:
    raise RuntimeError(f"Failed to initialize FastMCP: {str(e)}")


def create_db_connection():
    """Create a new database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("TIDB_HOST"),
            port=int(os.getenv("TIDB_PORT", 4000)),
            user=os.getenv("TIDB_USER"),
            password=os.getenv("TIDB_PASSWORD"),
            database=os.getenv("TIDB_DATABASE"),
            ssl_disabled=False,
            autocommit=True,
        )
        print("✅ TiDB connection OK")
        return connection
    except Exception as e:
        print(f"❌ TiDB connection error: {e}")
        return None


def get_db_connection():
    """Get database connection with reconnection if needed"""
    global db
    if db is None or not db.is_connected():
        print("🔄 Reconnecting to database...")
        db = create_db_connection()
    return db


# Initial connection
db = create_db_connection()

# Export
__all__ = [
    "mcp",
    "db",
    "get_db_connection",
]
