# app/brain/executor_agent.py

from app.llm.client import query_llm
from app.embedding.embedder import Embedder
from app.db.neo4j_driver import neo4j_driver
from datetime import datetime

class ExecutorAgent:
    def __init__(self, llm, embedder: Embedder):
        self.llm = llm
        self.embedder = embedder

    def get_current_step(self, user_id: str):
        query = """
        MATCH (u:User {id: $user_id})-[:PLANNED]->(p:Plan)-[:HAS_STEP]->(s:Step)
        WHERE s.status <> 'done'
        RETURN s ORDER BY s.index ASC LIMIT 1
        """
        result = neo4j_driver.execute_read(query, {"user_id": user_id})
        return result[0] if result else None

    def guide_step(self, step_text: str) -> str:
        prompt = f"""
You are an execution coach. Help the user understand and take action on this step:

Step: "{step_text}"

Break it into mini-steps if possible and give concise advice.
"""
        return self.llm(prompt)

    def mark_step_done(self, user_id: str, step_id: str, step_text: str):
        timestamp = datetime.now().isoformat()

        # ✅ Update Neo4j
        update_query = """
        MATCH (s:Step {id: $step_id})
        SET s.status = 'done', s.completed_at = $timestamp
        """
        neo4j_driver.execute_write(update_query, {"step_id": step_id, "timestamp": timestamp})

        # 🧠 Save in Qdrant
        vector = self.embedder.get_embedding(step_text)
        self.embedder.upsert_point(
            user_id=user_id,
            point_id=step_id,
            vector=vector,
            payload={
                "text": step_text,
                "timestamp": timestamp,
                "type": "step_done"
            }
        )

    def execute_next(self, user_id: str):
        step = self.get_current_step(user_id)
        if not step:
            return "🎉 All steps completed! Great job."

        step_text = step['s']['text']
        step_id = step['s']['id']

        explanation = self.guide_step(step_text)

        return {
            "step_id": step_id,
            "step_text": step_text,
            "guidance": explanation
        }
