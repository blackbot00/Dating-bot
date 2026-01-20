from telegram import Update
from telegram.ext import ContextTypes
from app.services.user_service import ensure_user
from app.db import user_state_col
from app.states import ASK_STATE
from app.keyboard import states_kb, choose_chat_kb
from app.services.log_service import log_group1
from app.handlers.common import banned_guard

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return

    u = update.effective_user
    ensure_user(u.id, u.full_name, u.username)

    # set registration state
    user_state_col.update_one({"_id": u.id}, {"$set": {"step": ASK_STATE, "temp": {}}}, upsert=True)

    await log_group1(context.bot, f"🟢 START\nID: {u.id}\nName: {u.full_name}\nUsername: @{u.username if u.username else 'none'}")

    await update.message.reply_text(
        "👋 Welcome!\n\n✅ Registration start ஆகுது.\n\n📍 Select your State:",
        reply_markup=states_kb()
    )
