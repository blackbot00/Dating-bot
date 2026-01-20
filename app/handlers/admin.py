from telegram import Update
from telegram.ext import ContextTypes
from app.security import is_owner
from app.db import users_col
from app.services.premium_service import set_premium_enabled
from app.services.log_service import log_group1

async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        return
    await update.message.reply_text("👑 Owner panel active. Bot running ✅")

async def premium_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        return
    set_premium_enabled(True)
    await update.message.reply_text("✅ Premium Enabled")
    await log_group1(context.bot, "⚙️ Premium Enabled by Owner")

async def premium_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
        return
    set_premium_enabled(False)
    await update.message.reply_text("✅ Premium Disabled")
    await log_group1(context.bot, "⚙️ Premium Disabled by Owner")

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
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

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_owner(uid):
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
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /warn <user_id> <message>")
        return

    target = int(context.args[0])
    msg = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=target, text=f"⚠️ Warning from Admin:\n\n{msg}")
    except:
        pass

    await update.message.reply_text(f"✅ Warning sent to {target}")
    await log_group1(context.bot, f"⚠️ WARN\nUser: {target}\nMsg: {msg}")
