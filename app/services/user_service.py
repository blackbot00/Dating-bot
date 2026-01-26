from datetime import datetime, timedelta, date
from app.db import users_col, settings_col
from app.config import PREMIUM_ENABLED, FREE_TRIAL_DAYS
from app.constants import AI_FREE_PER_DAY
from app.services.premium_service import user_has_premium


def ensure_settings():
    settings_col.update_one(
        {"_id": "app"},
        {"$setOnInsert": {"premium_enabled": PREMIUM_ENABLED, "free_trial_days": FREE_TRIAL_DAYS}},
        upsert=True
    )


def ensure_user(user_id: int, name: str, username: str | None):
    ensure_settings()

    if users_col.find_one({"_id": user_id}):
        users_col.update_one({"_id": user_id}, {"$set": {"last_active": datetime.utcnow().isoformat()}})
        return

    users_col.insert_one({
        "_id": user_id,
        "name": name,
        "username": username,

        "state": None,
        "gender": None,
        "age": None,
        "registered": False,

        # 🔥 Preferences (Premium only)
        "pref_gender": None,
        "pref_age_min": None,
        "pref_age_max": None,

        "is_premium": False,
        "premium_until": None,

        "ai_mode": False,
        "ai_language": None,
        "ai_style": None,

        "ai_daily_count": 0,
        "ai_daily_date": date.today().isoformat(),

        "created_at": datetime.utcnow().isoformat(),
        "last_active": datetime.utcnow().isoformat()
    })


def set_profile(user_id: int, *, state=None, gender=None, age=None):
    upd = {}
    if state is not None:
        upd["state"] = state
    if gender is not None:
        upd["gender"] = gender
    if age is not None:
        upd["age"] = age
    if upd:
        upd["registered"] = True
        users_col.update_one({"_id": user_id}, {"$set": upd})


def set_preferences(user_id: int, gender=None, age_min=None, age_max=None):
    if not user_has_premium(user_id):
        return False

    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "pref_gender": gender,
            "pref_age_min": age_min,
            "pref_age_max": age_max
        }}
    )
    return True


def get_user(user_id: int):
    return users_col.find_one({"_id": user_id})
