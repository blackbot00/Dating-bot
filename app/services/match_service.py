from datetime import datetime
from app.db import active_chats_col
from app.services.queue_service import find_candidate
from app.services.premium_service import user_has_premium


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


def get_partner(uid: int):
    chat = active_chats_col.find_one(
        {"$or": [{"user1": uid}, {"user2": uid}], "status": "active"}
    )
    if not chat:
        return None
    return chat["user2"] if chat["user1"] == uid else chat["user1"]


def end_chat(uid: int):
    chat = active_chats_col.find_one(
        {"$or": [{"user1": uid}, {"user2": uid}], "status": "active"}
    )
    if chat:
        active_chats_col.update_one(
            {"_id": chat["_id"]},
            {"$set": {"status": "ended"}}
        )
    return chat


def try_match(user: dict):
    uid = user["_id"]

    # 💎 Premium preference match
    if user_has_premium(uid):
        q = {}
        if user.get("pref_gender"):
            q["gender"] = user["pref_gender"]
        if user.get("pref_age_min") and user.get("pref_age_max"):
            q["age"] = {
                "$gte": user["pref_age_min"],
                "$lte": user["pref_age_max"]
            }
        if q:
            q["_id"] = {"$ne": uid}
            c = find_candidate(q)
            if c:
                return c

    # 🔁 Fallback random match
    return find_candidate({"_id": {"$ne": uid}})
