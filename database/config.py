import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# 1. SIMPLE CONFIGURATION
# =============================================================================
# Connexion config for TiDBhttps://langchain-ai.github.io/langgraph/tutorials/sql/sql-agent/
DB_CONFIG = {
    "host": os.getenv("TIDB_HOST"),
    "port": 4000,
    "user": os.getenv("TIDB_USER", "root"),
    "password": os.getenv("TIDB_PASSWORD", ""),
    "database": os.getenv("TIDB_DATABASE", "test_db"),
    "ssl_disabled": False,  # Force SSL pour TiDB Cloud
    "ssl_verify_cert": True,
    "ssl_verify_identity": True,
}
