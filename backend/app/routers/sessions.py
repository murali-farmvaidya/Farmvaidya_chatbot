from fastapi import APIRouter, Depends, Request, HTTPException
from bson import ObjectId
from app.db.mongo import sessions, messages
from app.services.session_service import create_session, list_sessions
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/sessions")

@router.post("/")
def new_session(request: Request, user_id=Depends(get_current_user)):
    sid = create_session(user_id)
    return {"session_id": sid}

@router.get("/")
def get_sessions(request: Request, user_id=Depends(get_current_user)):
    return list_sessions(user_id)

@router.delete("/{session_id}")
def delete_session(session_id: str, user_id=Depends(get_current_user)):
    res = sessions.delete_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })

    messages.delete_many({"session_id": session_id})

    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "deleted"}
