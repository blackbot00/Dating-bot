import os
import time
import psutil
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from app.security import is_owner
from app.db import users_col, queue_col, active_chats_col
from app.services.log_service import log_group1
from app.services.premium_service import activate_premium

START_TIME = time.time()

ADMIN_ONLY_MSG = "🚫 This command is for Admin only 🥸"


# ---------------- Owner Info ----------------

async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    await update.message.reply_text("👑 Owner panel active. Bot running ✅")


# ---------------- Status ----------------

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    user_count = users_col.count_documents({})
    queue_count = queue_col.count_documents({})
    active_count = active_chats_col.count_documents({"status": "active"})

    proc = psutil.Process(os.getpid())
    mem_mb = proc.memory_info().rss / (1024 * 1024)

    uptime = int(time.time() - START_TIME)

    await update.message.reply_text(
        "📊 *Bot Status*\n\n"
        f"👥 Users: `{user_count}`\n"
        f"🕒 Active chats: `{active_count}`\n"
        f"⌛ Queue: `{queue_count}`\n"
        f"🧠 Bot Memory: `{mem_mb:.1f} MB`\n"
        f"⏱ Uptime: `{uptime}s`\n",
        parse_mode="Markdown"
    )


# ---------------- 🎁 GIVEAWAY PREMIUM ----------------

async def giveaway_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    if not context.args:
        await update.message.reply_text("Usage: /giveaway <user_id> [days]")
        return

    try:
        target = int(context.args[0])
        days = int(context.args[1]) if len(context.args) > 1 else 7
    except ValueError:
        await update.message.reply_text("❌ Invalid user id or days")
        return

    user = users_col.find_one({"_id": target})
    if not user:
        await update.message.reply_text("❌ User not found")
        return

    # ✅ Activate premium
    valid_till = activate_premium(target, days)

    # 🎉 USER MESSAGE
    try:
        await context.bot.send_message(
            chat_id=target,
            text=(
                "🎉 *Surprise!*\n\n"
                "You got *Premium access* 💎\n"
                f"⏳ Valid till: `{valid_till.date()}`\n\n"
                "✨ Enjoy unlimited AI 🤖\n"
                "✨ Enjoy unlimited Human chat 👩‍❤️‍👨"
            ),
            parse_mode="Markdown"
        )
    except:
        pass

    # ✅ ADMIN CONFIRMATION
    await update.message.reply_text(
        "🎉 *Premium Activated!*\n\n"
        f"👤 User ID: `{target}`\n"
        f"⏳ Valid till: `{valid_till.date()}`",
        parse_mode="Markdown"
    )

    # 📌 LOG
    await log_group1(
        context.bot,
        f"🎁 GIVEAWAY PREMIUM\nUser: {target}\nDays: {days}\nTill: {valid_till.date()}"
    )
