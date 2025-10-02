import os
from typing import List

def _get_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=key)
    except Exception:
        return None

def suggest_titles_llm(text: str) -> List[str]:
    client = _get_client()
    if not client:
        return []
    prompt = f"Suggest 5 short, catchy, executive-friendly titles for an internal employee story. Story context:\n{text}\nReturn one title per line, no numbering."
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7,
        )
        content = resp.choices[0].message.content.strip()
        lines = [l.strip("- ").strip() for l in content.splitlines() if l.strip()]
        return lines[:5]
    except Exception:
        return []

def chatbot_answer(prompt: str, context: str) -> str:
    client = _get_client()
    if not client:
        return ""
    sys = "You recommend internal stories to read based on the user's interests. Be concise and friendly."
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":sys},
                {"role":"user","content": f"User question: {prompt}\n\nStory context:\n{context}"}
            ],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""
