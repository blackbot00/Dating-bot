from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.constants import STATES, AI_STYLES


# =================================================
# REGISTRATION
# =================================================

def states_kb(edit: bool = False):
    prefix = "edit_state" if edit else "reg_state"

    rows = []
    for i in range(0, len(STATES), 3):
        row = []
        for j in range(i, min(i + 3, len(STATES))):
            row.append(
                InlineKeyboardButton(
                    STATES[j],
                    callback_data=f"{prefix}:{STATES[j]}"
                )
            )
        rows.append(row)

    return InlineKeyboardMarkup(rows)


def genders_kb(edit: bool = False):
    prefix = "edit_gender" if edit else "reg_gender"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Male", callback_data=f"{prefix}:Male")],
        [InlineKeyboardButton("Female", callback_data=f"{prefix}:Female")],
        [InlineKeyboardButton("Transgender", callback_data=f"{prefix}:Transgender")]
    ])


# =================================================
# MAIN CHAT MENU
# =================================================

def choose_chat_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Human", callback_data="chat_choice:human")],
        [InlineKeyboardButton("🤖 AI", callback_data="chat_choice:ai")]
    ])


def choose_again_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚩 Previous chat report", callback_data="prev_report")],
        [
            InlineKeyboardButton("👤 Human", callback_data="chat_choice:human"),
            InlineKeyboardButton("🤖 AI", callback_data="chat_choice:ai")
        ]
    ])


# =================================================
# PROFILE EDIT
# =================================================

def edit_profile_kb(is_premium: bool):
    rows = [
        [InlineKeyboardButton("👤 Edit Gender", callback_data="edit:gender")],
        [InlineKeyboardButton("🎂 Edit Age", callback_data="edit:age")],
        [InlineKeyboardButton("🌍 Edit State", callback_data="edit:state")],
        [InlineKeyboardButton("⭐ Partner Preference", callback_data="edit:preference")]
    ]
    return InlineKeyboardMarkup(rows)


def edit_age_kb():
    rows = []

    col1 = list(range(11, 81))
    col2 = list(range(21, 91))

    for a, b in zip(col1, col2):
        if b > 80:
            rows.append([
                InlineKeyboardButton(str(a), callback_data=f"edit_age:{a}")
            ])
        else:
            rows.append([
                InlineKeyboardButton(str(a), callback_data=f"edit_age:{a}"),
                InlineKeyboardButton(str(b), callback_data=f"edit_age:{b}")
            ])

    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="edit:back")])
    return InlineKeyboardMarkup(rows)


def preference_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👩‍❤️‍👨 Gender", callback_data="pref:gender")],
        [InlineKeyboardButton("🎉 Age", callback_data="pref:age")],
        [InlineKeyboardButton("🎲 Random", callback_data="pref:random")],
        [InlineKeyboardButton("⬅️ Back", callback_data="edit:back")]
    ])


# =================================================
# PREVIOUS CHAT REPORT
# =================================================

def prev_report_reason_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Abuse", callback_data="prevrep:abuse")],
        [InlineKeyboardButton("🔞 Adult content", callback_data="prevrep:adult")],
        [InlineKeyboardButton("🧨 Scam / Fraud", callback_data="prevrep:scam")],
        [InlineKeyboardButton("🤢 Harassment", callback_data="prevrep:harass")],
        [InlineKeyboardButton("❌ Cancel", callback_data="prevrep:cancel")]
    ])


# =================================================
# AI CHAT
# =================================================

def ai_language_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Tamil", callback_data="ai_lang:Tamil"),
            InlineKeyboardButton("Tanglish", callback_data="ai_lang:Tanglish")
        ],
        [
            InlineKeyboardButton("English", callback_data="ai_lang:English"),
            InlineKeyboardButton("Telugu", callback_data="ai_lang:Telugu")
        ],
        [
            InlineKeyboardButton("Hindi", callback_data="ai_lang:Hindi")
        ]
    ])


def ai_style_kb():
    rows = []
    for style in AI_STYLES:
        rows.append(
            [InlineKeyboardButton(style, callback_data=f"ai_style:{style}")]
        )
    return InlineKeyboardMarkup(rows)


def ai_exit_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Exit AI Chat", callback_data="ai_action:exit")]
    ])


# =================================================
# HUMAN CHAT
# =================================================

def inchat_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Exit", callback_data="chat_action:exit"),
            InlineKeyboardButton("🚩 Report", callback_data="chat_action:report")
        ]
    ])
