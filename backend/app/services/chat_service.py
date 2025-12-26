from bson import ObjectId
from app.db.mongo import messages, sessions
from app.models.message import message_doc
from app.services.lightrag_service import query_lightrag
from app.utils.cleaner import clean_response
from app.services.chat_logic import (
    is_direct_knowledge_question,
    is_program_or_fee_question,
    is_logistics_question
)
from app.services.followup_service import needs_follow_up

def generate_title(text: str) -> str:
    words = text.strip().split()
    return " ".join(words[:6]).capitalize()

def get_history(session_id):
    cursor = messages.find({"session_id": session_id}).sort("created_at")
    return [{"role": m["role"], "content": m["content"]} for m in cursor]

def handle_chat(session_id, user_message):
    messages.insert_one(message_doc(session_id, "user", user_message))

    session = sessions.find_one({"_id": ObjectId(session_id)})

    if session and session.get("title") == "New Chat":
        title = generate_title(user_message)
        sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"title": title}}
        )

    followups = session.get("followup_count", 0)

    # ❌ Never ask follow-up for these
    if (
        is_direct_knowledge_question(user_message)
        or is_program_or_fee_question(user_message)
        or is_logistics_question(user_message)
    ):
        answer = query_lightrag(user_message, get_history(session_id))
        answer = clean_response(answer)
        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 🔁 Ask follow-up if needed
    if followups < 2 and needs_follow_up(session_id):
        followup_q = query_lightrag(
            "Ask ONE clear follow-up question.",
            get_history(session_id),
            mode="bypass"
        )

        sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$inc": {"followup_count": 1}}
        )

        messages.insert_one(message_doc(session_id, "assistant", followup_q))
        return followup_q

    # ✅ Final answer
    answer = query_lightrag(user_message, get_history(session_id))
    answer = clean_response(answer)
    messages.insert_one(message_doc(session_id, "assistant", answer))
    return answer
