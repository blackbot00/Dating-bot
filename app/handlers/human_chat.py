from telegram import Update
from telegram.ext import ContextTypes

from datetime import datetime
import re

from app.handlers.common import banned_guard
from app.keyboard import inchat_kb, choose_again_kb, prev_report_reason_kb
from app.services.user_service import (
    get_user,
    human_can_chat,
    human_increment
)
from app.services.queue_service import add_to_queue, remove_from_queue
from app.services.match_service import (
    try_match,
    create_chat,
    end_chat,
    get_partner,
    is_in_chat
)
from app.services.log_service import log_group2, log_group1
from app.db import reports_col, active_chats_col, users_col
from app.config import GROUP2_ID


LINK_REGEX = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.IGNORECASE)


def partner_info_text(state: str, age: int) -> str:
    return (
        "✅ Partner Matched\n\n"
        f"🔢 Age: {age}\n"
        "👥 Gender: Premium User only\n"
        f"🌍 State: {state}\n\n"
        "🚫 Links are restricted 🥸\n"
        "⏱️ Media sharing unlocked after 2 minutes 🥸"
    )


async def human_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "chat_choice:human":
        user = get_user(uid)

        if not user or not user.get("registered"):
            await q.message.reply_text("❌ Registration incomplete. Use /start")
            return

        if is_in_chat(uid):
            await q.message.reply_text("✅ You are already in chat.", reply_markup=inchat_kb())
            return

        # ✅ DAILY LIMIT CHECK
        allowed, remaining = human_can_chat(uid)
        if not allowed:
            await q.message.reply_text(
                "🚫 *Daily human chat limit reached* (11/day)\n\n"
                "💎 Premium users get unlimited chats.\n"
                "Use /premium",
                parse_mode="Markdown"
            )
            return

        candidate = try_match(user)

        if candidate:
            cid = candidate["_id"]
            remove_from_queue(cid)
            create_chat(uid, cid)

            # ✅ increment only when chat starts
            human_increment(uid)

            partner = get_user(cid)

            await q.message.reply_text(
                partner_info_text(partner.get("state"), partner.get("age")),
                reply_markup=inchat_kb()
            )

            await context.bot.send_message(
                chat_id=cid,
                text=partner_info_text(user.get("state"), user.get("age")),
                reply_markup=inchat_kb()
            )
        else:
            add_to_queue(uid, user["state"], user["gender"], user["age"])
            await q.message.reply_text("🔎 Searching for a human match…")
