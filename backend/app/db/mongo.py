from pymongo import MongoClient
from app.core.config import MONGO_URI, DB_NAME

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.server_info()
    print("[SUCCESS] MongoDB connected successfully")
    db = client[DB_NAME]
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    print(f"   URI: {MONGO_URI}")
    raise

users = db.users
sessions = db.sessions
messages = db.messages
