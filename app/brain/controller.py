from app.brain.progress_tracker import ProgressTracker
from app.brain.milestone_agent import MilestoneAgent
from app.brain.reflection_logger import ReflectionLogger
from app.brain.meta_learner import MetaLearner
from app.brain.planner import PlannerAgent
from app.brain.executor import ExecutorAgent
from app.embedding.embedder import Embedder
from app.llm.client import query_llm


class PlannerController:
    def __init__(self):
        self.llm = query_llm
        self.embedder = Embedder()

        # Agents
        self.planner = PlannerAgent(llm=self.llm, embedder=self.embedder)
        self.executor = ExecutorAgent(llm=self.llm, embedder=self.embedder)
        self.progress_tracker = ProgressTracker()
        self.milestone_agent = MilestoneAgent(llm=self.llm)
        self.reflection_logger = ReflectionLogger(llm=self.llm, embedder=self.embedder)
        self.meta_learner = MetaLearner(llm=self.llm)

    def handle_user_plan_request(self, user_id: str, message: str) -> list:
        """
        Main handler: use LLM to decide what the user wants, then trigger that task.
        """
        task = self.decide_task_from_llm(user_id, message)

        if task == "generate_plan":
            return self.planner.generate_and_store_plan(user_id, message)

        elif task == "next_step":
            result = self.executor.execute_next(user_id)
            return [result["guidance"]] if isinstance(result, dict) else [result]

        elif task == "track_progress":
            return ["✅ Great! I've noted your progress."]

        elif task == "reflect":
            return ["📝 Would you like to log this reflection? Just reply 'yes' and I’ll save it."]

        elif task == "insight":
            return [self.meta_learner.analyze_learning_pattern([], [])]

        elif task == "milestones":
            return self.milestone_agent.generate_milestones([])

        return ["🤖 I'm not sure what you mean yet. Can you rephrase or be more specific?"]

    def decide_task_from_llm(self, user_id: str, message: str) -> str:
        """
        LLM decides which internal task to trigger based on user input + context.
        """
        # 👇 Optional: Get context from memory if available
        context_summary = self.meta_learner.get_recent_summary(user_id)  # Can be stubbed for now

        prompt = f"""
You are a smart task routing assistant for a planner AI.

Here’s what the user said:
"{message}"

Here’s what we know about their recent activity:
"{context_summary}"

Choose ONE task that best fits the situation:
- generate_plan
- next_step
- track_progress
- reflect
- insight
- milestones

Respond ONLY with the task name.
"""

        response = self.llm(prompt)
        task = response.strip().lower()

        print(f"🧠 LLM routed task: {task}")
        return task
