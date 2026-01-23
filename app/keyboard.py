from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.constants import STATES, AI_STYLES


def states_kb():
    rows = []
    for i in range(0, len(STATES), 3):
        row = []
        for j in range(i, min(i + 3, len(STATES))):
            row.append(InlineKeyboardButton(STATES[j], callback_data=f"reg_state:{STATES[j]}"))
        rows.append(row)
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
        [InlineKeyboardButton("🤖 AI", callback_data="chat_choice:ai")]
    ])


def choose_again_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚩 Previous chat report", callback_data="prev_report")],
        [InlineKeyboardButton("👤 Human", callback_data="chat_choice:human"),
         InlineKeyboardButton("🤖 AI", callback_data="chat_choice:ai")]
    ])


def prev_report_reason_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Abuse", callback_data="prevrep:abuse")],
        [InlineKeyboardButton("🔞 Adult content", callback_data="prevrep:adult")],
        [InlineKeyboardButton("🧨 Scam / Fraud", callback_data="prevrep:scam")],
        [InlineKeyboardButton("🤢 Harassment", callback_data="prevrep:harass")],
        [InlineKeyboardButton("❌ Cancel", callback_data="prevrep:cancel")]
    ])


def ai_language_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Tamil", callback_data="ai_lang:Tamil"),
         InlineKeyboardButton("English", callback_data="ai_lang:English")],
        [InlineKeyboardButton("Hindi", callback_data="ai_lang:Hindi"),
         InlineKeyboardButton("Telugu", callback_data="ai_lang:Telugu")]
    ])


def ai_style_kb():
    rows = []
    for st in AI_STYLES:
        rows.append([InlineKeyboardButton(st, callback_data=f"ai_style:{st}")])
    return InlineKeyboardMarkup(rows)


def inchat_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Exit", callback_data="chat_action:exit"),
         InlineKeyboardButton("🚩 Report", callback_data="chat_action:report")]
    ])


def ai_exit_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Exit AI Chat", callback_data="ai_action:exit")]
    ])
