import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct, Filter, FieldCondition, MatchValue, SearchParams, Payload
)
from qdrant_client.http.models import VectorParams, Distance
from qdrant_client.models import PayloadSchemaType

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mmaze_cluster")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def setup_collection(vector_dim: int = 1024):
    collections = client.get_collections().collections
    if COLLECTION_NAME not in [c.name for c in collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
        )
        print(f"✅ Created collection: {COLLECTION_NAME}")

    # Always ensure user_id index exists
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="user_id",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print(f"🔁 Ensured 'user_id' index exists.")

def insert_memory(user_id: str, text: str, vector: list, role: str, tags: list = None, timestamp: str = None) -> str:
    point_id = str(uuid.uuid4())
    payload: Payload = {
        "user_id": user_id,
        "text": text,
        "role": role,
        "tags": tags or [],
        "timestamp": timestamp or ""
    }
    point = PointStruct(id=point_id, vector=vector, payload=payload)
    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    print(f"🧠 Inserted memory for user {user_id} with role={role}")
    return point_id

def search_memory(user_id: str, query_vector: list, top_k: int = 5):
    return client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        search_params=SearchParams(hnsw_ef=128, exact=False),
        query_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
    )

def update_memory_by_id(user_id: str, memory_id: str, vector: list, payload: dict):
    # Always reassign user_id to payload to prevent orphaned updates
    payload["user_id"] = user_id
    point = PointStruct(id=memory_id, vector=vector, payload=payload)
    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    print(f"✅ Updated memory {memory_id} for user {user_id}")

def delete_memory_by_id(user_id: str, memory_id: str):
    # Optional: enforce user_id match before deletion if needed
    client.delete(collection_name=COLLECTION_NAME, points_selector={"points": [memory_id]})
    print(f"🗑️ Deleted memory {memory_id} for user {user_id}")

def get_all_user_memory(user_id: str):
    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        ),
        limit=100
    )
    return results
