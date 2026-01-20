from app.config import OWNER_ID
from app.db import users_col

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def is_banned(user_id: int) -> bool:
    u = users_col.find_one({"_id": user_id}, {"is_banned": 1})
    return bool(u and u.get("is_banned"))
