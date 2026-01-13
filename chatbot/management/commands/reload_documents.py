from django.core.management.base import BaseCommand
from chatbot.models import Document
from chatbot.rag.vectorstore import initialize_vectorstore
from chatbot.rag.rag_pipeline import chunk_text


class Command(BaseCommand):
    help = 'Reload all documents from database into the vector store'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Reloading documents into vector store...')
        
        # Initialize vector store
        vectorstore = initialize_vectorstore()
        
        # Check if model can load
        vectorstore._load_model()
        if vectorstore.model is None:
            self.stdout.write(self.style.ERROR('❌ Failed to load SentenceTransformer model'))
            return
        
        # Get all documents with extracted text
        documents = Document.objects.filter(
            extracted_text__isnull=False
        ).exclude(extracted_text='')
        
        total_count = documents.count()
        self.stdout.write(f'📄 Found {total_count} documents with extracted text')
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING('⚠️ No documents to reload'))
            return
        
        reloaded_count = 0
        total_chunks = 0
        
        for doc in documents:
            try:
                if doc.extracted_text:
                    chunks = chunk_text(doc.extracted_text)
                    fname = doc.file.name.split('/')[-1] if doc.file.name else f'doc_{doc.id}'
                    wrapped_chunks = [
                        f"[DOCUMENT_ID={doc.id} FILENAME={fname}]\n{chunk}"
                        for chunk in chunks
                    ]
                    vectorstore.add_texts(
                        texts=wrapped_chunks,
                        metadata={
                            "user_id": doc.user.id,
                            "filename": fname,
                        }
                    )
                    reloaded_count += 1
                    total_chunks += len(chunks)
                    self.stdout.write(f'✅ Reloaded: {fname} ({len(chunks)} chunks)')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error reloading document {doc.id}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully reloaded {reloaded_count}/{total_count} documents '
                f'({total_chunks} total chunks)'
            )
        )
