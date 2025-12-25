from fastapi import APIRouter, Depends, Request
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
