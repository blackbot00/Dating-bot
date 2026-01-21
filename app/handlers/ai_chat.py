from telegram import Update
from telegram.ext import ContextTypes

from app.keyboard import ai_language_kb, ai_style_kb, ai_exit_kb, choose_chat_kb
from app.services.user_service import set_ai_prefs, get_user
from app.openai_client import ai_reply
from app.handlers.common import banned_guard


async def ai_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # user chooses AI mode
    if q.data == "chat_choice:ai":
        await q.message.reply_text("🌐 Select language:", reply_markup=ai_language_kb())
        return

    # language set
    if q.data.startswith("ai_lang:"):
        lang = q.data.split(":", 1)[1]
        set_ai_prefs(uid, lang=lang)

        await q.message.reply_text(
            f"✅ Language set: {lang}\n\n💖 Select AI style:",
            reply_markup=ai_style_kb()
        )
        return

    # style set & enable ai mode
    if q.data.startswith("ai_style:"):
        style = q.data.split(":", 1)[1]
        set_ai_prefs(uid, style=style, ai_mode=True)

        await q.message.reply_text(
            f"✅ AI Mode ON!\nLanguage: {get_user(uid).get('ai_language')}\nStyle: {style}\n\nNow message me 🥰",
            reply_markup=ai_exit_kb()
        )
        return

    # exit ai mode
    if q.data == "ai_action:exit":
        set_ai_prefs(uid, ai_mode=False)
        await q.message.reply_text(
            "✅ AI chat exited.\n\nChoose again:",
            reply_markup=choose_chat_kb()
        )
        return


async def ai_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    # only respond if AI mode ON
    if not u or not u.get("ai_mode"):
        return

    lang = u.get("ai_language") or "English"
    style = u.get("ai_style") or "Sweet"

    user_text = (update.message.text or "").strip()
    if not user_text:
        return

    # Optional: show typing...
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    except:
        pass

    try:
        reply = ai_reply(user_text, lang, style)
    except Exception as e:
        # ✅ VERY IMPORTANT: show real error for debugging
        reply = f"❌ AI Error:\n{e}"

    await update.message.reply_text(reply, reply_markup=ai_exit_kb())
