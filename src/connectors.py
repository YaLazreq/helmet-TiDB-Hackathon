import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

import json
import sys

sys.path.append("../src")  # Adjust the path as necessary to import from src
from src.config import Config
from src.embedding import Embedder


def get_connection(autocommit: bool = True) -> MySQLConnection:
    config = Config()
    db_conf = {
        "host": config.tidb_host,
        "port": config.tidb_port,
        "user": config.tidb_user,
        "password": config.tidb_password,
        "database": config.tidb_db_name,
        "autocommit": autocommit,
        # mysql-connector-python will use C extension by default,
        # to make this example work on all platforms more easily,
        # we choose to use pure python implementation.
        "use_pure": True,
    }

    if config.ca_path:
        db_conf["ssl_verify_cert"] = True
        db_conf["ssl_verify_identity"] = True
        db_conf["ssl_ca"] = config.ca_path
    return mysql.connector.connect(**db_conf)


def create_tables() -> None:
    with get_connection(autocommit=False) as connection:
        with connection.cursor() as cur:
            # 1) Création de la table avec embedding VECTOR
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS places (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    address JSON,
                    description TEXT,
                    category VARCHAR(255),
                    currency VARCHAR(10),
                    link VARCHAR(2048),
                    reviews JSON,
                    nbr_review INT,
                    price DECIMAL(13, 3),
                    rating DECIMAL(5, 2),
                    embedding VECTOR(384) NOT NULL
                )
            """
            )
            # add replica TiFlash
            # cur.execute("ALTER TABLE places SET TIFLASH REPLICA 1")
            # ## Créer index vectoriel
            # cur.execute(
            #     """
            # CREATE VECTOR INDEX idx_embedding_vector
            # ON places ((VEC_L2_DISTANCE(embedding)))
            # USING HNSW
            # """
            # )
        # Validation
        connection.commit()


def create_places(cursor: MySQLCursor, places: list) -> None:
    params = []
    for p in places:
        (
            name,
            description,
            address,
            category,
            currency,
            price,
            rating,
            nbr_review,
            link,
            reviews,
            embedding,
        ) = p

        # JSON-serialize the dict/list fields
        address_json = json.dumps(address)
        reviews_json = json.dumps(reviews)
        embedding_json = json.dumps(embedding)

        params.append(
            (
                name,
                description,
                address_json,
                category,
                currency,
                price,
                rating,
                nbr_review,
                link,
                reviews_json,
                embedding_json,
            )
        )

    sql = """
        INSERT INTO places
          (name, description, address, category, currency,
           price, rating, nbr_review, link, reviews, embedding)
        VALUES
          (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.executemany(sql, params)


def semantic_search(cursor: MySQLCursor, query: str, top_k: int = 3):
    # 1) Génération de l'embedding
    embedding = Embedder().encode_str(query)  # 1D array
    embedding_json = json.dumps(embedding.tolist())

    # 2) Requête vectorielle L2_DISTANCE
    sql = f"""
        SELECT
            id,
            name,
            category,
            description,
            VEC_COSINE_DISTANCE(embedding, %s) AS distance
        FROM places
        ORDER BY distance
        LIMIT %s
    """
    cursor.execute(sql, (embedding_json, top_k))
    results = cursor.fetchall()

    # 3) Affichage
    print("Search results:")
    for row in results:
        print(f"ID:{row['id']}  Name:{row['name']}  Distance:{row['distance']}")

    return results
