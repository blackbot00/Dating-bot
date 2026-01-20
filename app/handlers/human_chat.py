from telegram import Update
from telegram.ext import ContextTypes
from app.handlers.common import banned_guard
from app.keyboard import inchat_kb, choose_chat_kb
from app.services.user_service import get_user
from app.services.queue_service import add_to_queue, remove_from_queue
from app.services.match_service import try_match, create_chat, end_chat, get_partner, is_in_chat
from app.services.log_service import log_group2, log_group1
from app.db import reports_col
from datetime import datetime

async def human_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return
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

        # Try to match from queue
        candidate = try_match(user)
        if candidate:
            # connect
            cid = candidate["_id"]
            remove_from_queue(cid)

            create_chat(uid, cid)

            partner = get_user(cid)

            await q.message.reply_text(
                f"✅ Connected!\nPartner info:\n📍 {partner.get('state')}\n👤 {partner.get('gender')}\n🎂 {partner.get('age')}",
                reply_markup=inchat_kb()
            )
            await context.bot.send_message(
                chat_id=cid,
                text=f"✅ Connected!\nPartner info:\n📍 {user.get('state')}\n👤 {user.get('gender')}\n🎂 {user.get('age')}",
                reply_markup=inchat_kb()
            )
        else:
            # add to queue
            add_to_queue(uid, user["state"], user["gender"], user["age"])
            await q.message.reply_text("🔎 Searching for a human match…\nPlease wait…")
        return

    if q.data.startswith("chat_action:"):
        action = q.data.split(":", 1)[1]
        if action == "exit":
            chat = end_chat(uid)
            remove_from_queue(uid)

            partner_id = None
            if chat:
                partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]

            await q.message.reply_text("✅ Chat ended.\n\nChoose again:", reply_markup=choose_chat_kb())

            if partner_id:
                await context.bot.send_message(
                    chat_id=partner_id,
                    text="❌ Partner exited. Chat ended.\n\nChoose again:",
                    reply_markup=choose_chat_kb()
                )
            return

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
                    text="🚩 You were reported. Chat ended.\n\nChoose again:",
                    reply_markup=choose_chat_kb()
                )

            await q.message.reply_text("✅ Report submitted. Chat ended.\n\nChoose again:", reply_markup=choose_chat_kb())
            return

async def human_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return

    uid = update.effective_user.id
    partner_id = get_partner(uid)
    if not partner_id:
        return

    text = update.message.text

    # relay
    await context.bot.send_message(chat_id=partner_id, text=text, reply_markup=inchat_kb())

    # log to group2
    await log_group2(
        context.bot,
        f"💬 CHAT LOG\nFrom: {uid}\nTo: {partner_id}\nText: {text}"
          )
