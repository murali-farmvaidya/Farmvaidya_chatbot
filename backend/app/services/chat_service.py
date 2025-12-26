from bson import ObjectId
from datetime import datetime
from app.db.mongo import messages, sessions
from app.models.message import message_doc
from app.services.lightrag_service import query_lightrag
from app.utils.cleaner import clean_response
from app.services.chat_logic import is_dosage_question

def generate_title(text: str) -> str:
    words = text.strip().split()
    return " ".join(words[:6]).capitalize()

def get_history(session_id):
    cursor = messages.find({"session_id": session_id}).sort("created_at", 1)
    return [{"role": m["role"], "content": m["content"]} for m in cursor]

def handle_chat(session_id, user_message):
    print("🔥 NEW HANDLE_CHAT EXECUTED")
    # 1️⃣ Save user message
    messages.insert_one(message_doc(session_id, "user", user_message))

    # 2️⃣ 🔥 UPDATE last accessed time
    sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"updated_at": datetime.utcnow()}}
    )

    # 🔥 COUNT messages AFTER insert
    msg_count = messages.count_documents({"session_id": session_id})

    # 🔥 FIRST USER MESSAGE = SET TITLE
    if msg_count == 1:
        title = generate_title(user_message)
        sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"title": title}}
        )

    # 🚫 NEVER ask follow-up for dosage questions
    if is_dosage_question(user_message):
        print("✅ DOSAGE BRANCH RETURNING LIGHTRAG ANSWER")

        # ❗ get history EXCLUDING the latest user message
        history = get_history(session_id)[:-1]

        answer = query_lightrag(user_message, history)
        answer = clean_response(answer)

        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 3️⃣ Get history
    history = get_history(session_id)

    # 4️⃣ Get AI response
    answer = query_lightrag(user_message, history[:-1])
    answer = clean_response(answer)

    # 5️⃣ Save assistant response
    messages.insert_one(message_doc(session_id, "assistant", answer))

    return answer
