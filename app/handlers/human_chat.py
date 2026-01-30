from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import re

from app.handlers.common import banned_guard
from app.keyboard import (
    inchat_kb,
    choose_again_kb,
    prev_report_reason_kb
)
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
# HELPERS
# =================================================

def get_active_chat_doc(uid: int):
    return active_chats_col.find_one(
        {"$or": [{"user1": uid}, {"user2": uid}], "status": "active"}
    )


def is_media_unlocked(chat_doc) -> bool:
    try:
        started = datetime.fromisoformat(chat_doc.get("started_at"))
        return (datetime.utcnow() - started).total_seconds() >= 120
    except:
        return True


def save_last_partner(uid: int, partner_id: int):
    users_col.update_one(
        {"_id": uid},
        {"$set": {
            "last_partner_id": partner_id,
            "last_chat_ended_at": datetime.utcnow().isoformat()
        }}
    )


# =================================================
# CALLBACK HANDLER
# =================================================

async def human_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # ---------- PREVIOUS REPORT ----------
    if q.data == "prev_report":
        u = get_user(uid)
        pid = u.get("last_partner_id") if u else None

        if not pid:
            await q.message.reply_text("❌ No previous chat found.")
            return

        await q.message.reply_text(
            "🚩 *Report previous chat*\n\nSelect reason:",
            reply_markup=prev_report_reason_kb(),
            parse_mode="Markdown"
        )
        return

    if q.data.startswith("prevrep:"):
        reason = q.data.split(":", 1)[1]

        if reason == "cancel":
            await q.message.reply_text(
                "❌ Cancelled.",
                reply_markup=choose_again_kb()
            )
            return

        u = get_user(uid)
        pid = u.get("last_partner_id") if u else None
        if not pid:
            return

        reports_col.insert_one({
            "reporter_id": uid,
            "reported_id": pid,
            "reason": reason,
            "created_at": datetime.utcnow().isoformat()
        })

        await log_group1(
            context.bot,
            f"🚩 PREVIOUS CHAT REPORT\nReporter: {uid}\nReported: {pid}\nReason: {reason}"
        )

        await q.message.reply_text(
            "✅ Report submitted",
            reply_markup=choose_again_kb()
        )
        return

    # ---------- START HUMAN CHAT ----------
    if q.data == "chat_choice:human":
        user = get_user(uid)

        if not user or not user.get("registered"):
            await q.message.reply_text("❌ Complete registration using /start")
            return

        allowed, remaining = human_can_chat(uid)
        if not allowed:
            await q.message.reply_text(
                "🚫 *Daily human chat limit reached*\n\n"
                "💎 Upgrade to Premium",
                parse_mode="Markdown"
            )
            return

        if is_in_chat(uid):
            await q.message.reply_text(
                "💬 You are already chatting",
                reply_markup=inchat_kb()
            )
            return

        candidate = try_match(user)

        if candidate:
            cid = candidate["_id"]

            # ✅ VERY IMPORTANT
            remove_from_queue(uid)
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
            await q.message.reply_text("🔎 Searching for a human match…")

        return

    # ---------- EXIT CHAT ----------
    if q.data.startswith("chat_action:"):
        chat = end_chat(uid)
        remove_from_queue(uid)

        partner_id = None
        if chat:
            partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]

        if partner_id:
            save_last_partner(uid, partner_id)
            save_last_partner(partner_id, uid)

        await q.message.reply_text(
            "✅ Partner left 🚶🏼\n\nChoose again:",
            reply_markup=choose_again_kb()
        )

        if partner_id:
            await context.bot.send_message(
                chat_id=partner_id,
                text="✅ Partner left 🚶🏼\n\nChoose again:",
                reply_markup=choose_again_kb()
            )


# =================================================
# TEXT HANDLER (🔥 FIXED)
# =================================================

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
        await update.message.reply_text("🚫 Links are restricted 🥸")
        return

    # ✅ SEND TO PARTNER
    await context.bot.send_message(
        chat_id=partner_id,
        text=text
    )

    # ✅ GROUP-2 LOG (REQUESTED FORMAT)
    sender = get_user(uid)
    receiver = get_user(partner_id)

    time_str = datetime.now().strftime("%I:%M %p")

    log_text = (
        f"[{time_str}] "
        f"{sender.get('name')}({uid}) ➜ "
        f"{receiver.get('name')}({partner_id})\n"
        f"💬 {text}"
    )

    await log_group2(context.bot, log_text)


# =================================================
# MEDIA HANDLER
# =================================================

async def human_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    partner_id = get_partner(uid)
    if not partner_id:
        return

    chat_doc = get_active_chat_doc(uid)
    if not chat_doc:
        return

    if not is_media_unlocked(chat_doc):
        await update.message.reply_text(
            "⏱️ Media sharing unlocked after 2 minutes 🥸"
        )
        return

    await update.message.copy(chat_id=partner_id)

    if GROUP2_ID:
        await update.message.copy(chat_id=GROUP2_ID)
