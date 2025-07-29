from app.llm.client import query_llm
from app.memory.qdrant_client import search_memory


class MetaLearner:
    def __init__(self, llm: query_llm):
        self.llm = llm

    def analyze_learning_pattern(self, completed_steps: list, reflections: list) -> str:
        steps_text = "\n".join([f"- {step}" for step in completed_steps])
        reflections_text = "\n".join([f"- {r}" for r in reflections])

        prompt = f"""
        The user has completed the following learning steps:

        {steps_text}

        And has reflected with the following thoughts:

        {reflections_text}

        Based on this, analyze the user's learning style, strengths, bottlenecks, and recommend improvements.
        Also include 1 motivational insight.
        """
        return self.llm.query_llm(prompt)

    def suggest_study_strategy(self, user_goal: str) -> str:
        prompt = f"""
        Based on the goal: '{user_goal}', suggest an ideal learning strategy that fits a high-performance mindset.
        Include: pacing, type of content (video/text/project), and how to avoid burnout.
        """
        return self.llm.query_llm(prompt)

    def get_recent_summary(self, user_id: str, top_k: int = 5) -> str:
        """
        Retrieves top-k recent memories (reflections, plans, steps) and summarizes them.
        """
        memories = search_memory(user_id=user_id, top_k=top_k)
        memory_texts = [m["text"] for m in memories if "text" in m]

        if not memory_texts:
            return "No major memories found yet."

        combined = "\n".join(memory_texts)

        prompt = f"""
        Summarize the following notes and reflections to understand what the user is focused on recently:

        {combined}

        Provide a short summary in 2–3 lines.
        """
        return self.llm.query_llm(prompt)
