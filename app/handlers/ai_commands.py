from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.keyboard import ai_language_kb, choose_chat_kb
from app.services.user_service import get_user, set_ai_prefs


async def ai_on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    if not u or not u.get("registered"):
        await update.message.reply_text("❌ First register using /start")
        return

    # force choose language again
    set_ai_prefs(uid, ai_mode=False)
    await update.message.reply_text("🤖 AI Mode ON ✅\n\n🌐 Select language:", reply_markup=ai_language_kb())


async def ai_off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    set_ai_prefs(uid, ai_mode=False)

    await update.message.reply_text("✅ AI Mode OFF", reply_markup=choose_chat_kb())
