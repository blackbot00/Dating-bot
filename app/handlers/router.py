from telegram import Update
from telegram.ext import ContextTypes

from app.db import user_state_col
from app.states import ASK_AGE
from app.handlers.register import reg_age_text
from app.handlers.ai_chat import ai_text
from app.handlers.human_chat import human_text
from app.services.user_service import get_user


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # 1) Registration age step
    st = user_state_col.find_one({"_id": uid})
    if st and st.get("step") == ASK_AGE:
        await reg_age_text(update, context)
        return

    # 2) AI mode
    u = get_user(uid)
    if u and u.get("ai_mode"):
        await ai_text(update, context)
        return

    # 3) Human chat relay
    await human_text(update, context)
