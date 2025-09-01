# Connexion TiDB ultra-simple pour débuter
# Juste les concepts de base sans complications

import pymysql
from datetime import datetime
import database.config as config

# from database.schema.users import


# =============================================================================
# 2. FONCTION DE CONNEXION SIMPLE
# =============================================================================


def connect_to_tidb():
    """Se connecter à TiDB - version simple"""
    try:
        connection = pymysql.connect(**config.DB_CONFIG)
        print("✅ Connexion à TiDB réussie !")
        return connection
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return None
