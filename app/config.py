import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "datingbot")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GROUP1_ID = int(os.getenv("GROUP1_ID", "0"))  # registration + reports
GROUP2_ID = int(os.getenv("GROUP2_ID", "0"))  # chat logs

PREMIUM_ENABLED = os.getenv("PREMIUM_ENABLED", "false").lower() == "true"
FREE_TRIAL_DAYS = int(os.getenv("FREE_TRIAL_DAYS", "7"))
