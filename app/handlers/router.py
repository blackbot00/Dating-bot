from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.db import user_state_col
from app.states import ASK_AGE
from app.services.user_service import get_user
from app.services.match_service import is_in_chat


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id

    # 1️⃣ Registration age step → let reg_age_text handle it
    st = user_state_col.find_one({"_id": uid})
    if st and st.get("step") == ASK_AGE:
        return  # reg_age_text already handled by its own MessageHandler

    # 2️⃣ If user is in HUMAN chat → DO NOTHING
    # human_text MessageHandler will forward message + log group2
    if is_in_chat(uid):
        return

    # 3️⃣ If user is in AI mode → DO NOTHING
    # ai_text MessageHandler will handle it
    u = get_user(uid)
    if u and u.get("ai_mode"):
        return

    # 4️⃣ Fallback message (idle user)
    await update.message.reply_text(
        "ℹ️ Use /chat to start chatting 😊"
    )
