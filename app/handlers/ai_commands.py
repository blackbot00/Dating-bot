from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.security import is_owner
from app.db import settings_col
from app.keyboard import ai_language_kb
from app.services.user_service import get_user, set_ai_prefs

ADMIN_ONLY_MSG = "🚫 This command is for Admin only 🥸"


def ensure_ai_settings():
    settings_col.update_one(
        {"_id": "app"},
        {"$setOnInsert": {"ai_enabled": True}},
        upsert=True
    )


def ai_is_enabled() -> bool:
    ensure_ai_settings()
    s = settings_col.find_one({"_id": "app"}) or {}
    return bool(s.get("ai_enabled", True))


def set_ai_enabled(value: bool):
    ensure_ai_settings()
    settings_col.update_one({"_id": "app"}, {"$set": {"ai_enabled": value}})


# ---------------- ADMIN COMMANDS ----------------

async def ai_enable_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    set_ai_enabled(True)
    await update.message.reply_text("✅ AI chat enabled")


async def ai_disable_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    if not is_owner(update.effective_user.id):
        await update.message.reply_text(ADMIN_ONLY_MSG)
        return

    set_ai_enabled(False)
    await update.message.reply_text("🚫 AI chat disabled")


# ---------------- AI FLOW START ----------------

async def start_ai_flow_from_button(message, uid: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    This is the ONLY place where language keyboard is shown
    """
    u = get_user(uid)

    if not u or not u.get("registered"):
        await message.reply_text("❌ First register using /start")
        return False

    if not ai_is_enabled():
        await message.reply_text("🚫 AI chat is temporarily disabled.")
        return False

    # reset AI state
    set_ai_prefs(uid, ai_mode=False, lang=None, style=None)

    await message.reply_text(
        "🌐 Select your language:",
        reply_markup=ai_language_kb()
    )
    return True
