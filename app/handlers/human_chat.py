from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import re

from app.handlers.common import banned_guard
from app.keyboard import inchat_kb, choose_again_kb, prev_report_reason_kb
from app.services.user_service import get_user, human_can_chat, human_increment
from app.services.queue_service import add_to_queue, remove_from_queue
from app.services.match_service import try_match, create_chat, end_chat, is_in_chat
from app.services.log_service import log_group1, log_group2
from app.db import reports_col, active_chats_col, users_col
from app.config import GROUP2_ID


LINK_REGEX = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.IGNORECASE)


# =================================================
# PARTNER INFO
# =================================================

def partner_info_text(state: str, age: int) -> str:
    return (
        "✅ *Partner Matched*\n\n"
        f"🔢 Age: {age}\n"
        "👥 Gender: Hidden\n"
        f"🌍 State: {state}\n\n"
        "🚫 Links are restricted 🥸\n"
        "⏱️ Media sharing unlocked after 2 minutes 🥸"
    )


# =================================================
# CALLBACKS
# =================================================

async def human_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # ---------- START CHAT ----------
    if q.data == "chat_choice:human":
        user = get_user(uid)

        if not user or not user.get("registered"):
            await q.message.reply_text("❌ Complete registration using /start")
            return

        allowed, remaining = human_can_chat(uid)
        if not allowed:
            await q.message.reply_text("🚫 Daily limit reached")
            return

        if is_in_chat(uid):
            await q.message.reply_text("Already in chat", reply_markup=inchat_kb())
            return

        candidate = try_match(user)

        if candidate:
            cid = candidate["_id"]
            remove_from_queue(cid)
            create_chat(uid, cid)
            human_increment(uid)

            partner = get_user(cid)

            await q.message.reply_text(
                partner_info_text(partner["state"], partner["age"]),
                reply_markup=inchat_kb(),
                parse_mode="Markdown"
            )

            await context.bot.send_message(
                chat_id=cid,
                text=partner_info_text(user["state"], user["age"]),
                reply_markup=inchat_kb(),
                parse_mode="Markdown"
            )
        else:
            add_to_queue(uid, user["state"], user["gender"], user["age"])
            await q.message.reply_text("🔎 Searching...")
        return


# =================================================
# TEXT HANDLER  ✅ FINAL FIX
# =================================================

async def human_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    user = get_user(uid)

    # 🔥 DEBUG – MESSAGE RECEIVED
    await log_group2(context.bot, f"📥 MSG RECEIVED from {uid}")

    # ❌ AI chat ignore
    if user and user.get("ai_mode"):
        return

    # 🔥 VERY IMPORTANT FIX (NO status filter)
    chat = active_chats_col.find_one({
        "$or": [{"user1": uid}, {"user2": uid}]
    })

    if not chat:
        await log_group2(context.bot, f"❌ NO ACTIVE CHAT for {uid}")
        return

    partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]
    partner = get_user(partner_id)

    text = (update.message.text or "").strip()
    if not text:
        return

    # 🚫 Link block
    if LINK_REGEX.search(text):
        await update.message.reply_text("🚫 Links are restricted")
        return

    # ✅ SEND
    await context.bot.send_message(chat_id=partner_id, text=text)

    # ✅ GROUP-2 LOG (YOUR FORMAT)
    time_str = datetime.now().strftime("%I:%M %p")
    log_text = (
        f"[{time_str}] "
        f"{user.get('name','User')}({uid}) ➜ "
        f"{partner.get('name','User')}({partner_id})\n"
        f"💬 {text}"
    )
    await log_group2(context.bot, log_text)


# =================================================
# MEDIA
# =================================================

async def human_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return
