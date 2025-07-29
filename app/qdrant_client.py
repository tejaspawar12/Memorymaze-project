# app/qdrant.py

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, SearchParams
from qdrant_client.http.models import VectorParams, Distance
import uuid
from qdrant_client.models import PayloadSchemaType, PayloadIndexInfo
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mmaze_cluster")

# ✅ Init Client
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

# ✅ Create collection if not exists
def setup_collection(vector_dim: int = 768):
    # Just a sanity check — skip if already exists
    collections = client.get_collections().collections
    if COLLECTION_NAME not in [c.name for c in collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="user_id",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' created.")
    else:
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' already exists. Using existing.")


# ✅ Insert embedding for a user
def insert_memory(user_id: str, text: str, embedding: list):
    point_id = str(uuid.uuid4())
    metadata = {
        "user_id": user_id,
        "text": text,
    }
    point = PointStruct(id=point_id, vector=embedding, payload=metadata)
    client.upsert(collection_name=COLLECTION_NAME, points=[point])

# ✅ Semantic search filtered by user_id
def search_memory(user_id: str, embedding: list, top_k: int = 5):
    return client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=top_k,
        search_params=SearchParams(hnsw_ef=128, exact=False),
        query_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
    )
