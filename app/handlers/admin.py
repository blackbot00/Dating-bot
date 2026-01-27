import os
import time
import psutil
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from app.security import is_owner
from app.db import users_col, queue_col, active_chats_col
from app.services.log_service import log_group1

START_TIME = time.time()

ADMIN_ONLY_MSG = "🚫 This command is for Admin only 🥸"


# ---------------- Owner Info ----------------

async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return
    await update.message.reply_text("👑 Owner panel active. Bot running ✅")


# ---------------- Status ----------------

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    user_count = users_col.count_documents({})
    queue_count = queue_col.count_documents({})
    active_count = active_chats_col.count_documents({"status": "active"})

    proc = psutil.Process(os.getpid())
    bot_mem_mb = proc.memory_info().rss / (1024 * 1024)

    cpu_percent = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    ram_used_mb = ram.used / (1024 * 1024)
    ram_total_mb = ram.total / (1024 * 1024)

    uptime_sec = int(time.time() - START_TIME)

    await update.message.reply_text(
        "📊 *Bot Status*\n\n"
        f"👥 Users: `{user_count}`\n"
        f"🕒 Active chats: `{active_count}`\n"
        f"⌛ Queue: `{queue_count}`\n\n"
        f"⚙️ CPU: `{cpu_percent}%`\n"
        f"🧠 RAM: `{ram_used_mb:.1f}/{ram_total_mb:.1f} MB`\n"
        f"🐍 Bot Memory: `{bot_mem_mb:.1f} MB`\n"
        f"⏱ Uptime: `{uptime_sec}s`\n",
        parse_mode="Markdown"
    )


# ---------------- 🎁 GIVEAWAY PREMIUM ----------------

async def giveaway_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    if not context.args:
        await update.message.reply_text("Usage: /giveaway <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return

    user = users_col.find_one({"_id": target_id})
    if not user:
        await update.message.reply_text("❌ User not found")
        return

    # ✅ Activate premium for 7 days
    valid_till = datetime.utcnow() + timedelta(days=7)

    users_col.update_one(
        {"_id": target_id},
        {"$set": {
            "is_premium": True,
            "premium_until": valid_till.isoformat()
        }}
    )

    # 🎉 Message to USER
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "🎉 *Surprise!*\n\n"
                "You got *Premium access* 💎\n"
                f"⏳ Valid till: `{valid_till.date()}`\n\n"
                "✨ Enjoy unlimited AI 🤖 & priority chat 💬"
            ),
            parse_mode="Markdown"
        )
    except:
        pass

    # ✅ Message to ADMIN
    await update.message.reply_text(
        "🎉 Premium Activated!\n\n"
        f"👤 User ID: `{target_id}`\n"
        f"⏳ Valid till: `{valid_till.date()}`",
        parse_mode="Markdown"
    )

    # 📌 Log
    await log_group1(
        context.bot,
        f"🎁 GIVEAWAY PREMIUM\nUser: {target_id}\nValid till: {valid_till.date()}"
    )


# ---------------- Broadcast ----------------

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
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
            await context.bot.send_message(chat_id=u["_id"], text=f"📢 Broadcast:\n\n{msg}")
            sent += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {sent} users")


# ---------------- Ban / Unban / Warn ----------------

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
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
    uid = update.effective_user.id
    if not is_owner(uid):
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
    uid = update.effective_user.id
    if not is_owner(uid):
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
