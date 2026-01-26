from telegram import Update
from telegram.ext import ContextTypes
from app.handlers.common import banned_guard
from app.services.user_service import get_user
from app.keyboard import states_kb
from app.services.log_service import log_group1


async def edit_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    if not u or not u.get("registered"):
        await update.message.reply_text("❌ Complete registration first using /start")
        return

    await update.message.reply_text(
        "✏️ *Edit Profile*\n\nSelect what you want to update:\n\n"
        "📍 State\n"
        "👤 Gender\n"
        "🔢 Age\n"
        "⭐ Preferences (Premium)",
        parse_mode="Markdown"
    )

    await log_group1(
        context.bot,
        f"✏️ PROFILE EDIT\nUser: {uid}\nFields: Requested edit menu"
    )
