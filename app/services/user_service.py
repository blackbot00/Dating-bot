from datetime import datetime, timedelta, date

from app.db import users_col, settings_col
from app.config import PREMIUM_ENABLED, FREE_TRIAL_DAYS
from app.constants import AI_FREE_PER_DAY
from app.services.premium_service import user_has_premium


# ---------- APP SETTINGS ----------

def ensure_settings():
    settings_col.update_one(
        {"_id": "app"},
        {"$setOnInsert": {
            "premium_enabled": PREMIUM_ENABLED,
            "free_trial_days": FREE_TRIAL_DAYS
        }},
        upsert=True
    )


def get_settings():
    ensure_settings()
    return settings_col.find_one({"_id": "app"})


# ---------- USER ----------

def ensure_user(user_id: int, name: str, username: str | None):
    ensure_settings()

    u = users_col.find_one({"_id": user_id})
    if u:
        users_col.update_one(
            {"_id": user_id},
            {"$set": {"last_active": datetime.utcnow().isoformat()}}
        )
        return

    settings = get_settings()
    premium_enabled = settings.get("premium_enabled", False)
    free_days = int(settings.get("free_trial_days", 7))

    premium_until = None
    is_premium = False

    if premium_enabled:
        premium_until = (
            datetime.utcnow() + timedelta(days=free_days)
        ).isoformat()
        is_premium = True

    users_col.insert_one({
        "_id": user_id,
        "name": name,
        "username": username,

        "state": None,
        "gender": None,
        "age": None,
        "registered": False,

        # ---------- AI ----------
        "ai_mode": False,
        "ai_language": None,
        "ai_style": None,
        "ai_daily_count": 0,
        "ai_daily_date": date.today().isoformat(),

        # ---------- OTHER ----------
        "is_banned": False,
        "is_premium": is_premium,
        "premium_until": premium_until,

        "created_at": datetime.utcnow().isoformat(),
        "last_active": datetime.utcnow().isoformat()
    })


def get_user(user_id: int):
    return users_col.find_one({"_id": user_id})


def set_profile(user_id: int, state: str, gender: str, age: int):
    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "state": state,
            "gender": gender,
            "age": age,
            "registered": True
        }}
    )


# ---------- ✅ THIS WAS MISSING (IMPORTANT) ----------

def set_ai_prefs(
    user_id: int,
    lang: str | None = None,
    style: str | None = None,
    ai_mode: bool | None = None
):
    update = {}

    if lang is not None:
        update["ai_language"] = lang

    if style is not None:
        update["ai_style"] = style

    if ai_mode is not None:
        update["ai_mode"] = ai_mode

    if update:
        users_col.update_one(
            {"_id": user_id},
            {"$set": update}
        )


# ---------- AI DAILY LIMIT ----------

def ai_can_send(user_id: int) -> tuple[bool, int]:
    u = users_col.find_one(
        {"_id": user_id},
        {"ai_daily_count": 1, "ai_daily_date": 1}
    )

    if not u:
        return True, AI_FREE_PER_DAY

    today = date.today().isoformat()

    if u.get("ai_daily_date") != today:
        users_col.update_one(
            {"_id": user_id},
            {"$set": {"ai_daily_count": 0, "ai_daily_date": today}}
        )
        return True, AI_FREE_PER_DAY

    count = int(u.get("ai_daily_count", 0))
    remaining = max(AI_FREE_PER_DAY - count, 0)

    if user_has_premium(user_id):
        return True, remaining

    return (count < AI_FREE_PER_DAY), remaining


def ai_increment(user_id: int):
    today = date.today().isoformat()
    users_col.update_one(
        {"_id": user_id},
        {
            "$inc": {"ai_daily_count": 1},
            "$set": {"ai_daily_date": today}
        },
        upsert=True
    )
