import os
import threading
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from app.config import BOT_TOKEN
from app.web_server import app as flask_app

from app.handlers.start import start_cmd
from app.handlers.chat import chat_cmd
from app.handlers.register import reg_callback
from app.handlers.ai_chat import ai_callbacks
from app.handlers.human_chat import human_callbacks, human_media
from app.handlers.admin import (
    about_cmd, broadcast_cmd, ban_cmd, unban_cmd, warn_cmd,
    premium_on, premium_off, status_cmd
)
from app.handlers.ai_commands import ai_enable_cmd, ai_disable_cmd
from app.handlers.router import text_router
from app.handlers.exit_cmd import exit_cmd
from app.handlers.profile import edit_profile_cmd


def build_bot():
    bot = Application.builder().token(BOT_TOKEN).build()

    # ✅ User commands
    bot.add_handler(CommandHandler("start", start_cmd))
    bot.add_handler(CommandHandler("chat", chat_cmd))
    bot.add_handler(CommandHandler("exit", exit_cmd))
    bot.add_handler(CommandHandler("edit_profile", edit_profile_cmd))

    bot.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
        "📌 Commands:\n\n"
        "✅ /start - Register / Open Menu\n"
        "💬 /chat - Choose Human / AI\n"
        "🛑 /exit - Stop conversation\n"
        "📝 /edit_profile - Re-register profile\n"
        "🔐 /privacy - Privacy Policy\n"
        "💎 /premium - Premium Plans\n"
        "❓ /help - Help Menu"
    )))

    # ✅ Privacy
    bot.add_handler(CommandHandler("privacy", lambda u, c: u.message.reply_text(
        "🔐 *Privacy Policy*\n\n"
        "1️⃣ 🛡️ *Safety First* — We take user safety seriously.\n"
        "2️⃣ 😇 *Don't be Misbehave* — Respect others and chat politely.\n"
        "3️⃣ 🚫 *No Personal Info* — Never share phone, OTP, address, bank details.\n"
        "4️⃣ 🚩 *Report Option* — Use Report button if someone abuses.\n"
        "5️⃣ 🔒 *Data Use* — Registration info (state/gender/age) used only for matching.\n",
        parse_mode="Markdown"
    )))

    # ✅ Premium
    bot.add_handler(CommandHandler("premium", lambda u, c: u.message.reply_text(
        "💎 *Premium Plans*\n\n"
        "🗓️ 1 Week  — ₹10\n"
        "🗓️ 2 Weeks — ₹19\n"
        "🗓️ 1 Month — ₹35\n\n"
        "✨ *Premium Benefits*\n"
        "🤖 Unlimited AI Chat\n"
        "⚡ Priority Human Matching\n"
        "🛡️ Safer & Faster Experience\n\n"
        "📌 *Note:* Premium will be enabled soon.\n",
        parse_mode="Markdown"
    )))

    # ✅ Admin commands
    bot.add_handler(CommandHandler("about", about_cmd))
    bot.add_handler(CommandHandler("status", status_cmd))
    bot.add_handler(CommandHandler("premium_on", premium_on))
    bot.add_handler(CommandHandler("premium_off", premium_off))
    bot.add_handler(CommandHandler("broadcast", broadcast_cmd))
    bot.add_handler(CommandHandler("ban", ban_cmd))
    bot.add_handler(CommandHandler("unban", unban_cmd))
    bot.add_handler(CommandHandler("warn", warn_cmd))

    # ✅ AI admin control
    bot.add_handler(CommandHandler("ai_enable", ai_enable_cmd))
    bot.add_handler(CommandHandler("ai_disable", ai_disable_cmd))

    # ✅ Callbacks (IMPORTANT FIX ✅)
    # registration callbacks pattern மட்டும் வைத்துக்கோ
    bot.add_handler(CallbackQueryHandler(reg_callback, pattern=r"^reg_"))

    # AI & Human callbacks pattern remove -> ALWAYS catch buttons
    bot.add_handler(CallbackQueryHandler(ai_callbacks))
    bot.add_handler(CallbackQueryHandler(human_callbacks))

    # ✅ Media handler
    bot.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO | filters.VOICE |
         filters.VIDEO_NOTE | filters.Sticker.ALL | filters.ANIMATION),
        human_media
    ))

    # ✅ Text router
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    return bot


def run_flask():
    port = int(os.environ.get("PORT", "8000"))
    flask_app.run(host="0.0.0.0", port=port)


def main():
    load_dotenv()

    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    bot = build_bot()
    bot.run_polling()


if __name__ == "__main__":
    main()
