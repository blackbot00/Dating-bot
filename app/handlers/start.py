from telegram import Update
from telegram.ext import ContextTypes

from app.services.user_service import ensure_user, get_user
from app.db import user_state_col
from app.states import ASK_STATE
from app.keyboard import states_kb, choose_chat_kb
from app.services.log_service import log_group1
from app.handlers.common import banned_guard


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    tg_user = update.effective_user
    ensure_user(tg_user.id, tg_user.full_name, tg_user.username)

    u = get_user(tg_user.id)

    # ✅ Already registered -> show chat options
    if u and u.get("registered"):
        await update.message.reply_text(
            "✅ Welcome back!\n\n💬 Choose chat mode:",
            reply_markup=choose_chat_kb()
        )
        return

    # ✅ Only first-time start log
    await log_group1(
        context.bot,
        f"🟢 FIRST START\nID: {tg_user.id}\nName: {tg_user.full_name}\nUsername: @{tg_user.username if tg_user.username else 'none'}"
    )

    # start registration
    user_state_col.update_one(
        {"_id": tg_user.id},
        {"$set": {"step": ASK_STATE, "temp": {}}},
        upsert=True
    )

    await update.message.reply_text(
        "👋 Welcome!\n\n✅ Registration start ஆகுது.\n\n📍 Select your State:",
        reply_markup=states_kb()
    )
