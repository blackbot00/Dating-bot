from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL

_client = None  # lazy init


def get_client():
    global _client
    if _client is None:
        if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
            raise ValueError("OPENAI_API_KEY missing or invalid in environment variables.")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def build_system_prompt(language: str, style: str):
    # Tamil => Tanglish mode
    if (language or "").lower() == "tamil":
        lang_instruction = (
            "Speak in Tanglish (Tamil written using English letters). "
            "Example: 'Epdi iruka?', 'Saptiya?', 'Nee romba cute da/di 😄'. "
            "Do NOT use Tamil script letters like 'எ', 'அ' etc."
        )
    else:
        lang_instruction = f"Speak in {language}."

    # Personality tuning
    style_instruction = {
        "Sweet": "Be sweet, cute, and supportive.",
        "Romantic": "Be romantic and emotional, use heart emojis sometimes.",
        "Caring": "Be caring like a best partner, ask about feelings and health.",
        "Possessive": "Be slightly possessive in a playful way (not toxic).",
        "Flirty": "Be flirty, fun, and teasing (not explicit)."
    }.get(style, "Be sweet and supportive.")

    return (
        "You are a romantic GF/BF chatbot.\n"
        f"{lang_instruction}\n"
        f"Personality: {style}.\n"
        f"{style_instruction}\n"
        "Rules:\n"
        "- Keep it clean and respectful.\n"
        "- Avoid explicit sexual content.\n"
        "- Never ask for phone number, address, or personal contact.\n"
        "- Use short natural messages like a real chat.\n"
    )


def ai_reply(user_text: str, language: str, style: str) -> str:
    client = get_client()
    system = build_system_prompt(language, style)

    model = OPENAI_MODEL or "gpt-4o-mini"

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_text}
            ],
            temperature=0.85,
            max_tokens=250
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        # return actual error for debugging (you can hide later)
        return f"❌ AI Error: {e}"
