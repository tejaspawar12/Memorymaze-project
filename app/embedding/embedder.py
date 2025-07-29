# app/embedding/embedder.py

from app.memory.embedding import get_embedding
import app.memory.qdrant_client as qdrant_client  # ✅ Import qdrant utilities

class Embedder:
    def get_embedding(self, text: str) -> list:
        return get_embedding(text)

    def upsert_point(self, user_id: str, point_id: str, vector: list, payload: dict):
        """
        Proxy method to insert into Qdrant.
        """
        qdrant_client.update_memory_by_id(user_id, point_id, vector, payload)
