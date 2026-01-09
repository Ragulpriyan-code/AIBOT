# chatbot/rag/vectorstore.py

import numpy as np
import hashlib


def simple_embed(text: str, dim: int = 384):
    """
    Lightweight deterministic embedding (Replit-safe).
    """
    vec = np.zeros(dim, dtype=np.float32)
    for i in range(dim):
        h = hashlib.md5(f"{text}-{i}".encode()).hexdigest()
        vec[i] = int(h[:8], 16) % 1000
    norm = np.linalg.norm(vec)
    return vec / norm if norm else vec


class SimpleVectorStore:
    def __init__(self):
        self.texts = []
        self.embeddings = []

    def add_texts(self, texts, metadata=None):
        for text in texts:
            emb = simple_embed(text)
            self.texts.append(text)
            self.embeddings.append(emb)

    def similarity_search(self, query, top_k=3):
        if not self.texts:
            return []

        query_emb = simple_embed(query)

        scores = []
        for idx, emb in enumerate(self.embeddings):
            score = float(np.dot(query_emb, emb))
            scores.append((score, self.texts[idx]))

        scores.sort(reverse=True, key=lambda x: x[0])
        return [text for _, text in scores[:top_k]]


# 🔥 GLOBAL STORE
GLOBAL_VECTOR_STORE = SimpleVectorStore()


def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap

    return chunks
