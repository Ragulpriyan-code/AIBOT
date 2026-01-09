import os
from openai import OpenAI

MODEL_NAME = "openai/gpt-oss-20b"  # Groq-hosted OSS model


def get_client():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )


def get_ai_reply(message, history_text="", document_text=""):
    client = get_client()

    prompt = f"""
You are a helpful AI assistant.

DOCUMENT:
{document_text}

CHAT HISTORY:
{history_text}

USER:
{message}
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        temperature=0.4,
        max_output_tokens=512,
    )

    return response.output_text
