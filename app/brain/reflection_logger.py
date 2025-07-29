# app/brain/reflection_logger.py

from datetime import datetime
from app.embedding.embedder import Embedder
from app.llm.client import query_llm
from app.memory.qdrant_client import insert_memory

class ReflectionLogger:
    def __init__(self, llm: callable, embedder: Embedder):
        self.llm = llm
        self.embedder = embedder

    def log_reflection(self, user_id: str, reflection_text: str) -> str:
        """
        Saves the user's daily/weekly reflections in Qdrant with 'reflection' tag.
        """
        embedding = self.embedder.get_embedding(reflection_text)

        insert_memory(
            user_id=user_id,
            text=reflection_text,
            vector=embedding,
            role="reflection_logger",
            tags=["reflection"],
            timestamp=datetime.utcnow().isoformat()
        )
        return f"📝 Reflection logged for user: {user_id}"

    def summarize_reflections(self, user_id: str, recent_reflections: list) -> str:
        """
        Takes in recent reflections and returns a summary insight.
        (Useful for MetaLearner or weekly review.)
        """
        combined = "\n".join(recent_reflections)
        prompt = f"""
        Analyze the following reflections and generate a short summary of the user's progress, mindset, and any emotional or motivational patterns:

        Reflections:
        {combined}
        """
        return self.llm(prompt)
