# app/agents/progress_tracker.py

from datetime import datetime
from app.memory.qdrant_client import update_memory_by_id, get_all_user_memory
from app.embedding.embedder import Embedder

class ProgressTracker:
    def __init__(self):
        self.embedder = Embedder()

    def mark_step_completed(self, user_id: str, step_text: str):
        # Search memory for this step
        memories = get_all_user_memory(user_id)
        for mem in memories:
            if step_text.strip().lower() in mem.payload.get("text", "").strip().lower():
                payload = mem.payload
                payload["status"] = "completed"
                payload["completed_at"] = datetime.utcnow().isoformat()
                update_memory_by_id(user_id, mem.id, mem.vector, payload)
                return f"✅ Marked step as completed: {step_text}"

        return f"⚠️ Step not found for user: {user_id}"

    def get_current_step(self, user_id: str):
        memories = get_all_user_memory(user_id)
        for mem in memories:
            if mem.payload.get("status", "") != "completed":
                return mem.payload.get("text", "No step found")
        return "🎉 All steps completed!"

    def get_progress_summary(self, user_id: str):
        memories = get_all_user_memory(user_id)
        total = len(memories)
        completed = sum(1 for mem in memories if mem.payload.get("status") == "completed")
        return {
            "total_steps": total,
            "completed_steps": completed,
            "pending_steps": total - completed
        }
