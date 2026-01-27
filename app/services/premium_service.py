from datetime import datetime, timedelta
from app.db import users_col


def user_has_premium(user_id: int) -> bool:
    u = users_col.find_one(
        {"_id": user_id},
        {"is_premium": 1, "premium_until": 1}
    )
    if not u or not u.get("is_premium"):
        return False

    until = u.get("premium_until")
    if not until:
        return True

    try:
        return datetime.fromisoformat(until) > datetime.utcnow()
    except:
        return False


def activate_premium(user_id: int, days: int) -> datetime:
    """
    Activate / extend premium by given days.
    Returns valid_till datetime.
    """
    u = users_col.find_one(
        {"_id": user_id},
        {"premium_until": 1}
    )

    now = datetime.utcnow()
    base = now

    if u and u.get("premium_until"):
        try:
            old = datetime.fromisoformat(u["premium_until"])
            if old > now:
                base = old
        except:
            pass

    valid_till = base + timedelta(days=days)

    users_col.update_one(
        {"_id": user_id},
        {"$set": {
            "is_premium": True,
            "premium_until": valid_till.isoformat()
        }}
    )

    return valid_till
