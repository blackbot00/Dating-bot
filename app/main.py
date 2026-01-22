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
from app.handlers.human_chat import human_callbacks
from app.handlers.admin import (
    about_cmd, broadcast_cmd, ban_cmd, unban_cmd, warn_cmd,
    premium_on, premium_off, status_cmd
)
from app.handlers.ai_commands import ai_on_cmd, ai_off_cmd
from app.handlers.router import text_router


def build_bot():
    bot = Application.builder().token(BOT_TOKEN).build()

    # user commands
    bot.add_handler(CommandHandler("start", start_cmd))
    bot.add_handler(CommandHandler("chat", chat_cmd))
    bot.add_handler(CommandHandler("ai_on", ai_on_cmd))
    bot.add_handler(CommandHandler("ai_off", ai_off_cmd))

    bot.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
        "Commands:\n/start - Register\n/chat - Choose Human/AI\n/ai_on - AI Mode ON\n/ai_off - AI Mode OFF\n/help\n/privacy\n/premium"
    )))

    bot.add_handler(CommandHandler("privacy", lambda u, c: u.message.reply_text(
        "🔐 *Privacy Policy*\n\n"
        "1️⃣ 🛡️ *Safety first* — Abuse / illegal chat இருந்தால் action எடுக்கப்படும்.\n"
        "2️⃣ 👀 *Monitoring* — Human chat messages safety purpose-க்கு monitor/log செய்யப்படும்.\n"
        "3️⃣ 🚫 *No personal info* — Phone, address, OTP share பண்ணாதீங்க.\n"
        "4️⃣ 🚩 *Report option* — Problem இருந்தா Report press பண்ணுங்க.\n"
        "5️⃣ 🔒 *Data use* — Registration info match purpose-க்கு மட்டும் use.\n",
        parse_mode="Markdown"
    )))

    bot.add_handler(CommandHandler("premium", lambda u, c: u.message.reply_text(
        "💎 Premium Plans:\n"
        "1 Week - ₹10\n"
        "2 Weeks - ₹19\n"
        "1 Month - ₹35\n\n"
        "✅ Premium benefits:\n"
        "- Unlimited AI chat\n"
        "- Priority human matching\n"
    )))

    # admin commands
    bot.add_handler(CommandHandler("about", about_cmd))
    bot.add_handler(CommandHandler("status", status_cmd))
    bot.add_handler(CommandHandler("premium_on", premium_on))
    bot.add_handler(CommandHandler("premium_off", premium_off))
    bot.add_handler(CommandHandler("broadcast", broadcast_cmd))
    bot.add_handler(CommandHandler("ban", ban_cmd))
    bot.add_handler(CommandHandler("unban", unban_cmd))
    bot.add_handler(CommandHandler("warn", warn_cmd))

    # callbacks (buttons)
    bot.add_handler(CallbackQueryHandler(reg_callback, pattern=r"^reg_"))
    bot.add_handler(CallbackQueryHandler(ai_callbacks, pattern=r"^(chat_choice:ai|ai_lang:|ai_style:|ai_action:)"))
    bot.add_handler(CallbackQueryHandler(human_callbacks, pattern=r"^(chat_choice:human|chat_action:)"))

    # ✅ ONE AND ONLY text handler (router decides)
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    return bot


def run_flask():
    port = int(os.environ.get("PORT", "8000"))
    flask_app.run(host="0.0.0.0", port=port)


def main():
    load_dotenv()

    # start web server in separate thread (koyeb health check)
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    # start telegram bot polling
    bot = build_bot()
    bot.run_polling()


if __name__ == "__main__":
    main()
