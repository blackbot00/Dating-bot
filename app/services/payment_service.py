import hmac
import hashlib
import json
from datetime import datetime, timedelta

from app.db import users_col
from app.services.premium_service import activate_premium


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Razorpay webhook signature
    """
    generated = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(generated, signature)


def process_payment(data: dict):
    """
    Process successful Razorpay payment
    Expected notes:
      notes.user_id
      notes.plan_days
    """
    entity = data.get("payload", {}).get("payment", {}).get("entity", {})
    notes = entity.get("notes", {})

    try:
        user_id = int(notes.get("user_id"))
        days = int(notes.get("plan_days"))
    except:
        return False

    # ✅ Activate premium
    activate_premium(user_id, days)
    return True
