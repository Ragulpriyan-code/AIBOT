from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import ChatMessage, Conversation, Document
from .openai_client import get_ai_reply

from .rag.rag_pipeline import ingest_document, retrieve_context



@login_required
def home(request, conversation_id=None):
    user = request.user

    # ===============================
    # Resolve active conversation
    # ===============================
    if conversation_id:
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=user
        )
    else:
        conversation = (
            Conversation.objects.filter(user=user)
            .order_by("-created_at")
            .first()
        )
        if not conversation:
            conversation = Conversation.objects.create(
                user=user, title="New chat"
            )

    # ===============================
    # Handle POST
    # ===============================
    if request.method == "POST":

        # ---- Document upload ----
        uploaded_file = request.FILES.get("document")
        if uploaded_file:
            document = Document.objects.create(
                user=user,
                file=uploaded_file
            )

            conversation.active_document = document
            conversation.save()

            ingest_document(
                user=user,
                uploaded_file=uploaded_file,
                document_id=document.id
            )

            ChatMessage.objects.create(
                conversation=conversation,
                user=user,
                message_type="document",
                uploaded_file_name=uploaded_file.name
            )

            return redirect("conversation", conversation_id=conversation.id)

        # ---- Text message ----
        user_msg = request.POST.get("message", "").strip()

        if user_msg:
            history_qs = (
                ChatMessage.objects
                .filter(conversation=conversation)
                .exclude(message_type="document")
                .order_by("-created_at")[:6]
            )

            history_text = ""
            for m in reversed(history_qs):
                history_text += f"User: {m.user_message}\n"
                history_text += f"Bot: {m.bot_reply}\n"

            document_text = ""
            if conversation.active_document:
                chunks = retrieve_context(
                    question=user_msg,
                    document_id=conversation.active_document.id
                )
                document_text = "\n".join(chunks)

            bot_reply = get_ai_reply(
                message=user_msg,
                history_text=history_text,
                document_text=document_text
            )

            ChatMessage.objects.create(
                conversation=conversation,
                user=user,
                message_type="text",
                user_message=user_msg,
                bot_reply=bot_reply
            )

            if conversation.title == "New chat":
                conversation.title = user_msg[:40]
                conversation.save()

        return redirect("conversation", conversation_id=conversation.id)

    # ===============================
    # Load UI
    # ===============================
    conversations = (
        Conversation.objects
        .filter(user=user)
        .order_by("-created_at")
    )

    chat_history = (
        ChatMessage.objects
        .filter(conversation=conversation)
        .order_by("created_at")
    )

    return render(
        request,
        "chatbot/index.html",
        {
            "chat_history": chat_history,
            "conversations": conversations,
            "active_conversation": conversation,
        }
    )

@login_required
def new_chat(request):
    conversation = Conversation.objects.create(
        user=request.user,
        title="New chat"
    )
    return redirect("conversation", conversation_id=conversation.id)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/signup.html",
        {"form": form}
    )

@login_required
def delete_chat(request, convo_id):
    conversation = get_object_or_404(
        Conversation,
        id=convo_id,
        user=request.user
    )
    conversation.delete()
    return redirect("home")

