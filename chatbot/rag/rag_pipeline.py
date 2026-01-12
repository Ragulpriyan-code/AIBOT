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
    - Detects 'first', 'second', or filenames to narrow down search.
    """
    if not document_ids:
        return []

    from ..models import Document
    
    # 🔄 AUTO-RELOAD logic
    existing_texts = " ".join(GLOBAL_VECTOR_STORE.texts[:100])
    for d_id in document_ids:
        marker_start = f"[DOCUMENT_ID={d_id}"
        if marker_start not in existing_texts:
            doc = Document.objects.filter(id=d_id).first()
            if doc and doc.extracted_text:
                fname = doc.file.name.split('/')[-1]
                chunks = chunk_text(doc.extracted_text)
                wrapped = [f"[DOCUMENT_ID={d_id} FILENAME={fname}]\n{c}" for c in chunks]
                GLOBAL_VECTOR_STORE.add_texts(wrapped)

    # 🎯 INTENT DETECTION: Is the user asking for a general summary?
    is_general_query = any(w in question.lower() for w in ["explain", "summarize", "tell me about", "what is this"])
    
    # 🎯 FILTER BY NAME OR POSITION
    target_ids = document_ids
    lower_q = question.lower()
    
    # Handle "first", "second", etc.
    if "first" in lower_q and len(document_ids) >= 1:
        target_ids = [document_ids[0]]
    elif "second" in lower_q and len(document_ids) >= 2:
        target_ids = [document_ids[1]]
    
    # Handle specific filename mentions
    for d_id in document_ids:
        doc = Document.objects.filter(id=d_id).first()
        if doc and doc.file.name.split('/')[-1].lower() in lower_q:
            target_ids = [d_id]
            break

    # If it's a general query for a specific document, just get the first few chunks
    if is_general_query and len(target_ids) == 1:
        # Get chunks directly from store starting with that ID
        relevant_chunks = [t for t in GLOBAL_VECTOR_STORE.texts if f"[DOCUMENT_ID={target_ids[0]}" in t]
        if relevant_chunks:
            # Return first few chunks of THIS document
            return [c.split("]\n", 1)[-1] for c in relevant_chunks[:top_k]]

    # Otherwise, fallback to similarity search
    results = GLOBAL_VECTOR_STORE.similarity_search(query=question, top_k=top_k * 5)
    if not results: return []

    filtered = []
    for chunk in results:
        for d_id in target_ids:
            if f"[DOCUMENT_ID={d_id}" in chunk:
                content = chunk.split("]\n", 1)[-1]
                filtered.append(content)
                break 
        if len(filtered) >= top_k:
            break

    return filtered
