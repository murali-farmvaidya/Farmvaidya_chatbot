from app.db.mongo import messages
from app.models.message import message_doc
from app.services.lightrag_service import query_lightrag
from app.utils.cleaner import clean_response

def get_history(session_id):
    cursor = messages.find({"session_id": session_id}).sort("created_at")
    return [{"role": m["role"], "content": m["content"]} for m in cursor]

def handle_chat(session_id, user_message):
    messages.insert_one(message_doc(session_id, "user", user_message))

    history = get_history(session_id)

    answer = query_lightrag(user_message, history)
    answer = clean_response(answer)

    messages.insert_one(message_doc(session_id, "assistant", answer))
    return answer
