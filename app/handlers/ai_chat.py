from telegram import Update
from telegram.ext import ContextTypes
from app.db import users_col
from app.keyboard import ai_language_kb, ai_style_kb, ai_exit_kb, choose_chat_kb
from app.services.user_service import set_ai_prefs, get_user
from app.openai_client import ai_reply
from app.handlers.common import banned_guard

async def ai_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "chat_choice:ai":
        await q.message.reply_text("🌐 Select language:", reply_markup=ai_language_kb())
        return

    if q.data.startswith("ai_lang:"):
        lang = q.data.split(":", 1)[1]
        set_ai_prefs(uid, lang=lang)
        await q.message.reply_text(f"✅ Language set: {lang}\n\n💖 Select AI style:", reply_markup=ai_style_kb())
        return

    if q.data.startswith("ai_style:"):
        style = q.data.split(":", 1)[1]
        set_ai_prefs(uid, style=style, ai_mode=True)
        await q.message.reply_text(
            f"✅ AI Mode ON!\nStyle: {style}\n\nNow message me 🥰",
            reply_markup=ai_exit_kb()
        )
        return

    if q.data == "ai_action:exit":
        set_ai_prefs(uid, ai_mode=False)
        await q.message.reply_text("✅ AI chat exited.\n\nChoose again:", reply_markup=choose_chat_kb())
        return

async def ai_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return

    uid = update.effective_user.id
    u = get_user(uid)
    if not u or not u.get("ai_mode"):
        return

    lang = u.get("ai_language") or "English"
    style = u.get("ai_style") or "Sweet"

    user_text = update.message.text.strip()

    try:
        reply = ai_reply(user_text, lang, style)
    except Exception:
        reply = "😔 Sorry! AI temporarily busy. Please try again."

    await update.message.reply_text(reply, reply_markup=ai_exit_kb())
