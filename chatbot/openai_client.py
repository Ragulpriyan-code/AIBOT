import os
import re
from openai import OpenAI

MODEL_NAME = "openai/gpt-oss-20b"  # Groq-hosted OSS model

def clean_llm_response(text):
    if not text:
        return ""
        
    # Fix literal unicode sequences like \u000A or \u002D
    text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)
    
    # Fix other common literal escapes like \n, \t, etc.
    text = text.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t').replace('\\"', '"').replace("\\'", "'")

    # Remove markdown tables (aggressive - if LLM ignores instructions)
    # We replace table-like lines with simpler formatting
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if '|' in line and (line.strip().startswith('|') or line.strip().endswith('|')):
            # It's a table row - skip or convert to list
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells and not all(all(char in '-' for char in c) for c in cells):
                cleaned_lines.append("- " + ": ".join(cells))
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    # Remove long separators and excessive whitespace
    text = re.sub(r'\n-{3,}\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

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
You are an AI assistant similar to ChatGPT. You have access to user-uploaded documents below.

IMPORTANT:
1. If 'DOCUMENT CONTEXT' is provided, use it to answer the user's question, especially if they ask to "explain", "summarize", or "read" a file.
2. If the user mentions "this PDF", "the document", or a specific filename, look in the 'DOCUMENT CONTEXT' first.
3. NO TABLES: Never use markdown tables. Use bullet points instead.
4. NO SEPARATORS: Do not use horizontal rules like '---'.
5. CONVERSATIONAL: Be friendly and simple.

DOCUMENT CONTEXT:
{document_text}

CHAT HISTORY:
{history_text}

USER QUESTION:
{message}

ASSISTANT RESPONSE:
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        temperature=0.4,
        max_output_tokens=700, # Increased for better detail 
    )

    raw_reply = getattr(response, 'output_text', '')
    if not raw_reply and hasattr(response, 'choices'):
        # Fallback for standard OpenAI response structure
        raw_reply = response.choices[0].message.content

    return clean_llm_response(raw_reply)
