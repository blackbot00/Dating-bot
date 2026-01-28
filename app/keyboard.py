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
        [InlineKeyboardButton("Transgender", callback_data=f"{prefix}:Transgender")],
        [InlineKeyboardButton("⬅️ Back", callback_data="edit:back")]
    ])


# =================================================
# MAIN CHAT
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
    ]

    rows.append(
        [InlineKeyboardButton("⭐ Partner Preference", callback_data="edit:preference")]
    )

    return InlineKeyboardMarkup(rows)


# =================================================
# EDIT AGE (6 columns × short height)
# =================================================

def edit_age_kb():
    rows = []
    ages = list(range(11, 81))  # 11–80

    for i in range(0, len(ages), 6):
        row = []
        for age in ages[i:i + 6]:
            row.append(
                InlineKeyboardButton(
                    str(age),
                    callback_data=f"edit_age:{age}"
                )
            )
        rows.append(row)

    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="edit:back")])
    return InlineKeyboardMarkup(rows)


# =================================================
# PARTNER PREFERENCE
# =================================================

def preference_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👩‍❤️‍👨 Gender", callback_data="pref:gender")],
        [InlineKeyboardButton("🎉 Age", callback_data="pref:age")],
        [InlineKeyboardButton("🎲 Random", callback_data="pref:random")],
        [InlineKeyboardButton("⬅️ Back", callback_data="edit:back")]
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
        [InlineKeyboardButton("Hindi", callback_data="ai_lang:Hindi")]
    ])


def ai_style_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(style, callback_data=f"ai_style:{style}")]
        for style in AI_STYLES
    ])


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
