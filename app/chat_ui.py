# app/chat_ui.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.embedding import embed_text
from app.qdrant_client import insert_memory, search_memory
from app.llm import generate_response

router = APIRouter()

# 🧾 Input schema
class ChatRequest(BaseModel):
    user_id: str
    message: str

# 📤 Output schema
class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat_with_mmaze(request: ChatRequest):
    user_id = request.user_id.strip()
    user_input = request.message.strip()

    if not user_input:
        raise HTTPException(status_code=400, detail="Empty message")

    # 🔹 1. Embed current message
    embedding = embed_text(user_input)

    # 🔹 2. Store current message in Qdrant with metadata
    insert_memory(user_id=user_id, text=user_input, vector=embedding)

    # 🔹 3. Search past memories
    memory_chunks = search_memory(user_id=user_id, query_vector=embedding)

    # 🔹 4. Generate personalized LLM response
    reply = generate_response(user_input=user_input, memory_chunks=memory_chunks)

    return ChatResponse(reply=reply)
