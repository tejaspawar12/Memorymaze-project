import os
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from app.embedding import get_embedding
from app.qdrant_client import search_memory, insert_memory
from app.llm import generate_response  # your LLM module
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter()
security = HTTPBearer()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

def get_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # typically user_id or username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
"""
@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, user_id: str = Depends(get_user_id_from_token)):
    query = req.message
    embedding = get_embedding(query)

    # Search memory for this user
    memories = search_memory(user_id, embedding)
    context = "\n".join([m.payload["text"] for m in memories]) if memories else ""

    # Generate response
    reply = generate_response(context=context, query=query)

    # Save user query and bot reply
    insert_memory(user_id, query, embedding)
    insert_memory(user_id, reply, get_embedding(reply))

    return {"response": reply}
"""

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, user_id: str = Depends(get_user_id_from_token)):
    try:
        query = req.message
        print(f"📨 Incoming query: {query} from user: {user_id}")

        embedding = get_embedding(query)
        print(f"🧠 Embedding: {embedding[:5]}...")

        memories = search_memory(user_id, embedding)
        context = "\n".join([m.payload["text"] for m in memories]) if memories else ""
        print(f"📚 Memory Context: {context[:100]}...")

        reply = generate_response(context=context, query=query)
        print(f"🤖 Reply: {reply}")

        insert_memory(user_id, query, embedding)
        insert_memory(user_id, reply, get_embedding(reply))

        return {"response": reply}

    except Exception as e:
        print("🚨 Error in chat_endpoint:", str(e))
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
