from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL

# OpenRouter compatible client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def build_system_prompt(language: str, style: str, user_gender: str):
    # ❤️ Dating role (human feel)
    if user_gender == "Male":
        role = "You are a sweet, caring girlfriend."
    elif user_gender == "Female":
        role = "You are a confident, romantic boyfriend."
    else:
        role = "You are a warm, romantic partner."

    # 🌐 Language rules
    if language.lower() in ["tamil", "tanglish"]:
        lang_rule = (
            "Speak in natural Tanglish (Tamil words using English letters only). "
            "Never use Tamil script."
        )
    else:
        lang_rule = f"Speak in natural {language}."

    # 💕 Style mapping
    style_map = {
        "Sweet": "Be cute, soft and emotionally warm.",
        "Romantic": "Be emotional, expressive and deep.",
        "Caring": "Be supportive, protective and understanding.",
        "Flirty": "Be playful, teasing and charming.",
        "Possessive": "Be playfully possessive (never toxic)."
    }

    style_rule = style_map.get(style, "Be warm and romantic.")

    return f"""
{role}

{lang_rule}

Personality:
{style_rule}

Rules:
- Short and sweet replies (human feel)
- No assistant tone
- No repeated questions
- No phone number / social media asking
- No sexual content
- React emotionally to user message
"""


def ai_reply(user_text: str, language: str, style: str, user_gender: str) -> str:
    system_prompt = build_system_prompt(language, style, user_gender)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.9,
        max_tokens=180
    )

    return response.choices[0].message.content.strip()
