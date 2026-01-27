from datetime import datetime, date

from app.db import users_col, settings_col
from app.constants import AI_FREE_PER_DAY
from app.services.premium_service import user_has_premium


# ---------- USER ----------

def ensure_user(user_id: int, name: str, username: str | None):
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

        # ---------- HUMAN CHAT ----------
        "human_daily_count": 0,
        "human_daily_date": date.today().isoformat(),

        # ---------- OTHER ----------
        "is_banned": False,
        "is_premium": False,
        "premium_until": None,

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


# ---------- HUMAN CHAT DAILY LIMIT ----------

HUMAN_FREE_PER_DAY = 11


def human_can_chat(user_id: int) -> tuple[bool, int]:
    """
    Returns (allowed, remaining_today)
    """
    if user_has_premium(user_id):
        return True, -1  # unlimited

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
