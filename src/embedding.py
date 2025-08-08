import numpy as np
from sentence_transformers import SentenceTransformer
from tidb_vector.integrations import TiDBVectorClient


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer("msmarco-MiniLM-L12-cos-v5")

    def encode_str(self, sentences: str) -> np.ndarray:
        """(3, 384)"""
        if not sentences:
            return np.array([]).reshape(0, 384)
        embeddings = self.model.encode(sentences)
        return embeddings

    def encode_list(self, sentences: list[str]) -> np.ndarray:
        """(3, 384)"""
        if not sentences:
            return np.array([]).reshape(0, 384)
        embeddings = self.model.encode(sentences)
        return embeddings

    def run(self, places: list) -> np.ndarray:
        texts = []
        for p in places:
            toEncode = self.flatten_place(p)
            embedding = self.encode_list(toEncode)
            t = (
                p[0],
                p[1],
                p[2],
                p[3],
                p[4],
                p[5],
                p[6],
                p[7],
                p[8],
                p[9],
                embedding.tolist(),
            )
            texts.append(t)
            # print(t)
            # print("=======================================")
        return texts

    def flatten_place(self, place) -> str:
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
        ) = place
        reviews_text = " ".join([r["comment"] for r in reviews])
        all_text = f"""
        Name: {name}
        Description: {description}
        Category: {category}
        Rating: {rating}
        Reviews: {reviews_text}
        """
        txtToEncode = all_text.strip()
        return txtToEncode
