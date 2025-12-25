import requests
from app.core.config import LIGHTRAG_URL

def query_lightrag(query, history, mode="mix"):
    payload = {
        "query": query,
        "mode": mode,
        "conversation_history": history,
        "response_type": "Multiple Paragraphs"
    }
    res = requests.post(LIGHTRAG_URL, json=payload, timeout=60)
    return res.json().get("response", "")
