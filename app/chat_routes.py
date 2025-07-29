from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from app.embedding import get_embedding
from app.qdrant_client import insert_memory, search_memory
from app.llm import generate_response
from app.auth import get_current_user  # You'll need this to extract username from JWT

router = APIRouter()

# 👤 Input format
class ChatMessage(BaseModel):
    query: str

# 💬 Output format
class ChatReply(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatReply)
def chat_with_mmaze(chat: ChatMessage, username: str = Depends(get_current_user)):
    user_id = username  # use username as user_id

    # 🧠 Step 1: Embed the user message
    query_embedding = get_embedding(chat.message)

    # 🔍 Step 2: Search for similar memories for this user
    similar_memories = search_memory(user_id=user_id, query_embedding=query_embedding)

    # 🧠 Step 3: Use context + user input to get a response
    memory_context = "\n".join([mem['text'] for mem in similar_memories])
    prompt = f"""You are M-Maze, a personal assistant.
You remember the user's past messages and respond accordingly.

Past memory:
{memory_context}

Current user message:
{chat.message}

Respond in a helpful, friendly, and intelligent way:
"""
    response = generate_response(prompt)

    # 💾 Step 4: Store the user message + response in memory
    insert_memory(user_id, chat.message)
    insert_memory(user_id, response)

    return {"reply": response}