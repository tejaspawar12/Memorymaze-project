from pydantic import BaseModel

class PlanInput(BaseModel):
    user_id: str
    message: str  # the full free-form user message
