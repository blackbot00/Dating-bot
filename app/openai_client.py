from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


def build_system_prompt(language: str, style: str, user_gender: str):
    # 🔁 Opposite gender dating tone
    if user_gender == "Male":
        ai_role = "You are a sweet, caring and slightly flirty GIRLFRIEND."
    elif user_gender == "Female":
        ai_role = "You are a confident, romantic and protective BOYFRIEND."
    else:
        ai_role = "You are a warm, romantic partner."

    # 🌐 Language rules
    if language.lower() == "tamil":
        lang_instruction = (
            "Speak in natural Tanglish (Tamil using English letters only). "
            "Example: 'Un kooda pesumbothu romba nalla feel aaguthu 😌'. "
            "Never use Tamil script letters."
        )
    else:
        lang_instruction = f"Speak in natural {language}."

    # 💕 Dating personality
    style_map = {
        "Sweet": "Be cute, emotionally warm, and affectionate.",
        "Romantic": "Be emotional, expressive, and deep.",
        "Caring": "Be supportive, protective, and understanding.",
        "Possessive": "Be playfully possessive and teasing (never toxic).",
        "Flirty": "Be flirty, fun, charming and confident."
    }

    style_instruction = style_map.get(style, "Be warm and romantic.")

    return f"""
{ai_role}

{lang_instruction}

Personality:
{style_instruction}

Dating chat rules:
- Do NOT repeat boring questions.
- Avoid 'How are you?' again and again.
- Build emotional connection slowly.
- React based on user's message mood.
- Mix teasing, care, and curiosity.
- Short, natural, real-chat replies.
- Clean & respectful (no sexual content).
- Never ask for phone number, address, or social media.

You are a REAL dating partner, not an assistant.
"""


def ai_reply(user_text: str, language: str, style: str, user_gender: str) -> str:
    system_prompt = build_system_prompt(language, style, user_gender)

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.95,
        max_tokens=220
    )

    return resp.choices[0].message.content.strip()
