from datetime import datetime
from telegram import Bot
from app.config import GROUP1_ID, GROUP2_ID

async def log_group1(bot: Bot, text: str):
    if GROUP1_ID:
        await bot.send_message(chat_id=GROUP1_ID, text=text)

async def log_group2(bot: Bot, text: str):
    if GROUP2_ID:
        await bot.send_message(chat_id=GROUP2_ID, text=text)

def now_ist_string():
    # simple timestamp string (UTC stored in DB)
    return datetime.utcnow().isoformat()
