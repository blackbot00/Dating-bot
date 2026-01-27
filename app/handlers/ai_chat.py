from telegram import Update
from telegram.ext import ContextTypes

from app.keyboard import (
    ai_style_kb,
    ai_language_kb,
    choose_chat_kb
)
from app.services.user_service import (
    set_ai_prefs,
    get_user,
    ai_can_send,
    ai_increment
)
from app.services.premium_service import user_has_premium
from app.openai_client import ai_reply
from app.handlers.common import banned_guard
from app.handlers.ai_commands import ai_is_enabled, start_ai_flow_from_button


# -------------------------------------------------
# CALLBACK HANDLER (BUTTONS)
# -------------------------------------------------

async def ai_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    uid = q.from_user.id

    # stop loading animation
    try:
        await q.answer()
    except:
        pass

    # ---------------- AI START ----------------
    if q.data == "chat_choice:ai":
        ok = await start_ai_flow_from_button(q.message, uid, context)
        if not ok:
            return

        await q.message.reply_text(
            "💬 Choose your language:",
            reply_markup=ai_language_kb()
        )
        return

    # ---------------- LANGUAGE ----------------
    if q.data.startswith("ai_lang:"):
        if not ai_is_enabled():
            await q.message.reply_text(
                "🚫 AI chat is temporarily disabled."
            )
            return

        lang = q.data.split(":", 1)[1]
        set_ai_prefs(uid, lang=lang)

        await q.message.reply_text(
            f"✅ Language set: *{lang}*\n\n💖 Choose AI style:",
            reply_markup=ai_style_kb(),
            parse_mode="Markdown"
        )
        return

    # ---------------- STYLE ----------------
    if q.data.startswith("ai_style:"):
        if not ai_is_enabled():
            await q.message.reply_text(
                "🚫 AI chat is temporarily disabled."
            )
            return

        style = q.data.split(":", 1)[1]
        set_ai_prefs(uid, style=style, ai_mode=True)

        u = get_user(uid) or {}

        await q.message.reply_text(
            "💞 *AI Chat Started*\n\n"
            f"🌐 Language: `{u.get('ai_language')}`\n"
            f"🎭 Style: `{style}`\n\n"
            "Now just message me like a real chat 😌",
            parse_mode="Markdown"
        )
        return

    # ---------------- EXIT AI ----------------
    if q.data == "ai_action:exit":
        set_ai_prefs(uid, ai_mode=False)

        await q.message.reply_text(
            "👋 AI chat closed.\n\nChoose again:",
            reply_markup=choose_chat_kb()
        )
        return


# -------------------------------------------------
# TEXT HANDLER (AI CHAT)
# -------------------------------------------------

async def ai_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    # AI mode OFF → ignore
    if not u or not u.get("ai_mode"):
        return

    # AI disabled by admin
    if not ai_is_enabled():
        await update.message.reply_text(
            "🚫 AI chat is temporarily disabled."
        )
        return

    allowed, remaining = ai_can_send(uid)
    if not allowed:
        await update.message.reply_text(
            "🚫 *Today's free AI limit reached*\n\n"
            "💎 Premium users get unlimited AI chat.\n"
            "Use /premium",
            parse_mode="Markdown"
        )
        return

    user_text = (update.message.text or "").strip()
    if not user_text:
        return

    # typing effect
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
    except:
        pass

    try:
        reply = ai_reply(
            user_text=user_text,
            language=u.get("ai_language") or "English",
            style=u.get("ai_style") or "Sweet",
            user_gender=u.get("gender")
        )
    except Exception as e:
        reply = f"❌ AI Error:\n{e}"

    if not reply.startswith("❌"):
        ai_increment(uid)

    # free limit warning
    if (not user_has_premium(uid)) and remaining != -1 and remaining <= 5:
        reply += f"\n\n⚠️ Free AI left today: {max(remaining - 1, 0)}"

    await update.message.reply_text(reply)
