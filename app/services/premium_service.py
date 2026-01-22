from datetime import datetime
from app.db import settings_col, users_col


def ensure_settings():
    settings_col.update_one(
        {"_id": "app"},
        {"$setOnInsert": {"premium_enabled": False, "free_trial_days": 7}},
        upsert=True
    )


def premium_enabled() -> bool:
    ensure_settings()
    s = settings_col.find_one({"_id": "app"}) or {}
    return bool(s.get("premium_enabled", False))


def set_premium_enabled(value: bool):
    ensure_settings()
    settings_col.update_one({"_id": "app"}, {"$set": {"premium_enabled": value}})


def user_has_premium(user_id: int) -> bool:
    """
    Premium user check.
    If premium_until exists, check date.
    If premium_until missing but is_premium True => treat as premium.
    """
    u = users_col.find_one({"_id": user_id}, {"is_premium": 1, "premium_until": 1})
    if not u:
        return False

    if not u.get("is_premium", False):
        return False

    until = u.get("premium_until")
    if not until:
        return True

    try:
        return datetime.fromisoformat(until) > datetime.utcnow()
    except:
        return True
