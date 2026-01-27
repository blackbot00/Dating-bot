from telegram import Update
from telegram.ext import ContextTypes


async def premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 *Premium Plans*\n\n"
        "🗓️ 1 Week  – ₹29\n"
        "🗓️ 1 Month – ₹79\n"
        "🗓️ 3 Months – ₹149\n\n"
        "✨ *Premium Benefits*\n"
        "🤖 Unlimited AI Chat\n"
        "👩‍❤️‍👨 Unlimited Human Chat\n"
        "⚡ Faster & priority matching\n\n"
        "💳 Payment via *Razorpay*\n"
        "✅ All cards supported\n\n"
        "📌 Premium activation will be instant after payment.",
        parse_mode="Markdown"
    )
