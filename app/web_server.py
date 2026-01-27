import json
from flask import Flask, request, abort

from app.services.payment_service import verify_signature, process_payment
from app.telegram_bot import send_premium_message  # we will add this

app = Flask(__name__)


@app.get("/")
def home():
    return "✅ Bot Running"


@app.get("/health")
def health():
    return "ok"


@app.post("/razorpay/webhook")
def razorpay_webhook():
    sig = request.headers.get("X-Razorpay-Signature")
    payload = request.data

    if not sig or not verify_signature(payload, sig):
        abort(400, "Invalid signature")

    data = json.loads(payload.decode())
    result = process_payment(data)

    if result:
        user_id, valid_till = result
        send_premium_message(user_id, valid_till)

    return {"status": "ok"}
