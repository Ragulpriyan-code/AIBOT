# chatbot/rag/vectorstore.py

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class SimpleVectorStore:
    def __init__(self):
        self.texts = []
        self.embeddings = []
        self.model = None

    def _load_model(self):
        if self.model is None and SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"⚠️ Error loading SentenceTransformer: {e}")
                self.model = None

    def add_texts(self, texts, metadata=None):
        self._load_model()
        if self.model is None:
            print("❌ Cannot add_texts: Model is not loaded. Check if sentence-transformers is installed.")
            return

        for text in texts:
            emb = self.model.encode(text)
            self.texts.append(text)
            self.embeddings.append(emb)

    def similarity_search(self, query, top_k=3):
        self._load_model()
        if not self.texts:
            return []
        if self.model is None:
            print("❌ Cannot search: Model is not loaded.")
            return []

        query_emb = self.model.encode(query)
        scores = []

        for idx, emb in enumerate(self.embeddings):
            # Calculate cosine similarity
            norm_q = np.linalg.norm(query_emb)
            norm_e = np.linalg.norm(emb)
            if norm_q > 0 and norm_e > 0:
                score = np.dot(query_emb, emb) / (norm_q * norm_e)
            else:
                score = 0.0
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
