from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.db import users_col, user_state_col
from app.states import ASK_STATE
from app.keyboard import states_kb
from app.services.queue_service import remove_from_queue
from app.services.match_service import end_chat
from app.services.user_service import set_ai_prefs


async def edit_profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id

    # stop everything
    remove_from_queue(uid)
    end_chat(uid)
    set_ai_prefs(uid, ai_mode=False)

    # reset profile
    users_col.update_one(
        {"_id": uid},
        {"$set": {"state": None, "gender": None, "age": None, "registered": False}}
    )

    # restart registration
    user_state_col.update_one(
        {"_id": uid},
        {"$set": {"step": ASK_STATE, "temp": {}}},
        upsert=True
    )

    await update.message.reply_text(
        "✅ Profile reset done.\n\n📍 Select your State:",
        reply_markup=states_kb()
    )
