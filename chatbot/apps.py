from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    
    def ready(self):
        """Initialize vector store when Django starts"""
        # Initialize vector store safely - it handles multiple initializations
        # This runs in both master and worker processes, but that's OK
        # because initialize_vectorstore() checks if already initialized
        try:
            from .rag.vectorstore import initialize_vectorstore
            vectorstore = initialize_vectorstore()
            # Pre-load the model to avoid blocking on first request
            # This is safe even if called multiple times
            if vectorstore.model is None:
                vectorstore._load_model()
            logger.info("✅ Vector store initialized on startup")
        except Exception as e:
            logger.warning(f"⚠️ Warning: Could not initialize vector store on startup: {e}")
            # Don't crash the app if vector store fails
            # Workers will initialize on first request if needed
            pass