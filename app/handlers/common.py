from telegram import Update
from telegram.ext import ContextTypes
from app.security import is_banned

async def banned_guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    uid = update.effective_user.id
    if is_banned(uid):
        if update.message:
            await update.message.reply_text("🚫 You are banned from using this bot.")
        elif update.callback_query:
            await update.callback_query.answer("Banned.", show_alert=True)
        return True
    return False
