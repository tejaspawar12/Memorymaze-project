from app.memory.embedding import get_embedding
from app.memory.qdrant_client import insert_memory, search_memory

vec = get_embedding("Hello world!")
insert_memory("test_user", "Hello world!", vec, "user")
results = search_memory("test_user", vec)
print([r.payload["text"] for r in results])
