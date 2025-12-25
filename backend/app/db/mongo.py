from pymongo import MongoClient
from app.core.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users = db.users
sessions = db.sessions
messages = db.messages
