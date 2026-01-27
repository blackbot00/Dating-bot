from telegram import Bot
from app.config import BOT_TOKEN

bot = Bot(BOT_TOKEN)


def send_premium_message(user_id: int, valid_till):
    try:
        bot.send_message(
            chat_id=user_id,
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
