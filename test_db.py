#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()


def test_db_connection():
    """Test database connection and show schema"""

    # Get connection details
    host = os.getenv("TIDB_HOST")
    port = int(os.getenv("TIDB_PORT", 4000))
    user = os.getenv("TIDB_USER")
    password = os.getenv("TIDB_PASSWORD")
    database = os.getenv("TIDB_DATABASE")
    ssl_ca = os.getenv("TIDB_SSL_CA", "./ca_tidb.pem")

    print("🔍 Testing TiDB Connection...")
    print(f"Host: {host}:{port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print("-" * 50)

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
            print("✅ Connection successful!")

            # Show all tables
            print("\n📋 Available tables:")
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()

            if tables:
                for table in tables:
                    print(f"  - {table[0]}")

                # Show schema for first table
                if tables:
                    table_name = tables[0][0]
                    print(f"\n🏗️  Schema for table '{table_name}':")
                    result = conn.execute(text(f"DESCRIBE {table_name}"))
                    columns = result.fetchall()
                    for col in columns:
                        print(f"  - {col[0]} ({col[1]})")
            else:
                print("  No tables found in database")

    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    test_db_connection()
