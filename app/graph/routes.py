from fastapi import APIRouter
from app.graph.graph_manager import GraphMemoryManager

router = APIRouter()

@router.get("/graph/test")
def test_graph():
    gm = GraphMemoryManager()
    gm.create_user_node("user123")
    gm.create_plan("user123", "Become a scientist", "Day 1")
    gm.close()
    return {"message": "Graph entry created!"}
