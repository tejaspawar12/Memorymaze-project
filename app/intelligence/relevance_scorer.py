# app/intelligence/relevance_scorer.py

from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
import numpy as np

class RelevanceScorer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", similarity_threshold: float = 0.65):
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        print(f"✅ RelevanceScorer initialized with model: {model_name}")

    def score_relevance(self, query: str, memories: List[Dict]) -> List[Dict]:
        """
        Scores each memory against the query and returns top relevant ones.
        """
        if not memories:
            return []

        # Embed query and memory texts
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        memory_texts = [m["text"] for m in memories]
        memory_embeddings = self.model.encode(memory_texts, convert_to_tensor=True)

        # Compute cosine similarities
        cosine_scores = util.cos_sim(query_embedding, memory_embeddings)[0]

        # Filter and sort based on similarity
        scored_memories = []
        for mem, score in zip(memories, cosine_scores):
            score_val = float(score)
            if score_val >= self.similarity_threshold:
                mem["relevance_score"] = score_val
                scored_memories.append(mem)

        # Sort by score descending
        scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_memories

    def deduplicate(self, memories: List[Dict], dedup_threshold: float = 0.92) -> List[Dict]:
        """
        Removes near-duplicate memory chunks.
        """
        if len(memories) <= 1:
            return memories

        texts = [m["text"] for m in memories]
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        similarity_matrix = util.cos_sim(embeddings, embeddings)

        unique_indices = []
        for i in range(len(texts)):
            if all(similarity_matrix[i][j] < dedup_threshold for j in unique_indices):
                unique_indices.append(i)

        return [memories[i] for i in unique_indices]
