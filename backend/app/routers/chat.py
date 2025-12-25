from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from app.services.chat_service import handle_chat
from app.middleware.auth_middleware import get_current_user

router = APIRouter()

class Chat(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
def chat(data: Chat, user_id=Depends(get_current_user)):
    return {"response": handle_chat(data.session_id, data.message)}
