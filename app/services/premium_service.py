from datetime import datetime
from app.db import settings_col, users_col
from app.services.user_service import ensure_settings

def premium_enabled():
    ensure_settings()
    s = settings_col.find_one({"_id": "app"})
    return bool(s.get("premium_enabled", False))

def set_premium_enabled(value: bool):
    ensure_settings()
    settings_col.update_one({"_id": "app"}, {"$set": {"premium_enabled": value}})

def user_has_premium(user_id: int) -> bool:
    u = users_col.find_one({"_id": user_id}, {"is_premium": 1, "premium_until": 1})
    if not u:
        return False
    if not u.get("is_premium"):
        return False
    until = u.get("premium_until")
    if not until:
        return True
    try:
        return datetime.fromisoformat(until) > datetime.utcnow()
    except:
        return True
