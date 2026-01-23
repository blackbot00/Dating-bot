from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.keyboard import inchat_kb, choose_again_kb
from app.services.user_service import get_user
from app.services.queue_service import add_to_queue, remove_from_queue
from app.services.match_service import try_match, create_chat, end_chat, get_partner, is_in_chat
from app.services.log_service import log_group2, log_group1
from app.db import reports_col
from datetime import datetime


def partner_info_text(state: str, age: int) -> str:
    return (
        "✅ Partner Matched\n\n"
        f"🔢 Age: {age}\n"
        "👥 Gender: Premium User only\n"
        f"🌍 State: {state}\n\n"
        "🚫 Links are restricted🥸\n"
        "⏱️ Media sharing unlocked after 2 minutes🥸"
    )


async def human_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

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

            # ✅ show partner matched
            await q.message.reply_text(
                partner_info_text(
                    state=partner.get("state"),
                    age=partner.get("age")
                ),
                reply_markup=inchat_kb()
            )

            await context.bot.send_message(
                chat_id=cid,
                text=partner_info_text(
                    state=user.get("state"),
                    age=user.get("age")
                ),
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

        # ✅ Report
        if action == "report":
            chat = end_chat(uid)
            remove_from_queue(uid)

            partner_id = None
            if chat:
                partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]

            if partner_id:
                reports_col.insert_one({
                    "reporter_id": uid,
                    "reported_id": partner_id,
                    "chat_id": str(chat["_id"]) if chat else None,
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

    text = update.message.text

    # ✅ relay WITHOUT buttons
    await context.bot.send_message(chat_id=partner_id, text=text)

    # log to group2
    await log_group2(
        context.bot,
        f"💬 CHAT LOG\nFrom: {uid}\nTo: {partner_id}\nText: {text}"
            )
