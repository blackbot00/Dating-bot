import os
import threading
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from app.config import BOT_TOKEN
from app.web_server import app as flask_app

from app.handlers.start import start_cmd
from app.handlers.chat import chat_cmd
from app.handlers.register import reg_callback, reg_age_text
from app.handlers.ai_chat import ai_callbacks, ai_text
from app.handlers.human_chat import human_callbacks, human_text
from app.handlers.admin import about_cmd, broadcast_cmd, ban_cmd, unban_cmd, warn_cmd, premium_on, premium_off


def build_bot():
    bot = Application.builder().token(BOT_TOKEN).build()

    bot.add_handler(CommandHandler("start", start_cmd))
    bot.add_handler(CommandHandler("chat", chat_cmd))

    bot.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
        "Commands:\n/start - Register\n/chat - Choose Human/AI\n/help\n/privacy\n/premium"
    )))
    bot.add_handler(CommandHandler("privacy", lambda u, c: u.message.reply_text(
        "Privacy:\nHuman chats are monitored for safety.\nDo not share personal info."
    )))
    bot.add_handler(CommandHandler("premium", lambda u, c: u.message.reply_text(
        "Premium Plans:\n1 Week - ₹10\n2 Weeks - ₹19\n1 Month - ₹35\n\n(Currently free.)"
    )))

    # admin
    bot.add_handler(CommandHandler("about", about_cmd))
    bot.add_handler(CommandHandler("premium_on", premium_on))
    bot.add_handler(CommandHandler("premium_off", premium_off))
    bot.add_handler(CommandHandler("broadcast", broadcast_cmd))
    bot.add_handler(CommandHandler("ban", ban_cmd))
    bot.add_handler(CommandHandler("unban", unban_cmd))
    bot.add_handler(CommandHandler("warn", warn_cmd))

    # callbacks
    bot.add_handler(CallbackQueryHandler(reg_callback, pattern=r"^reg_"))
    bot.add_handler(CallbackQueryHandler(ai_callbacks, pattern=r"^(chat_choice:ai|ai_lang:|ai_style:|ai_action:)"))
    bot.add_handler(CallbackQueryHandler(human_callbacks, pattern=r"^(chat_choice:human|chat_action:)"))

    # text
    from app.handlers.router import text_router
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    return bot


def run_flask():
    port = int(os.environ.get("PORT", "8000"))
    flask_app.run(host="0.0.0.0", port=port)


def main():
    load_dotenv()

    # start web server in separate thread
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    # start telegram bot polling
    bot = build_bot()
    bot.run_polling()


if __name__ == "__main__":
    main()
