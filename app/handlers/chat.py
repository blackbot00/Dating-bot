from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.keyboard import choose_chat_kb, inchat_kb
from app.services.user_service import get_user
from app.services.match_service import is_in_chat


async def chat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 🚫 Banned user guard
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    # ❌ Not registered
    if not u or not u.get("registered"):
        await update.message.reply_text(
            "❌ You are not registered yet.\nUse /start to complete registration."
        )
        return

    # 👤 Already in human chat
    if is_in_chat(uid):
        await update.message.reply_text(
            "💬 You are already chatting with a partner.",
            reply_markup=inchat_kb()
        )
        return

    # 🤖 AI mode already ON
    if u.get("ai_mode"):
        await update.message.reply_text(
            "🤖 AI chat is already active.\nJust send a message 💕"
        )
        return

    # ✅ Normal flow → choose mode
    await update.message.reply_text(
        "💬 Choose chat mode:",
        reply_markup=choose_chat_kb()
        )
