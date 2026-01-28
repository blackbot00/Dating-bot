from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.services.user_service import get_user
from app.services.premium_service import user_has_premium
from app.keyboard import (
    edit_profile_kb,
    genders_kb,
    states_kb
)
from app.services.log_service import log_group1


# -------------------------------------------------
# PROFILE VIEW TEXT
# -------------------------------------------------

def profile_text(u: dict, is_premium: bool) -> str:
    gender = u.get("gender") or "Not set"
    age = u.get("age") or "Not set"
    state = u.get("state") or "Not set"

    premium_txt = "Yes ✅" if is_premium else "No ❌"

    return (
        "⚙️ *Edit Profile*\n\n"
        f"👤 Gender: *{gender}*\n"
        f"📅 Age: *{age}*\n"
        f"🌍 Country: 🇮🇳 India - *{state}*\n"
        f"💎 Premium: *{premium_txt}*\n\n"
        "Use buttons below to update 👇"
    )


# -------------------------------------------------
# /edit_profile COMMAND
# -------------------------------------------------

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
        reply_markup=edit_profile_kb(is_premium=True),  # 👈 always show preference
        parse_mode="Markdown"
    )

    await log_group1(
        context.bot,
        f"✏️ PROFILE EDIT OPENED\nUser: {uid}\nPremium: {is_premium}"
    )


# -------------------------------------------------
# CALLBACK HANDLER (PROFILE BUTTONS)
# -------------------------------------------------

async def profile_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    u = get_user(uid)

    if not u:
        return

    is_premium = user_has_premium(uid)

    # -------- BACK TO PROFILE --------
    if q.data == "edit:back":
        await q.message.reply_text(
            profile_text(u, is_premium),
            reply_markup=edit_profile_kb(is_premium=True),
            parse_mode="Markdown"
        )
        return

    # -------- EDIT GENDER --------
    if q.data == "edit:gender":
        await q.message.reply_text(
            "👤 Select your gender:",
            reply_markup=genders_kb(edit=True)
        )
        return

    # -------- EDIT AGE --------
    if q.data == "edit:age":
        context.user_data["edit_age"] = True
        await q.message.reply_text("🎂 Enter your new age:")
        return

    # -------- EDIT STATE --------
    if q.data == "edit:state":
        await q.message.reply_text(
            "🌍 Select your state:",
            reply_markup=states_kb(edit=True)
        )
        return

    # -------- EDIT PREFERENCE (PREMIUM ONLY) --------
    if q.data == "edit:preference":
        if not is_premium:
            await q.message.reply_text(
                "🔒 *Premium Feature*\n\n"
                "Partner preference is available only for 💎 Premium users.\n"
                "Upgrade to unlock ❤️",
                parse_mode="Markdown"
            )
            return

        await q.message.reply_text(
            "⭐ *Partner Preference*\n\n"
            "Preference setup coming soon 😍",
            parse_mode="Markdown"
        )
        return
