from telegram import Update
from telegram.ext import ContextTypes
from app.keyboard import choose_chat_kb
from app.handlers.common import banned_guard

async def chat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return
    await update.message.reply_text("💬 Choose chat mode:", reply_markup=choose_chat_kb())
