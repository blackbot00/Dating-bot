from datetime import datetime, date

from app.db import users_col
from app.constants import AI_FREE_PER_DAY
from app.services.premium_service import user_has_premium


# ---------- USER ----------

def ensure_user(user_id: int, name: str, username: str | None):
    """
    Create user if not exists.
    """
    u = users_col.find_one({"_id": user_id})
    if u:
        users_col.update_one(
            {"_id": user_id},
            {"$set": {"last_active": datetime.utcnow().isoformat()}}
        )
        return

    users_col.insert_one({
        "_id": user_id,
        "name": name,
        "username": username,

        # ---------- PROFILE ----------
        "state": None,
        "gender": None,
        "age": None,
        "registered": False,

        # ---------- AI CHAT ----------
        "ai_mode": False,
        "ai_language": None,
        "ai_style": None,
        "ai_daily_count": 0,
        "ai_daily_date": date.today().isoformat(),

        # ---------- HUMAN CHAT ----------
        "human_daily_count": 0,
        "human_daily_date": date.today().isoformat(),

        # ---------- PREMIUM ----------
        "is_premium": False,
        "premium_until": None,

        # ---------- OTHER ----------
        "is_banned": False,

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


# ---------- AI PREFS (REQUIRED) ----------

def set_ai_prefs(
    user_id: int,
    lang: str | None = None,
    style: str | None = None,
    ai_mode: bool | None = None
):
    """
    Update AI preferences.
    Used by ai_chat handlers.
    """
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
    """
    Returns (allowed, remaining_today)
    Premium → unlimited
    """
    if user_has_premium(user_id):
        return True, -1

    u = users_col.find_one(
        {"_id": user_id},
        {"ai_daily_count": 1, "ai_daily_date": 1}
    )

    today = date.today().isoformat()

    if not u or u.get("ai_daily_date") != today:
        users_col.update_one(
            {"_id": user_id},
            {"$set": {
                "ai_daily_count": 0,
                "ai_daily_date": today
            }},
            upsert=True
        )
        return True, AI_FREE_PER_DAY

    count = int(u.get("ai_daily_count", 0))
    remaining = max(AI_FREE_PER_DAY - count, 0)

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


# ---------- HUMAN CHAT DAILY LIMIT ----------

HUMAN_FREE_PER_DAY = 11


def human_can_chat(user_id: int) -> tuple[bool, int]:
    """
    Returns (allowed, remaining_today)
    Premium → unlimited
    """
    if user_has_premium(user_id):
        return True, -1

    u = users_col.find_one(
        {"_id": user_id},
        {"human_daily_count": 1, "human_daily_date": 1}
    )

    today = date.today().isoformat()

    if not u or u.get("human_daily_date") != today:
        users_col.update_one(
            {"_id": user_id},
            {"$set": {
                "human_daily_count": 0,
                "human_daily_date": today
            }},
            upsert=True
        )
        return True, HUMAN_FREE_PER_DAY

    count = int(u.get("human_daily_count", 0))
    remaining = max(HUMAN_FREE_PER_DAY - count, 0)

    return (count < HUMAN_FREE_PER_DAY), remaining


def human_increment(user_id: int):
    today = date.today().isoformat()
    users_col.update_one(
        {"_id": user_id},
        {
            "$inc": {"human_daily_count": 1},
            "$set": {"human_daily_date": today}
        },
        upsert=True
    )
