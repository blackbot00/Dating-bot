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
    mem = proc.memory_info().rss / (1024 * 1024)

    await update.message.reply_text(
        "📊 *Bot Status*\n\n"
        f"👥 Users: `{user_count}`\n"
        f"🕒 Active chats: `{active_count}`\n"
        f"⌛ Queue: `{queue_count}`\n"
        f"🧠 Bot Memory: `{mem:.1f} MB`\n",
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
    except:
        await update.message.reply_text("❌ Invalid input")
        return

    if not users_col.find_one({"_id": target}):
        await update.message.reply_text("❌ User not found")
        return

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

    # ADMIN CONFIRMATION
    await update.message.reply_text(
        "🎉 Premium Activated!\n\n"
        f"👤 User ID: `{target}`\n"
        f"⏳ Valid till: `{valid_till.date()}`",
        parse_mode="Markdown"
    )

    await log_group1(
        context.bot,
        f"🎁 GIVEAWAY PREMIUM\nUser: {target}\nTill: {valid_till.date()}"
    )


# ---------------- 📢 Broadcast ----------------

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    msg = " ".join(context.args)
    users = users_col.find({}, {"_id": 1})
    sent = 0

    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u["_id"],
                text=f"📢 Broadcast:\n\n{msg}"
            )
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {sent} users")


# ---------------- Ban / Unban / Warn ----------------

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id> [reason]")
        return

    target = int(context.args[0])
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason"

    users_col.update_one({"_id": target}, {"$set": {"is_banned": True}})
    await update.message.reply_text(f"✅ Banned {target}")

    await log_group1(context.bot, f"🚫 BAN\nUser: {target}\nReason: {reason}")


async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return

    target = int(context.args[0])
    users_col.update_one({"_id": target}, {"$set": {"is_banned": False}})
    await update.message.reply_text(f"✅ Unbanned {target}")

    await log_group1(context.bot, f"✅ UNBAN\nUser: {target}")


async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /warn <user_id> <message>")
        return

    target = int(context.args[0])
    msg = " ".join(context.args[1:])

    try:
        await context.bot.send_message(
            chat_id=target,
            text=f"⚠️ Warning from Admin:\n\n{msg}"
        )
    except:
        pass

    await update.message.reply_text(f"✅ Warning sent to {target}")
    await log_group1(context.bot, f"⚠️ WARN\nUser: {target}\nMsg: {msg}")
