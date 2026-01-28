from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.db import user_state_col
from app.states import ASK_STATE, ASK_GENDER, ASK_AGE, DONE
from app.keyboard import states_kb, genders_kb, choose_chat_kb
from app.constants import MIN_AGE, MAX_AGE
from app.services.user_service import set_profile, get_user
from app.services.log_service import log_group1
from app.handlers.common import banned_guard


# ---------- BACK BUTTON ----------

def back_kb(target: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data=f"reg_back:{target}")]
    ])


# ---------- CALLBACK HANDLER ----------

async def reg_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    q = update.callback_query
    await q.answer()

    uid = q.from_user.id

    st = user_state_col.find_one({"_id": uid}) or {
        "_id": uid,
        "step": ASK_STATE,
        "temp": {}
    }

    step = st.get("step")
    temp = st.get("temp", {})
    data = q.data

    # ---------- BACK HANDLER ----------
    if data.startswith("reg_back:"):
        target = data.split(":", 1)[1]

        if target == "state":
            user_state_col.update_one(
                {"_id": uid},
                {"$set": {"step": ASK_STATE}},
                upsert=True
            )
            await q.message.edit_text(
                "🌍 Select your State:",
                reply_markup=states_kb()
            )
            return

        if target == "gender":
            user_state_col.update_one(
                {"_id": uid},
                {"$set": {"step": ASK_GENDER}},
                upsert=True
            )
            await q.message.edit_text(
                "👤 Select your Gender:",
                reply_markup=InlineKeyboardMarkup(
                    genders_kb().inline_keyboard +
                    back_kb("state").inline_keyboard
                )
            )
            return

    # ---------- STATE ----------
    if data.startswith("reg_state:"):
        state = data.split(":", 1)[1]
        temp["state"] = state

        user_state_col.update_one(
            {"_id": uid},
            {"$set": {"step": ASK_GENDER, "temp": temp}},
            upsert=True
        )

        await q.message.edit_text(
            f"🌍 State selected: *{state}*\n\n👤 Select Gender:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                genders_kb().inline_keyboard +
                back_kb("state").inline_keyboard
            )
        )
        return

    # ---------- GENDER ----------
    if data.startswith("reg_gender:"):
        gender = data.split(":", 1)[1]
        temp["gender"] = gender

        user_state_col.update_one(
            {"_id": uid},
            {"$set": {"step": ASK_AGE, "temp": temp}},
            upsert=True
        )

        await q.message.edit_text(
            f"👤 Gender selected: *{gender}*\n\n🎂 Enter your Age ({MIN_AGE}-{MAX_AGE}):",
            parse_mode="Markdown",
            reply_markup=back_kb("gender")
        )
        return


# ---------- AGE TEXT HANDLER ----------

async def reg_age_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id
    st = user_state_col.find_one({"_id": uid})

    if not st or st.get("step") != ASK_AGE:
        return

    txt = (update.message.text or "").strip()

    if not txt.isdigit():
        await update.message.reply_text("❌ Please enter a valid age number.")
        return

    age = int(txt)
    if age < MIN_AGE or age > MAX_AGE:
        await update.message.reply_text(
            f"❌ Age must be between {MIN_AGE} and {MAX_AGE}."
        )
        return

    temp = st.get("temp", {})
    state = temp.get("state")
    gender = temp.get("gender")

    set_profile(uid, state, gender, age)
    user_state_col.update_one(
        {"_id": uid},
        {"$set": {"step": DONE}},
        upsert=True
    )

    u = get_user(uid)

    await log_group1(
        context.bot,
        f"✅ REG COMPLETED\n"
        f"ID: {uid}\n"
        f"State: {state}\n"
        f"Gender: {gender}\n"
        f"Age: {age}\n"
        f"Username: @{u.get('username') or 'none'}"
    )

    await update.message.reply_text(
        "✅ *Registration Completed!*\n\n💬 Choose chat mode:",
        parse_mode="Markdown",
        reply_markup=choose_chat_kb()
    )
