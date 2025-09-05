from fastmcp import FastMCP
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    mcp = FastMCP("api-server")
except Exception as e:
    raise RuntimeError(f"Failed to initialize FastMCP: {str(e)}")

try:
    db = mysql.connector.connect(
        host=os.getenv('TIDB_HOST'),
        port=int(os.getenv('TIDB_PORT', 4000)),
        user=os.getenv('TIDB_USER'),
        password=os.getenv('TIDB_PASSWORD'),
        database=os.getenv('TIDB_DATABASE'),
        ssl_disabled=False,
        ssl_ca=os.getenv('TIDB_SSL_CA', './ca_tidb.pem'),
        autocommit=True
    )
    print("Connexion TiDB OK")
except Exception as e:
    print(f"Erreur connexion TiDB : {e}")
    db = None

# Export
__all__ = [
    "mcp",
    "db",
]