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

# ---------------- HANDLERS ----------------
from app.handlers.start import start_cmd
from app.handlers.chat import chat_cmd
from app.handlers.exit_cmd import exit_cmd

from app.handlers.register import reg_callback, reg_age_text
from app.handlers.profile import edit_profile_cmd, profile_callbacks

from app.handlers.human_chat import (
    human_callbacks,
    human_text,
    human_media
)

from app.handlers.ai_chat import (
    ai_callbacks,
    ai_text
)

from app.handlers.admin import (
    about_cmd,
    broadcast_cmd,
    ban_cmd,
    unban_cmd,
    warn_cmd,
    status_cmd,
    giveaway_cmd
)

from app.handlers.ai_commands import ai_enable_cmd, ai_disable_cmd
from app.handlers.router import text_router


# =================================================
# BUILD BOT
# =================================================

def build_bot():
    bot = Application.builder().token(BOT_TOKEN).build()

    # ================= USER COMMANDS =================
    bot.add_handler(CommandHandler("start", start_cmd))
    bot.add_handler(CommandHandler("chat", chat_cmd))
    bot.add_handler(CommandHandler("exit", exit_cmd))
    bot.add_handler(CommandHandler("edit_profile", edit_profile_cmd))

    bot.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text(
        "📌 Commands:\n\n"
        "✅ /start - Register / Open Menu\n"
        "💬 /chat - Choose Human / AI\n"
        "🛑 /exit - Stop conversation\n"
        "✏️ /edit_profile - Edit your profile\n"
        "🔐 /privacy - Privacy Policy\n"
        "💎 /premium - Premium Plans\n"
        "❓ /help - Help Menu"
    )))

    # ================= PRIVACY =================
    bot.add_handler(CommandHandler("privacy", lambda u, c: u.message.reply_text(
        "🔐 *Privacy Policy*\n\n"
        "• Be respectful\n"
        "• No personal info sharing\n"
        "• Use report if needed\n",
        parse_mode="Markdown"
    )))

    # ================= ADMIN =================
    bot.add_handler(CommandHandler("about", about_cmd))
    bot.add_handler(CommandHandler("status", status_cmd))
    bot.add_handler(CommandHandler("giveaway", giveaway_cmd))
    bot.add_handler(CommandHandler("broadcast", broadcast_cmd))
    bot.add_handler(CommandHandler("ban", ban_cmd))
    bot.add_handler(CommandHandler("unban", unban_cmd))
    bot.add_handler(CommandHandler("warn", warn_cmd))

    # ================= AI ADMIN =================
    bot.add_handler(CommandHandler("ai_enable", ai_enable_cmd))
    bot.add_handler(CommandHandler("ai_disable", ai_disable_cmd))

    # ================= CALLBACK QUERY HANDLERS =================

    # Registration flow
    bot.add_handler(
        CallbackQueryHandler(reg_callback, pattern=r"^reg_")
    )

    # Profile edit (IMPORTANT: covers ALL edit & pref callbacks)
    bot.add_handler(
        CallbackQueryHandler(profile_callbacks, pattern=r"^(edit_|pref:)")
    )

    # AI buttons
    bot.add_handler(
        CallbackQueryHandler(
            ai_callbacks,
            pattern=r"^(chat_choice:ai|ai_lang:.*|ai_style:.*|ai_action:.*)$"
        )
    )

    # Human chat buttons
    bot.add_handler(
        CallbackQueryHandler(
            human_callbacks,
            pattern=r"^(chat_choice:human|chat_action:.*|prev_report|prevrep:.*)$"
        )
    )

    # ================= MESSAGE HANDLERS =================
    # ORDER IS VERY IMPORTANT BELOW 👇

    # 1️⃣ Registration age input
    bot.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, reg_age_text)
    )

    # 2️⃣ AI chat messages
    bot.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ai_text)
    )

    # 3️⃣ Human chat messages
    bot.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, human_text)
    )

    # 4️⃣ Human media
    bot.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.Document.ALL |
            filters.AUDIO | filters.VOICE | filters.VIDEO_NOTE |
            filters.Sticker.ALL | filters.ANIMATION,
            human_media
        )
    )

    # 5️⃣ Fallback router (ALWAYS LAST)
    bot.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_router)
    )

    return bot


# =================================================
# FLASK + BOT RUNNER
# =================================================

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
