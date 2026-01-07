# chatbotapp/rag/loader.py

from PyPDF2 import PdfReader
from docx import Document as DocxDocument


def load_document(uploaded_file):
    """
    Load text from PDF, DOCX, or TXT
    """

    filename = uploaded_file.name.lower()

    # ==========================
    # PDF
    # ==========================
    if filename.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    # ==========================
    # DOCX
    # ==========================
    elif filename.endswith(".docx"):
        doc = DocxDocument(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs).strip()

    # ==========================
    # TXT
    # ==========================
    elif filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore").strip()

    else:
        raise ValueError("Unsupported file type") 