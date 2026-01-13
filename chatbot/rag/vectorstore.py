# chatbot/rag/vectorstore.py

import numpy as np
import os
import pickle
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class SimpleVectorStore:
    def __init__(self, persist_path=None):
        self.texts = []
        self.embeddings = []
        self.model = None
        self.persist_path = persist_path
        if persist_path:
            self._load_from_disk()

    def _load_model(self):
        if self.model is None and SentenceTransformer is not None:
            try:
                # Use local model cache directory
                base_dir = Path(__file__).resolve().parent.parent.parent
                cache_dir = str(base_dir / "model_cache")
                print(f"🔄 Loading SentenceTransformer from {cache_dir}...")
                self.model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_dir)
            except Exception as e:
                print(f"⚠️ Error loading SentenceTransformer: {e}")
                self.model = None

    def _save_to_disk(self):
        """Save vector store to disk"""
        if not self.persist_path:
            return
        try:
            data = {
                'texts': self.texts,
                'embeddings': self.embeddings
            }
            # Ensure directory exists
            persist_dir = Path(self.persist_path).parent
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to temporary file first, then rename (atomic write)
            temp_path = str(self.persist_path) + '.tmp'
            with open(temp_path, 'wb') as f:
                pickle.dump(data, f)
            
            # Atomic rename
            if os.path.exists(self.persist_path):
                os.remove(self.persist_path)
            os.rename(temp_path, self.persist_path)
            
            print(f"💾 Saved {len(self.texts)} chunks to {self.persist_path}")
        except Exception as e:
            print(f"⚠️ Error saving vector store: {e}")

    def _load_from_disk(self):
        """Load vector store from disk"""
        if not self.persist_path or not os.path.exists(self.persist_path):
            if self.persist_path:
                print(f"📂 No existing vector store found at {self.persist_path}, starting fresh")
            return
        try:
            with open(self.persist_path, 'rb') as f:
                data = pickle.load(f)
                self.texts = data.get('texts', [])
                self.embeddings = data.get('embeddings', [])
                print(f"✅ Loaded {len(self.texts)} chunks from {self.persist_path}")
        except Exception as e:
            print(f"⚠️ Error loading vector store from {self.persist_path}: {e}")
            # Reset to empty on error
            self.texts = []
            self.embeddings = []

    def add_texts(self, texts, metadata=None):
        self._load_model()
        if self.model is None:
            print("❌ Cannot add_texts: Model is not loaded. Check if sentence-transformers is installed.")
            return

        print(f"📝 Vectorizing {len(texts)} new chunks...")
        try:
            for text in texts:
                emb = self.model.encode(text)
                self.texts.append(text)
                self.embeddings.append(emb)
            
            print(f"✅ Current total chunks in store: {len(self.texts)}")
            
            # Auto-save after adding texts
            if self.persist_path:
                self._save_to_disk()
        except Exception as e:
            print(f"❌ Error adding texts to vector store: {e}")

    def similarity_search(self, query, top_k=3):
        self._load_model()
        if not self.texts:
            print("📭 Vector store is empty. No context to retrieve.")
            return []
        if self.model is None:
            print("❌ Cannot search: Model is not loaded.")
            return []

        print(f"🔍 Searching context for query: '{query}'...")
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


# 🔥 GLOBAL STORE with persistence
def get_vectorstore_path():
    """Get the path for the persistent vector store"""
    # Use a fixed path relative to the project root for reliability
    base_dir = Path(__file__).resolve().parent.parent.parent
    vectorstore_dir = base_dir / 'vectorstore_data'
    vectorstore_dir.mkdir(exist_ok=True)
    return str(vectorstore_dir / 'vectorstore.pkl')

# Initialize once at module level
GLOBAL_VECTOR_STORE = SimpleVectorStore(persist_path=get_vectorstore_path())

def initialize_vectorstore():
    """Returns the global vector store instance"""
    return GLOBAL_VECTOR_STORE


def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks
