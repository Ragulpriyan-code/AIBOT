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
    - If memory is empty, auto-reloads from DB.
    """

    # 🔄 AUTO-RELOAD: If store is empty but we have IDs, reload them from DB
    if document_ids:
        from ..models import Document
        
        # Check if we need to reload any document
        existing_texts = " ".join(GLOBAL_VECTOR_STORE.texts[:100]) # Sample for speed
        
        for d_id in document_ids:
            marker_start = f"[DOCUMENT_ID={d_id}"
            if marker_start not in existing_texts:
                doc = Document.objects.filter(id=d_id).first()
                if doc and doc.extracted_text:
                    fname = doc.file.name.split('/')[-1]
                    print(f"🔄 Auto-reloading {fname} into vector store...")
                    chunks = chunk_text(doc.extracted_text)
                    wrapped = [f"[DOCUMENT_ID={d_id} FILENAME={fname}]\n{c}" for c in chunks]
                    GLOBAL_VECTOR_STORE.add_texts(wrapped)

    results = GLOBAL_VECTOR_STORE.similarity_search(
        query=question,
        top_k=top_k * 5 
    )

    if not results:
        return []

    filtered = []

    for chunk in results:
        if document_ids:
            found = False
            for d_id in document_ids:
                if f"[DOCUMENT_ID={d_id}" in chunk:
                    found = True
                    parts = chunk.split("]\n", 1)
                    marker = parts[0]
                    content = parts[1]
                    
                    filename = "Unknown"
                    if "FILENAME=" in marker:
                        filename = marker.split("FILENAME=")[1]
                    
                    filtered.append(f"[File: {filename}]\n{content}")
                    break 
            if found and len(filtered) >= top_k:
                break
        else:
            filtered.append(chunk)
            if len(filtered) >= top_k:
                break

    return filtered
