import os

from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL_NAME = "openai/gpt-oss-20b"  # ✅ THIS IS THE FIX

def get_ai_reply(message, history_text="", document_text=""):
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
