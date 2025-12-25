from datetime import datetime

def message_doc(session_id, role, content):
    return {
        "session_id": session_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow()
    }
