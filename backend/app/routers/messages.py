from fastapi import APIRouter, Depends
from app.db.mongo import messages
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/messages")

@router.get("/{session_id}")
def get_messages(session_id: str, user_id=Depends(get_current_user)):
    cursor = messages.find({"session_id": session_id}).sort("created_at", 1)
    return [{"role": m["role"], "content": m["content"]} for m in cursor]
