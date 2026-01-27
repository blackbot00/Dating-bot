import hmac
import hashlib
import json
from datetime import datetime

from app.config import RAZORPAY_WEBHOOK_SECRET
from app.services.premium_service import activate_premium

# Plan mapping (amount in paise)
PLAN_MAP = {
    2900: 7,     # ₹29 → 1 week
    7900: 30,    # ₹79 → 1 month
    14900: 90    # ₹149 → 3 months
}


def verify_signature(payload: bytes, received_sig: str) -> bool:
    expected_sig = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_sig, received_sig)


def process_payment(payload: dict):
    """
    Called after signature verification
    """
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    amount = entity.get("amount")          # in paise
    notes = entity.get("notes", {})

    user_id = notes.get("user_id")
    if not user_id:
        return None

    user_id = int(user_id)
    days = PLAN_MAP.get(amount)

    if not days:
        return None

    valid_till = activate_premium(user_id, days)
    return user_id, valid_till
