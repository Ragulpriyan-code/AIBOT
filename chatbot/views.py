from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import ChatMessage, Conversation, Document
from .openai_client import get_ai_reply

from .rag.rag_pipeline import ingest_document, retrieve_context


def home(request, conversation_id=None):
    # ✅ RENDER HEALTH CHECK BYPASS
    # If Render's health checker hits '/', return 200 instead of a 302 redirect
    if "Go-http-client" in request.META.get("HTTP_USER_AGENT", ""):
        return JsonResponse({"status": "healthy", "source": "root_bypass"})

    # Manual login check since we removed the decorator
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user

    # ===============================
    # Resolve active conversation
    # ===============================
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=user)
    else:
        conversation = (
            Conversation.objects.filter(user=user).order_by("-created_at").first()
        )
        if not conversation:
            conversation = Conversation.objects.create(user=user, title="New chat")

    # ===============================
    # Handle POST
    # ===============================
    if request.method == "POST":
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        # 1. Handle Document Upload (if any)
        uploaded_file = request.FILES.get("document")
        doc_obj = None
        if uploaded_file:
            doc_obj = Document.objects.create(user=user, file=uploaded_file)
            conversation.active_document = doc_obj
            conversation.save()

            try:
                ingest_document(
                    user=user, uploaded_file=uploaded_file, document_id=doc_obj.id
                )
            except Exception as e:
                print(f"❌ Error during document ingestion: {e}")

            ChatMessage.objects.create(
                conversation=conversation,
                user=user,
                message_type="document",
                uploaded_file_name=uploaded_file.name,
                document=doc_obj,
            )

        # 2. Handle Text Message (if any)
        user_msg = request.POST.get("message", "").strip()
        bot_reply = ""

        if user_msg:
            # Get history
            history_qs = (
                ChatMessage.objects.filter(conversation=conversation)
                .exclude(message_type="document")
                .order_by("-created_at")[:6]
            )
            history_text = ""
            for m in reversed(history_qs):
                history_text += f"User: {m.user_message}\nBot: {m.bot_reply}\n"

            # Get Documents and Manifest (Ordered by upload time)
            doc_messages = ChatMessage.objects.filter(
                conversation=conversation, message_type="document"
            ).order_by("created_at")

            doc_ids = []
            doc_manifest = []
            seen_ids = set()
            for msg in doc_messages:
                if msg.document_id and msg.document_id not in seen_ids:
                    doc_ids.append(msg.document_id)
                    doc_manifest.append(msg.uploaded_file_name)
                    seen_ids.add(msg.document_id)

            document_text = ""
            if doc_ids:
                try:
                    # Pass the full document list so ordinal logic knows the count
                    document_text = "\n".join(
                        retrieve_context(question=user_msg, document_ids=doc_ids)
                    )
                except Exception as e:
                    print(f"⚠️ Context retrieval failed: {e}")

            bot_reply = get_ai_reply(
                message=user_msg,
                history_text=history_text,
                document_text=document_text,
                doc_manifest=doc_manifest,  # ✅ NEW: Tell AI about ALL docs
            )

            ChatMessage.objects.create(
                conversation=conversation,
                user=user,
                message_type="text",
                user_message=user_msg,
                bot_reply=bot_reply,
            )

            if conversation.title == "New chat":
                conversation.title = user_msg[:40]
                conversation.save()

        # 3. Return Response
        if is_ajax:
            return JsonResponse(
                {
                    "status": "success",
                    "bot_reply": bot_reply,
                    "user_msg": user_msg,
                    "uploaded_file": uploaded_file.name if uploaded_file else None,
                }
            )

        return redirect("conversation", conversation_id=conversation.id)

    # ===============================
    # Load UI
    # ===============================
    conversations = Conversation.objects.filter(user=user).order_by("-created_at")
    chat_history = ChatMessage.objects.filter(conversation=conversation).order_by(
        "created_at"
    )

    return render(
        request,
        "chatbot/index.html",
        {
            "chat_history": chat_history,
            "conversations": conversations,
            "active_conversation": conversation,
        },
    )


@login_required
def new_chat(request):
    conversation = Conversation.objects.create(user=request.user, title="New chat")
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
    return render(request, "registration/signup.html", {"form": form})


@login_required
def delete_chat(request, convo_id):
    conversation = get_object_or_404(Conversation, id=convo_id, user=request.user)
    conversation.delete()
    return redirect("home")


def health_check(request):
    """Health check endpoint for Render"""
    return JsonResponse({"status": "ok", "service": "aibot"})
