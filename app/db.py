from pymongo import MongoClient
from app.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
user_state_col = db["user_state"]
queue_col = db["queue"]
active_chats_col = db["active_chats"]
reports_col = db["reports"]
settings_col = db["settings"]
