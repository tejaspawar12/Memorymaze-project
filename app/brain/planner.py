# app/brain/planner.py
from app.llm.client import query_llm
from app.embedding.embedder import Embedder
from app.db.neo4j_driver import neo4j_driver
from datetime import datetime
import uuid
import re

class PlannerAgent:
    def __init__(self, llm: query_llm, embedder: Embedder):
        self.llm = llm
        self.embedder = embedder

    def generate_and_store_plan(self, user_id: str, user_input: str) -> list:
        """
        Accepts a user request, generates a structured plan using LLM,
        stores it in Neo4j and Qdrant, and returns the steps.
        """
        plan_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # 🧠 1. Generate plan with LLM
        prompt = f"""
You are a high-level reasoning agent. Break down the user's request into 3–7 structured steps.

User Request:
\"{user_input}\"

Respond only in this format:
Step 1: ...
Step 2: ...
Step 3: ...
"""
        raw_output = self.llm(prompt)
        steps = self._parse_plan(raw_output)

        # 📅 2. Extract day from input (optional)
        day = self._extract_day_from_input(user_input)

        # 💾 3. Store in Neo4j
        self._store_in_neo4j(user_id, plan_id, steps, timestamp, day)

        # 📦 4. Store in Qdrant
        self._store_in_qdrant(user_id, plan_id, user_input, steps, timestamp)

        return steps

    def _parse_plan(self, text: str) -> list:
        """
        Extracts 'Step N: ...' lines from LLM output.
        """
        lines = text.split("\n")
        return [line.strip() for line in lines if line.lower().startswith("step")]

    def _extract_day_from_input(self, text: str) -> str | None:
        """
        Optionally extract a day like 'Monday' or 'tomorrow' from user input.
        """
        day_keywords = [
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "today", "tomorrow"
        ]
        matches = re.findall(r"\b(" + "|".join(day_keywords) + r")\b", text.lower())
        return matches[0].capitalize() if matches else None

    def _store_in_neo4j(self, user_id, plan_id, steps, timestamp, day=None):
        query = """
        MERGE (u:User {id: $user_id})
        CREATE (p:Plan {
            id: $plan_id,
            steps: $steps,
            created_at: $timestamp,
            day: $day
        })
        MERGE (u)-[:PLANNED]->(p)
        """
        parameters = {
            "user_id": user_id,
            "plan_id": plan_id,
            "steps": steps,
            "timestamp": timestamp,
            "day": day
        }
        neo4j_driver.execute_write(query, parameters)

    def _store_in_qdrant(self, user_id, plan_id, user_input, steps, timestamp):
        full_text = f"Plan generated on {timestamp} for '{user_input}':\n" + "\n".join(steps)
        embedding = self.embedder.get_embedding(full_text)

        metadata = {
            "user_id": user_id,
            "plan_id": plan_id,
            "type": "plan",
            "timestamp": timestamp,
            "input": user_input
        }

        self.embedder.upsert_point(user_id, plan_id, embedding, metadata)
