# chatbot/rag/rag_pipeline.py

from .loader import load_document
from .vectorstore import GLOBAL_VECTOR_STORE, chunk_text


# ======================================================
# 📄 INGEST DOCUMENT (PDF / DOCX / TXT)
# ======================================================
def ingest_document(user, uploaded_file, document_id):
    """
    Store document chunks with document_id embedded into text.
    Persists extracted text to DB for auto-reload.
    """

    text = load_document(uploaded_file)

    if not text or not text.strip():
        print("❌ No text extracted")
        return

    # ✅ SAVE TO DATABASE (for persistence across restarts)
    from ..models import Document
    Document.objects.filter(id=document_id).update(extracted_text=text)

    chunks = chunk_text(text)

    # 🔑 Embed document_id and FILENAME into the text itself
    fname = uploaded_file.name
    wrapped_chunks = [
        f"[DOCUMENT_ID={document_id} FILENAME={fname}]\n{chunk}"
        for chunk in chunks
    ]

    GLOBAL_VECTOR_STORE.add_texts(
        texts=wrapped_chunks,
        metadata={
            "user_id": user.id,
            "filename": fname,
        }
    )

    print(f"✅ Ingested {len(chunks)} chunks for document {document_id}")
    

# ======================================================
# 🔍 RETRIEVE CONTEXT (SUPPORT MULTI-DOC + AUTO-RELOAD)
# ======================================================
def retrieve_context(question, document_ids=None, top_k=3):
    """
    Retrieve chunks.
    - If document_ids is provided (list) → only chunks from those documents.
    - Matches ordinal words (first, second, last) to the correct doc.
    - 🔄 PRODUCTION FIX: Auto-reloads context into the current worker if missing.
    """
    if not document_ids:
        return []

    from ..models import Document
    
    # 🔄 ROBUST AUTO-RELOAD (Fix for Render/Multi-worker)
    # Get all text markers currently in this process's memory
    currently_loaded_markers = "".join([t.split(']\n', 1)[0] for t in GLOBAL_VECTOR_STORE.texts[:500]])
    
    for d_id in document_ids:
        marker = f"[DOCUMENT_ID={d_id}"
        if marker not in currently_loaded_markers:
            doc = Document.objects.filter(id=d_id).first()
            if doc and doc.extracted_text:
                fname = doc.file.name.split('/')[-1]
                print(f"📦 [Worker Sync] Loading {fname} (ID: {d_id}) into memory...")
                chunks = chunk_text(doc.extracted_text)
                wrapped = [f"[DOCUMENT_ID={d_id} FILENAME={fname}]\n{c}" for c in chunks]
                GLOBAL_VECTOR_STORE.add_texts(wrapped)
            else:
                print(f"⚠️ [Worker Sync] Document {d_id} has no extracted text in DB.")

    # 🎯 INTENT DETECTION
    is_general_query = any(w in question.lower() for w in ["explain", "summarize", "tell me about", "what is this"])
    
    target_ids = document_ids
    lower_q = question.lower()
    
    order_map = {
        "first": 0, "1st": 0, "one": 0,
        "second": 1, "2nd": 1, "two": 1,
        "third": 2, "3rd": 2, "three": 2, "3": 2,
        "last": -1, "latest": -1, "recent": -1
    }
    
    for word, idx in order_map.items():
        if word in lower_q:
            try:
                target_ids = [document_ids[idx]]
                break
            except (IndexError, KeyError):
                continue
    
    if target_ids == document_ids:
        for d_id in document_ids:
            doc = Document.objects.filter(id=d_id).first()
            if doc and doc.file.name.split('/')[-1].lower() in lower_q:
                target_ids = [d_id]
                break

    if is_general_query and len(target_ids) == 1:
        try:
            curr_idx = document_ids.index(target_ids[0]) + 1
        except ValueError:
            curr_idx = "?"

        relevant_chunks = [t for t in GLOBAL_VECTOR_STORE.texts if f"[DOCUMENT_ID={target_ids[0]}" in t]
        if relevant_chunks:
            res = []
            for c in relevant_chunks[:3]:
                content = c.split("]\n", 1)[-1]
                res.append(f"[Document {curr_idx}]\n{content}")
            return res

    # Similarity Search
    results = GLOBAL_VECTOR_STORE.similarity_search(query=question, top_k=top_k * 5)
    if not results: return []

    filtered = []
    for chunk in results:
        for idx, d_id in enumerate(document_ids):
            if f"[DOCUMENT_ID={d_id}" in chunk:
                if d_id in target_ids:
                    content = chunk.split("]\n", 1)[-1]
                    filtered.append(f"[Document {idx+1}]\n{content}")
                break 
        if len(filtered) >= top_k:
            break

    return filtered
