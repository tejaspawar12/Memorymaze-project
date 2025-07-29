from app.embedding.embedder import Embedder
from app.memory.qdrant_client import (
    insert_memory,
    search_memory,
    update_memory_by_id,
    delete_memory_by_id,
)
from app.llm.client import query_llm
from app.personality.personality_profiler import PersonalityProfiler
from datetime import datetime

class MemoryManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.embedder = Embedder()
        self.profiler = PersonalityProfiler(user_id=user_id)  # ✅ Personalized traits per user
        print(f"🧠 MemoryManager initialized for user_id: {user_id}")

    def add_memory(self, text: str, role: str = "user") -> str:
        embedding = self.embedder.get_embedding(text)

        # 🧠 Trait inference
        self.profiler.infer_traits_from_text(text)

        # 🏷️ Tag extraction using LLM
        tag_prompt = (
            f"Extract 2–4 tags for the following user input:\n\"{text}\"\n"
            "Only return a Python list of lowercase category words (like ['identity', 'goal', 'emotion'])."
        )
        tag_response = query_llm(tag_prompt)

        try:
            tags = eval(tag_response.strip())
            if not isinstance(tags, list):
                tags = []
        except:
            tags = []

        memory_id = insert_memory(
            user_id=self.user_id,
            text=text,
            vector=embedding,
            role=role,
            tags=tags,
            timestamp=datetime.now().isoformat()
        )

        print(f"✅ Memory added for {self.user_id}: {memory_id} | Tags: {tags}")
        return memory_id

    def query_memory(self, query: str, top_k: int = 5):
        query_vector = self.embedder.get_embedding(query)
        results = search_memory(user_id=self.user_id, query_vector=query_vector, top_k=top_k)
        return [
            {
                "id": str(r.id),
                "text": r.payload.get("text", ""),
                "tags": r.payload.get("tags", []),
                "timestamp": r.payload.get("timestamp", ""),
                "score": r.score,
            }
            for r in results
        ]

    def delete_memory(self, memory_id: str):
        delete_memory_by_id(user_id=self.user_id, memory_id=memory_id)

    def update_memory(self, memory_id: str, new_text: str, new_tags: list = None):
        embedding = self.embedder.get_embedding(new_text)
        new_payload = {
            "text": new_text,
            "tags": new_tags or [],
            "timestamp": datetime.now().isoformat(),
            "user_id": self.user_id
        }
        update_memory_by_id(user_id=self.user_id, memory_id=memory_id, vector=embedding, payload=new_payload)

    def summarize_key_facts(self, top_k: int = 100) -> str:
        memories = self.query_memory(" ", top_k=top_k)
        combined = "\n".join([m["text"] for m in memories])
        prompt = (
            "You are a personal memory assistant. Summarize key facts about the user "
            "from the following past interactions. Include name, goals, interests, and repeated behaviors if possible:\n\n"
            f"{combined}\n\nReturn a short paragraph summary."
        )
        return query_llm(prompt)

    def get_fact(self, fact_type: str) -> str:
        memories = self.query_memory(" ", top_k=100)
        combined = "\n".join([m["text"] for m in memories])
        prompt = (
            f"You are an assistant that extracts specific facts from memory logs.\n"
            f"From the following, extract only the user's {fact_type}:\n\n"
            f"{combined}\n\n"
            "Respond with only the value, nothing else."
        )
        return query_llm(prompt).strip()

    def get_memories_by_tag(self, tag: str, top_k: int = 50):
        results = self.query_memory(" ", top_k=top_k)
        return [m for m in results if tag in m.get("tags", [])]

    def add_goal(self, text: str, category: str = "general", deadline: str = None):
        if deadline:
            text += f" (Deadline: {deadline})"
        return self.add_memory(text, role="user")

    def get_goals(self):
        memories = self.query_memory(" ", top_k=100)
        return [m for m in memories if "goal" in m.get("tags", [])]

    def check_goal_status(self):
        goals = self.get_goals()
        if not goals:
            return "You haven't shared any specific goals yet."

        summary = "Here are your current goals:\n"
        for g in goals:
            date = g["timestamp"].split("T")[0]
            summary += f"• {g['text']} (added on {date})\n"
        return summary
