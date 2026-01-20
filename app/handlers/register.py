from telegram import Update
from telegram.ext import ContextTypes
from app.db import user_state_col
from app.states import ASK_STATE, ASK_GENDER, ASK_AGE, DONE
from app.keyboard import genders_kb, choose_chat_kb
from app.constants import MIN_AGE, MAX_AGE
from app.services.user_service import set_profile, get_user
from app.services.log_service import log_group1
from app.handlers.common import banned_guard

async def reg_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return

    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    st = user_state_col.find_one({"_id": uid}) or {"step": ASK_STATE, "temp": {}}
    step = st.get("step")
    temp = st.get("temp", {})

    data = q.data

    if data.startswith("reg_state:"):
        state = data.split(":", 1)[1]
        temp["state"] = state
        user_state_col.update_one({"_id": uid}, {"$set": {"step": ASK_GENDER, "temp": temp}}, upsert=True)
        await q.message.reply_text("✅ State selected.\n\n👤 Select Gender:", reply_markup=genders_kb())
        return

    if data.startswith("reg_gender:"):
        gender = data.split(":", 1)[1]
        temp["gender"] = gender
        user_state_col.update_one({"_id": uid}, {"$set": {"step": ASK_AGE, "temp": temp}}, upsert=True)
        await q.message.reply_text(f"✅ Gender selected: {gender}\n\n🎂 Enter your Age ({MIN_AGE}-{MAX_AGE}):")
        return

async def reg_age_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context): return

    uid = update.effective_user.id
    st = user_state_col.find_one({"_id": uid})
    if not st or st.get("step") != ASK_AGE:
        return

    txt = (update.message.text or "").strip()

    if not txt.isdigit():
        await update.message.reply_text("❌ Age number மட்டும் type பண்ணுங்க.")
        return

    age = int(txt)
    if age < MIN_AGE or age > MAX_AGE:
        await update.message.reply_text(f"❌ Invalid age. Enter {MIN_AGE}-{MAX_AGE} only.")
        return

    temp = st.get("temp", {})
    state = temp.get("state")
    gender = temp.get("gender")

    set_profile(uid, state, gender, age)
    user_state_col.update_one({"_id": uid}, {"$set": {"step": DONE}}, upsert=True)

    u = get_user(uid)

    await log_group1(
        context.bot,
        f"✅ REG COMPLETED\nID: {uid}\nState: {state}\nGender: {gender}\nAge: {age}\nUsername: @{u.get('username') or 'none'}"
    )

    await update.message.reply_text(
        "✅ Registration Completed!\n\n💬 நீங்க யாரோட chat பண்ணப்போறீங்க?",
        reply_markup=choose_chat_kb()
      )
