from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.services.user_service import get_user
from app.services.premium_service import user_has_premium
from app.keyboard import (
    edit_profile_kb,
    genders_kb,
    states_kb,
    edit_age_kb,
    preference_kb
)
from app.db import users_col
from app.services.log_service import log_group1


# ---------------- PROFILE TEXT ----------------

def profile_text(u: dict, is_premium: bool) -> str:
    return (
        "⚙️ *Edit Profile*\n\n"
        f"👤 Gender: *{u.get('gender') or 'Not set'}*\n"
        f"🎂 Age: *{u.get('age') or 'Not set'}*\n"
        f"🌍 State: *{u.get('state') or 'Not set'}*\n"
        f"💎 Premium: *{'Yes ✅' if is_premium else 'No ❌'}*\n\n"
        "Choose what to update 👇"
    )


# ---------------- COMMAND ----------------

async def edit_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    u = get_user(uid)

    if not u or not u.get("registered"):
        await update.message.reply_text("❌ Complete registration using /start")
        return

    is_premium = user_has_premium(uid)

    await update.message.reply_text(
        profile_text(u, is_premium),
        reply_markup=edit_profile_kb(is_premium=True),
        parse_mode="Markdown"
    )


# ---------------- CALLBACKS ----------------

async def profile_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    u = get_user(uid)
    is_premium = user_has_premium(uid)

    # -------- BACK --------
    if q.data == "edit:back":
        await q.message.edit_text(
            profile_text(u, is_premium),
            reply_markup=edit_profile_kb(is_premium=True),
            parse_mode="Markdown"
        )
        return

    # -------- GENDER --------
    if q.data == "edit:gender":
        await q.message.edit_text(
            "👤 Select Gender:",
            reply_markup=genders_kb(edit=True)
        )
        return

    if q.data.startswith("edit_gender:"):
        gender = q.data.split(":", 1)[1]
        users_col.update_one({"_id": uid}, {"$set": {"gender": gender}})
        await q.message.edit_text(
            f"✅ Gender updated to *{gender}*",
            parse_mode="Markdown",
            reply_markup=edit_profile_kb(is_premium=True)
        )
        return

    # -------- AGE --------
    if q.data == "edit:age":
        await q.message.edit_text(
            "🎂 Select your age:",
            reply_markup=edit_age_kb()
        )
        return

    if q.data.startswith("edit_age:"):
        age = int(q.data.split(":", 1)[1])
        users_col.update_one({"_id": uid}, {"$set": {"age": age}})
        await q.message.edit_text(
            f"✅ Age updated to *{age}*",
            parse_mode="Markdown",
            reply_markup=edit_profile_kb(is_premium=True)
        )
        return

    # -------- STATE --------
    if q.data == "edit:state":
        await q.message.edit_text(
            "🌍 Select State:",
            reply_markup=states_kb(edit=True)
        )
        return

    if q.data.startswith("edit_state:"):
        state = q.data.split(":", 1)[1]
        users_col.update_one({"_id": uid}, {"$set": {"state": state}})
        await q.message.edit_text(
            f"✅ State updated to *{state}*",
            parse_mode="Markdown",
            reply_markup=edit_profile_kb(is_premium=True)
        )
        return

    # -------- PREFERENCE --------
    if q.data == "edit:preference":
        if not is_premium:
            await q.message.reply_text(
                "🔒 Premium feature\nUpgrade to unlock ❤️"
            )
            return

        await q.message.edit_text(
            "⭐ *Partner Preference*",
            reply_markup=preference_kb(),
            parse_mode="Markdown"
        )
        return
