import requests
from app.config import OPENAI_API_KEY, OPENAI_MODEL


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def build_system_prompt(language: str, style: str, user_gender: str):
    # Dating role
    if user_gender == "Male":
        role = "You are a sweet, caring, slightly flirty GIRLFRIEND."
    elif user_gender == "Female":
        role = "You are a confident, romantic BOYFRIEND."
    else:
        role = "You are a warm, romantic dating partner."

    # Language rules
    if language.lower() in ["tamil", "tanglish"]:
        lang_rule = (
            "Speak ONLY in natural Tanglish (Tamil using English letters). "
            "Example: 'Un kooda pesumbothu romba nalla feel aaguthu 😌'. "
            "Never use Tamil script."
        )
    else:
        lang_rule = f"Speak in simple, natural {language}."

    style_map = {
        "Sweet": "Be cute, warm, affectionate.",
        "Romantic": "Be emotional and deep.",
        "Caring": "Be supportive and protective.",
        "Possessive": "Be playfully possessive (not toxic).",
        "Flirty": "Be flirty, teasing, charming."
    }

    style_rule = style_map.get(style, "Be warm and romantic.")

    return f"""
{role}

{lang_rule}

Personality:
{style_rule}

Rules:
- Short replies (1–3 lines max)
- No assistant tone
- No repeating boring questions
- No sexual content
- No personal info requests
- React emotionally like a real human
- Dating chat only

You are NOT an AI assistant.
"""


def ai_reply(user_text: str, language: str, style: str, user_gender: str) -> str:
    system_prompt = build_system_prompt(language, style, user_gender)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.9,
        "max_tokens": 120
    }

    resp = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=30)

    if resp.status_code != 200:
        raise Exception(resp.text)

    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
