from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.constants import STATES, AI_STYLES


def states_kb():
    rows = []
    for i in range(0, len(STATES), 3):
        rows.append([
            InlineKeyboardButton(STATES[j], callback_data=f"reg_state:{STATES[j]}")
            for j in range(i, min(i + 3, len(STATES)))
        ])
    return InlineKeyboardMarkup(rows)


def genders_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Male", callback_data="reg_gender:Male")],
        [InlineKeyboardButton("Female", callback_data="reg_gender:Female")],
        [InlineKeyboardButton("Transgender", callback_data="reg_gender:Transgender")]
    ])


def choose_chat_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Human", callback_data="chat_choice:human")],
        [InlineKeyboardButton("🤖 AI", callback_data="chat_choice:ai")],
        [InlineKeyboardButton("✏️ Edit Profile", callback_data="profile:edit")]
    ])


def choose_again_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚩 Previous chat report", callback_data="prev_report")],
        [
            InlineKeyboardButton("👤 Human", callback_data="chat_choice:human"),
            InlineKeyboardButton("🤖 AI", callback_data="chat_choice:ai")
        ],
        [InlineKeyboardButton("✏️ Edit Profile", callback_data="profile:edit")]
    ])


def prev_report_reason_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Abuse", callback_data="prevrep:abuse")],
        [InlineKeyboardButton("🔞 Adult content", callback_data="prevrep:adult")],
        [InlineKeyboardButton("🧨 Scam / Fraud", callback_data="prevrep:scam")],
        [InlineKeyboardButton("🤢 Harassment", callback_data="prevrep:harass")],
        [InlineKeyboardButton("❌ Cancel", callback_data="prevrep:cancel")]
    ])


def inchat_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Exit", callback_data="chat_action:exit"),
            InlineKeyboardButton("🚩 Report", callback_data="chat_action:report")
        ]
    ])
