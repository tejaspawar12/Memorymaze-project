# app/brain/milestone_agent.py

from app.llm.client import query_llm
from app.memory.qdrant_client import insert_memory
from datetime import datetime
import uuid

class MilestoneAgent:
    def __init__(self, llm: query_llm):
        self.llm = llm

    def extract_milestones(self, user_id: str, full_plan_text: str) -> list:
        """
        Uses the LLM to extract 3–6 major milestones from the full plan.
        """
        prompt = f"""
        You are a goal breakdown assistant. Extract the 4–6 major milestones from the following learning plan:

        Plan:
        {full_plan_text}

        Return each milestone as a bullet point, clearly and concisely.
        """
        response = self.llm(prompt)
        milestones = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]
        return milestones

    def save_milestones(self, user_id: str, milestones: list):
        """
        Saves each milestone as a separate memory point in Qdrant with 'milestone' tag.
        """
        for milestone in milestones:
            insert_memory(
                user_id=user_id,
                text=milestone,
                vector=self.llm.get_embedding(milestone),
                role="milestone_agent",
                tags=["milestone"],
                timestamp=datetime.utcnow().isoformat()
            )
        return f"✅ Saved {len(milestones)} milestones for {user_id}"
