"""
Payment Service (Razorpay)

This file is intentionally kept simple.
Later you can add:
- order creation
- webhook verification
- auto premium activation
"""

from datetime import datetime
from app.services.premium_service import activate_premium


def activate_premium_after_payment(user_id: int, plan: str) -> datetime:
    """
    plan values:
    - 'week'
    - 'month'
    - '3month'
    """

    if plan == "week":
        days = 7
    elif plan == "month":
        days = 30
    elif plan == "3month":
        days = 90
    else:
        raise ValueError("Invalid plan")

    valid_till = activate_premium(user_id, days)
    return valid_till
