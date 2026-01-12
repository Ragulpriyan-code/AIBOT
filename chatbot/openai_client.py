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

def get_ai_reply(message, history_text="", document_text="", doc_manifest=None):
    client = get_client()

    # Generate a readable list of available documents
    inventory = "NONE"
    if doc_manifest:
        inventory = "\n".join([f"{i+1}. {name}" for i, name in enumerate(doc_manifest)])

    prompt = f"""
You are an AI assistant similar to ChatGPT. 

CONVERSATION DOCUMENTS (IN ORDER):
{inventory}

IMPORTANT:
1. Use the 'DOCUMENT CONTEXT' below to answer questions about these files.
2. If the user mentions "first PDF", "second document", etc., match them to the list above.
3. If 'DOCUMENT CONTEXT' contains snippets labeled '[Document X]', that corresponds to the X-th file in the list above.
4. NO TABLES. NO SEPARATORS. CONVERSATIONAL TONE.

DOCUMENT CONTEXT (EXCERPTS):
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
