import re
from app.memory.memory_manager import MemoryManager
from app.llm.client import query_llm
from app.intelligence.relevance_scorer import RelevanceScorer  # New

class MemoryChatbot:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memory = MemoryManager(user_id=user_id)
        self.relevance_scorer = RelevanceScorer()
        print(f"✅ MemoryChatbot initialized for user: {user_id}")

    def chat(self, user_id: str, message: str) -> str:
        memory = self.memory

        # STEP 1: Goal detection
        goal_patterns = [
            r"\b(i want to|my goal is to|i plan to|i aim to|i will try to)\b (.+)",
            r"\bcomplete|finish|achieve|reach|build\b .+"
        ]
        matched_goal = next((message for pattern in goal_patterns if re.search(pattern, message.lower())), None)

        if matched_goal:
            category = "career" if "project" in message.lower() else "general"
            memory.add_goal(matched_goal, category=category)

        # STEP 2: Store user message
        memory.add_memory(message, role="user")

        # STEP 3: Retrieve and score relevant memories
        raw_memories = memory.query_memory(message, top_k=15)
        scored_memories = self.relevance_scorer.score_relevance(message, raw_memories)
        deduped_memories = self.relevance_scorer.deduplicate(scored_memories)
        similar_context = "\n".join([f"- {m['text']}" for m in deduped_memories]) or "No relevant memories found."

        # STEP 4: Long-term user facts
        key_facts_summary = memory.summarize_key_facts()

        # STEP 5: Personality traits
        traits = memory.profiler.get_traits()
        trait_summary = ", ".join(f"{k}: {v['value']}" for k, v in traits.items()) or "unknown"

        # STEP 6: User goals
        current_goals = memory.check_goal_status()

        # STEP 7: Construct final prompt
        prompt = f"""
You are MemoryMaze, a thoughtful, memory-enhanced, personality-aware AI assistant.
Your name is M-maze, created to build deep personal relationships with your user.

Only mention facts you actually know from the user's past messages, personality traits, and current goals.
If unsure about something, ask the user to clarify instead of hallucinating.

Use a warm, curious, and supportive tone in your response — but do NOT repeat style notes like this one in the final reply.

---
Personality Traits:
{trait_summary}

Key Long-Term Facts:
{key_facts_summary}

Relevant Past Interactions:
{similar_context}

User's Current Goals:
{current_goals}

Now the user says:
"{message}"

Reply intelligently based only on known context.
"""
        # STEP 8: Generate reply using Bedrock LLM
        reply = query_llm(prompt)

        # STEP 9: Store assistant reply in memory
        memory.add_memory(reply, role="assistant")

        return reply
