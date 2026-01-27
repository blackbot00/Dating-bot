from datetime import datetime, timedelta
from app.db import users_col


def user_has_premium(user_id: int) -> bool:
    """
    Check whether user currently has active premium.
    """
    u = users_col.find_one(
        {"_id": user_id},
        {"is_premium": 1, "premium_until": 1}
    )

    if not u or not u.get("is_premium"):
        return False

    until = u.get("premium_until")

    # No expiry set → lifetime premium
    if not until:
        return True

    try:
        return datetime.fromisoformat(until) > datetime.utcnow()
    except:
        return False


def activate_premium(user_id: int, days: int) -> datetime:
    """
    Activate or extend premium by given days.
    If user already has premium, it will be extended.
    Returns valid_till datetime.
    """
    u = users_col.find_one(
        {"_id": user_id},
        {"premium_until": 1}
    )

    now = datetime.utcnow()
    base_time = now

    # Extend existing premium if still valid
    if u and u.get("premium_until"):
        try:
            old_until = datetime.fromisoformat(u["premium_until"])
            if old_until > now:
                base_time = old_until
        except:
            pass

    valid_till = base_time + timedelta(days=days)

    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "is_premium": True,
            "premium_until": valid_till.isoformat()
        }},
        upsert=True
    )

    return valid_till
