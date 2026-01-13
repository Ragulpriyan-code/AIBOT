from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    
    def ready(self):
        """Initialize vector store when Django starts (lazy)"""
        try:
            from .rag.vectorstore import initialize_vectorstore
            initialize_vectorstore()
            logger.info("✅ Vector store initialized (lazy)")
        except Exception as e:
            logger.warning(f"⚠️ Warning: Could not initialize vector store: {e}")
            pass