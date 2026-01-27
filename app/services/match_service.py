from datetime import datetime, date
from app.db import active_chats_col, users_col
from app.services.queue_service import find_candidate
from app.services.premium_service import user_has_premium

FREE_DAILY_LIMIT = 10


def _can_human_chat(uid: int) -> bool:
    if user_has_premium(uid):
        return True

    u = users_col.find_one(
        {"_id": uid},
        {"human_count": 1, "human_date": 1}
    )

    today = date.today().isoformat()

    if not u or u.get("human_date") != today:
        users_col.update_one(
            {"_id": uid},
            {"$set": {"human_count": 0, "human_date": today}},
            upsert=True
        )
        return True

    return u.get("human_count", 0) < FREE_DAILY_LIMIT


def _inc_human(uid: int):
    users_col.update_one(
        {"_id": uid},
        {"$inc": {"human_count": 1}},
        upsert=True
    )


def is_in_chat(uid: int) -> bool:
    return active_chats_col.find_one(
        {"$or": [{"user1": uid}, {"user2": uid}], "status": "active"}
    ) is not None


def create_chat(u1: int, u2: int):
    active_chats_col.insert_one({
        "user1": u1,
        "user2": u2,
        "status": "active",
        "started_at": datetime.utcnow().isoformat()
    })
    _inc_human(u1)
    _inc_human(u2)


def try_match(user: dict):
    uid = user["_id"]

    if not _can_human_chat(uid):
        return None

    return find_candidate({"_id": {"$ne": uid}})
