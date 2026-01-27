from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.services.user_service import get_user
from app.services.premium_service import user_has_premium
from app.keyboard import edit_profile_kb
from app.services.log_service import log_group1


def profile_text(u: dict, is_premium: bool) -> str:
    gender = u.get("gender") or "Not set"
    age = u.get("age") or "Not set"
    state = u.get("state") or "Not set"

    premium_txt = "Yes ✅" if is_premium else "No ❌"

    return (
        "⚙️ *Edit Profile*\n\n"
        f"👤 Gender: {gender}\n"
        f"📅 Age: {age}\n"
        f"🌍 Country: 🇮🇳 India - {state}\n"
        f"💎 Premium: {premium_txt}\n\n"
        "Use buttons below to update:"
    )


async def edit_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    if not u or not u.get("registered"):
        await update.message.reply_text(
            "❌ Complete registration first using /start"
        )
        return

    is_premium = user_has_premium(uid)

    await update.message.reply_text(
        profile_text(u, is_premium),
        reply_markup=edit_profile_kb(is_premium),
        parse_mode="Markdown"
    )

    await log_group1(
        context.bot,
        f"✏️ PROFILE EDIT OPENED\nUser: {uid}\nPremium: {is_premium}"
)
