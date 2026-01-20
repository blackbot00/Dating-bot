from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

from app.config import BOT_TOKEN
from app.handlers.start import start_cmd
from app.handlers.chat import chat_cmd
from app.handlers.register import reg_callback, reg_age_text
from app.handlers.ai_chat import ai_callbacks, ai_text
from app.handlers.human_chat import human_callbacks, human_text
from app.handlers.admin import about_cmd, broadcast_cmd, ban_cmd, unban_cmd, warn_cmd, premium_on, premium_off

def build_app():
    app = Application.builder().token(BOT_TOKEN).build()

    # user commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("chat", chat_cmd))

    app.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
        "Commands:\n/start - Register\n/chat - Choose Human/AI\n/help\n/privacy\n/premium"
    )))
    app.add_handler(CommandHandler("privacy", lambda u, c: u.message.reply_text(
        "Privacy:\nHuman chats are monitored for safety and abuse prevention.\nDo not share personal details."
    )))
    app.add_handler(CommandHandler("premium", lambda u, c: u.message.reply_text(
        "Premium Plans:\n1 Week - ₹10\n2 Weeks - ₹19\n1 Month - ₹35\n\n(Currently free. Premium can be enabled later.)"
    )))

    # admin commands
    app.add_handler(CommandHandler("about", about_cmd))
    app.add_handler(CommandHandler("premium_on", premium_on))
    app.add_handler(CommandHandler("premium_off", premium_off))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("unban", unban_cmd))
    app.add_handler(CommandHandler("warn", warn_cmd))

    # callbacks
    app.add_handler(CallbackQueryHandler(reg_callback, pattern=r"^reg_"))
    app.add_handler(CallbackQueryHandler(ai_callbacks, pattern=r"^(chat_choice:ai|ai_lang:|ai_style:|ai_action:)"))
    app.add_handler(CallbackQueryHandler(human_callbacks, pattern=r"^(chat_choice:human|chat_action:)"))

    # text handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reg_age_text))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_text))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, human_text))

    return app

def main():
    load_dotenv()
    application = build_app()
    application.run_polling()

if __name__ == "__main__":
    main()
