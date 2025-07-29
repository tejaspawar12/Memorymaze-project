#app/chat/routes
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.routes import get_current_user
from app.memory.memory_chatbot import MemoryChatbot
from app.llm.client import query_llm
from app.embedding.embedder import Embedder
from app.brain.controller import PlannerController  # ✅ NEW controller import


router = APIRouter()

# 📥 Request models
class ChatRequest(BaseModel):
    message: str

class PlannerRequest(BaseModel):
    message: str  # No `day` field now, inferred automatically if found in text

# 📤 Response models
class ChatResponse(BaseModel):
    reply: str

class PlannerResponse(BaseModel):
    plan: list[str]

# ✅ Chat route
@router.post("/message", response_model=ChatResponse)
def chat_with_mmaze(request: ChatRequest, user: dict = Depends(get_current_user)):
    try:
        if not isinstance(user, dict) or "username" not in user:
            raise HTTPException(status_code=401, detail="Unauthorized user")

        user_id = user["username"].strip()
        message = request.message.strip()

        if not message:
            raise HTTPException(status_code=400, detail="Empty message")

        chatbot = MemoryChatbot(user_id=user_id)
        reply = chatbot.chat(user_id=user_id, message=message)
        return ChatResponse(reply=reply)

    except Exception as e:
        print("🔥 Error in chat route:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# ✅ Updated Planner route with Controller
@router.post("/planner/plan", response_model=PlannerResponse)
def generate_planner_plan(request: PlannerRequest, user: dict = Depends(get_current_user)):
    try:
        if not isinstance(user, dict) or "username" not in user:
            raise HTTPException(status_code=401, detail="Unauthorized user")

        user_id = user["username"].strip()
        user_input = request.message.strip()

        if not user_input:
            raise HTTPException(status_code=400, detail="Empty planner input")

        # 🧠 Use the unified controller instead of direct PlannerAgent
        controller = PlannerController()
        steps = controller.handle_user_plan_request(user_id, user_input)

        return PlannerResponse(plan=steps)

    except Exception as e:
        print("🔥 Planner error:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
