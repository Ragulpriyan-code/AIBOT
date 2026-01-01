from django.db import models
from django.conf import settings

# ==============================
# 📄 Document Model
# ==============================
class Document(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    file = models.FileField(upload_to="documents/")
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="chunks"
    )
    content = models.TextField()
    embedding = models.JSONField()  # vector
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk {self.id} of {self.document.file.name}"


# ==============================
# 💬 Conversation Model
# ==============================
class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations"
    )

    title = models.CharField(max_length=255, default="New chat")

    # ✅ Proper FK
    active_document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_in_conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==============================
# 🗨️ Chat Message Model (FIXED)
# ==============================
class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ("text", "Text"),
        ("document", "Document"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # ✅ FIXED HERE
        on_delete=models.CASCADE,
        related_name="messages"
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default="text"
    )

    user_message = models.TextField(blank=True)
    bot_reply = models.TextField(blank=True)

    uploaded_file_name = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.message_type == "document":
            return f"Document: {self.uploaded_file_name}"
        return self.user_message[:30]
