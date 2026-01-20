from datetime import datetime
from app.db import queue_col

def add_to_queue(user_id: int, state: str, gender: str, age: int):
    queue_col.update_one(
        {"_id": user_id},
        {"$set": {"state": state, "gender": gender, "age": age, "joined_at": datetime.utcnow().isoformat()}},
        upsert=True
    )

def remove_from_queue(user_id: int):
    queue_col.delete_one({"_id": user_id})

def find_candidate(query: dict):
    # oldest first
    return queue_col.find_one(query, sort=[("joined_at", 1)])
