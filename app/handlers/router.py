from telegram import Update
from telegram.ext import ContextTypes

from app.db import user_state_col
from app.states import ASK_AGE
from app.services.user_service import get_user

from app.handlers.register import reg_age_text
from app.handlers.ai_chat import ai_text
from app.handlers.human_chat import human_text

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # 1) If registration asking age -> handle age first
    st = user_state_col.find_one({"_id": uid})
    if st and st.get("step") == ASK_AGE:
        return await reg_age_text(update, context)

    # 2) If AI mode ON -> AI handler
    u = get_user(uid)
    if u and u.get("ai_mode"):
        return await ai_text(update, context)

    # 3) Else if user in human chat -> relay handler
    return await human_text(update, context)