from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.chat_service import handle_chat
from app.middleware.auth_middleware import get_current_user
import traceback

router = APIRouter()

class Chat(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
def chat(data: Chat, user_id=Depends(get_current_user)):
    try:
        print(f"[Chat] Received message from user {user_id}: {data.message[:50]}...")
        response = handle_chat(data.session_id, data.message)
        print(f"[Chat] Generated response: {response[:50]}...")
        return {"response": response}
    except Exception as e:
        print(f"[Chat] ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
