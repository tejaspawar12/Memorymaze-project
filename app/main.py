import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.routes import router as auth_router
from app.chat.routes import router as chat_router
from app.graph import routes as graph_routes


# 👇 Setup full traceback logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = FastAPI()

# 🌐 Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Auth routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# 🤖 Chat routes
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

