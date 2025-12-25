from bson import ObjectId
from app.db.mongo import sessions
from app.models.session import session_doc

def create_session(user_id, title="New Chat"):
    res = sessions.insert_one(session_doc(user_id, title))
    return str(res.inserted_id)

def list_sessions(user_id):
    return [
        {"id": str(s["_id"]), "title": s["title"]}
        for s in sessions.find({"user_id": user_id})
    ]
