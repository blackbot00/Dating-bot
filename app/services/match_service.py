from datetime import datetime
from app.constants import AGE_DIFF_LIMIT
from app.db import active_chats_col
from app.services.queue_service import find_candidate, remove_from_queue

def get_opposite_gender(gender: str) -> str | None:
    if gender == "Male":
        return "Female"
    if gender == "Female":
        return "Male"
    return None

def is_in_chat(user_id: int) -> bool:
    return active_chats_col.find_one({"$or": [{"user1": user_id}, {"user2": user_id}], "status": "active"}) is not None

def create_chat(user1: int, user2: int):
    active_chats_col.insert_one({
        "user1": user1,
        "user2": user2,
        "status": "active",
        "started_at": datetime.utcnow().isoformat()
    })

def end_chat(user_id: int):
    chat = active_chats_col.find_one({"$or": [{"user1": user_id}, {"user2": user_id}], "status": "active"})
    if not chat:
        return None
    active_chats_col.update_one({"_id": chat["_id"]}, {"$set": {"status": "ended", "ended_at": datetime.utcnow().isoformat()}})
    return chat

def get_partner(user_id: int):
    chat = active_chats_col.find_one({"$or": [{"user1": user_id}, {"user2": user_id}], "status": "active"})
    if not chat:
        return None
    partner = chat["user2"] if chat["user1"] == user_id else chat["user1"]
    return partner

def try_match(user):
    """
    Order:
    1) same state + opposite
    2) any state + opposite
    3) same state + random
    4) full random
    """
    uid = user["_id"]
    state = user["state"]
    gender = user["gender"]
    age = user["age"]

    opp = get_opposite_gender(gender)

    def age_query():
        return {"$gte": age - AGE_DIFF_LIMIT, "$lte": age + AGE_DIFF_LIMIT}

    # 1
    if opp:
        c = find_candidate({"state": state, "gender": opp, "age": age_query(), "_id": {"$ne": uid}})
        if c: return c

    # 2
    if opp:
        c = find_candidate({"gender": opp, "age": age_query(), "_id": {"$ne": uid}})
        if c: return c

    # 3
    c = find_candidate({"state": state, "age": age_query(), "_id": {"$ne": uid}})
    if c: return c

    # 4
    c = find_candidate({"age": age_query(), "_id": {"$ne": uid}})
    return c
