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
from app.db import reports_col, active_chats_col, users_col
from app.config import GROUP2_ID


LINK_REGEX = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.IGNORECASE)


def partner_info_text(state: str, age: int) -> str:
    return (
        "✅ Partner Matched\n\n"
        f"🔢 Age: {age}\n"
        "👥 Gender: Premium User only\n"
        f"🌍 State: {state}\n\n"
        "🚫 Links are restricted🥸\n"
        "⏱️ Media sharing unlocked after 2 minutes🥸"
    )


def get_active_chat_doc(uid: int):
    return active_chats_col.find_one(
        {"$or": [{"user1": uid}, {"user2": uid}], "status": "active"}
    )


def is_media_unlocked(chat_doc) -> bool:
    try:
        started_at = chat_doc.get("started_at")
        started = datetime.fromisoformat(started_at)
    except:
        return True

    diff = (datetime.utcnow() - started).total_seconds()
    return diff >= 120


def save_last_partner(uid: int, partner_id: int):
    users_col.update_one(
        {"_id": uid},
        {"$set": {"last_partner_id": partner_id, "last_chat_ended_at": datetime.utcnow().isoformat()}}
    )


async def human_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    # ✅ Previous chat report button
    if q.data == "prev_report":
        u = get_user(uid)
        last_partner = u.get("last_partner_id") if u else None
        if not last_partner:
            await q.message.reply_text("❌ No previous chat found to report.")
            return

        await q.message.reply_text("🚩 Report previous chat\n\nSelect reason:", reply_markup=prev_report_reason_kb())
        return

    if q.data.startswith("prevrep:"):
        reason = q.data.split(":", 1)[1]

        if reason == "cancel":
            await q.message.reply_text("✅ Cancelled.", reply_markup=choose_again_kb())
            return

        u = get_user(uid)
        last_partner = u.get("last_partner_id") if u else None
        if not last_partner:
            await q.message.reply_text("❌ No previous chat found.")
            return

        reports_col.insert_one({
            "reporter_id": uid,
            "reported_id": last_partner,
            "chat_id": "previous_chat",
            "reason": reason,
            "created_at": datetime.utcnow().isoformat()
        })

        await log_group1(context.bot, f"🚩 PREVIOUS CHAT REPORT\nReporter: {uid}\nReported: {last_partner}\nReason: {reason}")

        await q.message.reply_text("✅ Report submitted. Thank you!", reply_markup=choose_again_kb())
        return

    # ✅ when user clicks Human
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
                partner_info_text(state=partner.get("state"), age=partner.get("age")),
                reply_markup=inchat_kb()
            )

            await context.bot.send_message(
                chat_id=cid,
                text=partner_info_text(state=user.get("state"), age=user.get("age")),
                reply_markup=inchat_kb()
            )
        else:
            add_to_queue(uid, user["state"], user["gender"], user["age"])
            await q.message.reply_text("🔎 Searching for a human match…\nPlease wait…")

        return

    # ✅ chat actions
    if q.data.startswith("chat_action:"):
        action = q.data.split(":", 1)[1]

        # ✅ Exit
        if action == "exit":
            chat = end_chat(uid)
            remove_from_queue(uid)

            partner_id = None
            if chat:
                partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]

            if partner_id:
                save_last_partner(uid, partner_id)
                save_last_partner(partner_id, uid)

            await q.message.reply_text(
                "✅ Partner left🚶🏼\n\nChoose again:",
                reply_markup=choose_again_kb()
            )

            if partner_id:
                await context.bot.send_message(
                    chat_id=partner_id,
                    text="✅ Partner left🚶🏼\n\nChoose again:",
                    reply_markup=choose_again_kb()
                )
            return

        # ✅ Report current chat
        if action == "report":
            chat = end_chat(uid)
            remove_from_queue(uid)

            partner_id = None
            if chat:
                partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]

            if partner_id:
                save_last_partner(uid, partner_id)
                save_last_partner(partner_id, uid)

                reports_col.insert_one({
                    "reporter_id": uid,
                    "reported_id": partner_id,
                    "chat_id": str(chat["_id"]) if chat else None,
                    "reason": "live_report",
                    "created_at": datetime.utcnow().isoformat()
                })

                await log_group1(
                    context.bot,
                    f"🚩 REPORT\nReporter: {uid}\nReported: {partner_id}\nChat: {chat['_id'] if chat else 'none'}"
                )

                await context.bot.send_message(
                    chat_id=partner_id,
                    text="🚩 You were reported.\n\n✅ Partner left🚶🏼\n\nChoose again:",
                    reply_markup=choose_again_kb()
                )

            await q.message.reply_text(
                "✅ Report received.\n\nChoose again:",
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
        await update.message.reply_text("🚫 Links are restricted🥸")
        await log_group2(context.bot, f"🚫 LINK BLOCKED\nFrom: {uid}\nText: {text}")
        return

    await context.bot.send_message(chat_id=partner_id, text=text)

    await log_group2(
        context.bot,
        f"💬 CHAT LOG\nFrom: {uid}\nTo: {partner_id}\nText: {text}"
    )


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
        await update.message.reply_text("⏱️ Media sharing unlocked after 2 minutes🥸")
        await log_group2(context.bot, f"⏱️ MEDIA BLOCKED\nFrom: {uid}\nTo: {partner_id}")
        return

    try:
        await update.message.copy(chat_id=partner_id)
    except Exception as e:
        await update.message.reply_text("❌ Failed to send media. Try again.")
        await log_group2(context.bot, f"❌ MEDIA RELAY ERROR\nFrom: {uid}\nTo: {partner_id}\nError: {e}")
        return

    try:
        if GROUP2_ID:
            await update.message.copy(chat_id=GROUP2_ID)
    except:
        pass

    await log_group2(context.bot, f"📎 MEDIA LOG\nFrom: {uid}\nTo: {partner_id}")
