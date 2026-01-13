from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    
    def ready(self):
        """Initialize vector store when Django starts"""
        try:
            from .rag.vectorstore import initialize_vectorstore
            initialize_vectorstore()
            print("✅ Vector store initialized on startup")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize vector store on startup: {e}")