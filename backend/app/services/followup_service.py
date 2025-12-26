from app.services.lightrag_service import query_lightrag
from app.db.mongo import messages

def needs_follow_up(session_id: str) -> bool:
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages.find({"session_id": session_id}).sort("created_at")
    ]

    payload = {
        "query": (
            "You are an agriculture assistant.\n\n"
            "Ask a follow-up question ONLY IF:\n"
            "- The answer depends on farmer-specific inputs "
            "(crop type, symptoms, soil condition, growth stage, location).\n\n"
            "Reply ONLY with:\n"
            "ANSWER_DIRECTLY or ASK_FOLLOW_UP"
        ),
        "mode": "bypass",
        "conversation_history": history,
        "response_type": "Single Sentence"
    }

    res = query_lightrag(payload["query"], history, mode="bypass")
    return res.strip().upper() == "ASK_FOLLOW_UP"
