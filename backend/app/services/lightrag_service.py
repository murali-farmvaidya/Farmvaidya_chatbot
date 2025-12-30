import requests
from app.core.config import LIGHTRAG_URL

def query_lightrag(query, history, mode="mix", language="english"):
    """
    Query LightRAG with language awareness
    
    Args:
        query: The user's question
        history: Conversation history
        mode: LightRAG mode (mix, local, global, bypass)
        language: Language to respond in (english, telugu, hindi)
    """
    # Add language instruction to the query
    language_instructions = {
        "telugu": "\n\nIMPORTANT: You MUST respond ONLY in Telugu (తెలుగు) language. Do not use English or any other language in your response.",
        "hindi": "\n\nIMPORTANT: You MUST respond ONLY in Hindi (हिंदी) language. Do not use English or any other language in your response.",
        "english": ""  # No need for instruction in English
    }
    
    language_instruction = language_instructions.get(language, "")
    enhanced_query = query + language_instruction
    
    payload = {
        "query": enhanced_query,
        "mode": mode,
        "conversation_history": history,
        "response_type": "Multiple Paragraphs"
    }
    res = requests.post(LIGHTRAG_URL, json=payload, timeout=60)
    return res.json().get("response", "")

