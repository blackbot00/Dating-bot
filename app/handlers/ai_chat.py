from telegram import Update
from telegram.ext import ContextTypes

from app.keyboard import ai_style_kb, ai_exit_kb, choose_chat_kb
from app.services.user_service import (
    set_ai_prefs, get_user,
    ai_can_send, ai_increment
)
from app.services.premium_service import user_has_premium
from app.openai_client import ai_reply
from app.handlers.common import banned_guard
from app.handlers.ai_commands import ai_is_enabled, start_ai_flow_from_button


async def ai_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    uid = q.from_user.id

    # ✅ always answer callback (remove loading)
    try:
        await q.answer()
    except:
        pass

    # ✅ DEBUG: print data in logs
    try:
        print("AI CALLBACK:", q.data, "FROM:", uid)
    except:
        pass

    try:
        # ✅ user chooses AI mode
        if q.data == "chat_choice:ai":
            ok = await start_ai_flow_from_button(q.message, uid, context)
            if not ok:
                return
            return

        # ✅ language set
        if q.data.startswith("ai_lang:"):
            if not ai_is_enabled():
                await q.message.reply_text("🚫 AI chat is temporarily disabled. Please try again later.")
                return

            lang = q.data.split(":", 1)[1]
            set_ai_prefs(uid, lang=lang)

            await q.message.reply_text(
                f"✅ Language set: {lang}\n\n💖 Select AI style:",
                reply_markup=ai_style_kb()
            )
            return

        # ✅ style set & enable ai mode
        if q.data.startswith("ai_style:"):
            if not ai_is_enabled():
                await q.message.reply_text("🚫 AI chat is temporarily disabled. Please try again later.")
                return

            style = q.data.split(":", 1)[1]
            set_ai_prefs(uid, style=style, ai_mode=True)

            u = get_user(uid) or {}
            await q.message.reply_text(
                f"✅ AI Mode ON!\nLanguage: {u.get('ai_language')}\nStyle: {style}\n\nNow message me 🥰",
                reply_markup=ai_exit_kb()
            )
            return

        # ✅ exit ai mode
        if q.data == "ai_action:exit":
            set_ai_prefs(uid, ai_mode=False)
            await q.message.reply_text(
                "✅ AI chat exited.\n\nChoose again:",
                reply_markup=choose_chat_kb()
            )
            return

    except Exception as e:
        # ✅ show real error (so no silent fail)
        try:
            await q.message.reply_text(f"❌ AI Callback Error:\n{e}")
        except:
            pass


async def ai_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    # respond only if AI mode ON
    if not u or not u.get("ai_mode"):
        return

    # ✅ admin global AI switch
    if not ai_is_enabled():
        await update.message.reply_text("🚫 AI chat is temporarily disabled. Please try again later.")
        return

    allowed, remaining = ai_can_send(uid)
    if not allowed:
        await update.message.reply_text(
            "🚫 *Today's free AI limit reached* (40/day)\n\n"
            "💎 Premium users get unlimited AI chat.\n"
            "Use /premium",
            parse_mode="Markdown"
        )
        return

    lang = u.get("ai_language") or "English"
    style = u.get("ai_style") or "Sweet"

    user_text = (update.message.text or "").strip()
    if not user_text:
        return

    # typing action
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    except:
        pass

    try:
        reply = ai_reply(user_text, lang, style)
    except Exception as e:
        reply = f"❌ AI Error:\n{e}"

    # increment only if not error
    if not reply.startswith("❌ AI Error"):
        ai_increment(uid)

    # show remaining notice (free users)
    if (not user_has_premium(uid)) and remaining <= 5:
        reply += f"\n\n⚠️ Free AI remaining today: {max(remaining - 1, 0)}/40"

    await update.message.reply_text(reply, reply_markup=ai_exit_kb())
