from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import re

from app.handlers.common import banned_guard
from app.keyboard import inchat_kb, choose_again_kb, prev_report_reason_kb
from app.services.user_service import get_user
from app.services.queue_service import add_to_queue, remove_from_queue
from app.services.match_service import try_match, create_chat, end_chat, get_partner, is_in_chat
from app.services.log_service import log_group2, log_group1
from app.services.premium_service import user_has_premium
from app.db import reports_col, active_chats_col, users_col

LINK_REGEX = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.IGNORECASE)


def partner_info_text(user, partner):
    text = (
        "✅ Partner Matched\n\n"
        f"🔢 Age: {partner.get('age')}\n"
        f"🌍 State: {partner.get('state')}\n\n"
        "🚫 Links are restricted\n"
        "⏱️ Media sharing unlocked after 2 minutes"
    )

    if user_has_premium(user["_id"]):
        text += f"\n👤 Gender: {partner.get('gender')}"

    return text


async def human_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # ✅ Human chat start
    if q.data == "chat_choice:human":
        user = get_user(uid)

        if not user or not user.get("registered"):
            await q.message.reply_text("❌ Registration incomplete. Use /start")
            return

        if is_in_chat(uid):
            await q.message.reply_text("✅ You are already in chat.", reply_markup=inchat_kb())
            return

        candidate = try_match(user)

        if candidate:
            cid = candidate["_id"]
            remove_from_queue(cid)
            create_chat(uid, cid)

            partner = get_user(cid)

            await q.message.reply_text(
                partner_info_text(user, partner),
                reply_markup=inchat_kb()
            )

            await context.bot.send_message(
                chat_id=cid,
                text=partner_info_text(partner, user),
                reply_markup=inchat_kb()
            )

            await log_group1(
                context.bot,
                f"🤝 MATCH\nUser: {uid}\nPartner: {cid}\nPremium: {user_has_premium(uid)}"
            )
        else:
            add_to_queue(uid, user["state"], user["gender"], user["age"])
            await q.message.reply_text("🔎 Searching for a human match…")

        return

    # ✅ Exit chat
    if q.data == "chat_action:exit":
        chat = end_chat(uid)
        remove_from_queue(uid)

        partner_id = None
        if chat:
            partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]

        await q.message.reply_text("✅ Partner left\n\nChoose again:", reply_markup=choose_again_kb())

        if partner_id:
            await context.bot.send_message(
                chat_id=partner_id,
                text="✅ Partner left\n\nChoose again:",
                reply_markup=choose_again_kb()
            )
        return


async def human_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    partner_id = get_partner(uid)
    if not partner_id:
        return

    text = (update.message.text or "").strip()
    if not text:
        return

    if LINK_REGEX.search(text):
        await update.message.reply_text("🚫 Links are restricted")
        return

    await context.bot.send_message(chat_id=partner_id, text=text)

    await log_group2(
        context.bot,
        f"💬 CHAT\nFrom: {uid}\nTo: {partner_id}\nText: {text}"
            )
