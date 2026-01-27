import razorpay
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)

PLANS = {
    "week": {"amount": 2900, "days": 7, "label": "1 Week"},
    "month": {"amount": 7900, "days": 30, "label": "1 Month"},
    "quarter": {"amount": 14900, "days": 90, "label": "3 Months"}
}


def create_payment_link(user_id: int, plan_key: str):
    plan = PLANS.get(plan_key)
    if not plan:
        return None

    link = client.payment_link.create({
        "amount": plan["amount"],        # paise
        "currency": "INR",
        "description": f"Premium Plan - {plan['label']}",
        "customer": {
            "name": str(user_id)
        },
        "notes": {
            "user_id": str(user_id)       # 🔥 THIS IS THE KEY POINT
        },
        "notify": {
            "sms": False,
            "email": False
        }
    })

    return link["short_url"]
