# chatbotapp/rag/embeddings.py

from typing import List

_model = None  # lazy-loaded


def get_model():
    """
    Lazy-load SentenceTransformer model.
    Loads only when called, not at Django startup.
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print("⚠️ Embedding model not available:", e)
            _model = None
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_model()
    if model is None:
        return []  # Safe fallback (Replit-safe)

    return model.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=True
    ).tolist()
