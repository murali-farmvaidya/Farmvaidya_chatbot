import requests
from app.core.config import LIGHTRAG_URL
from deep_translator import GoogleTranslator

def query_lightrag(query, history, mode="mix", language="english", factual=False):
    """
    Query LightRAG with language awareness
    
    Args:
        query: The user's question
        history: Conversation history
        mode: LightRAG mode (mix, local, global, bypass)
        language: Language to respond in (english, telugu, hindi, etc.)
        factual: If True, use softer language instruction to avoid forcing wrong answers
    """
    
    # Translate non-English queries to English for LightRAG search
    english_query = query
    if language != "english":
        try:
            translator = GoogleTranslator(source='auto', target='en')
            english_query = translator.translate(query)
            print(f"🔄 Translated query: {query} → {english_query}")
        except Exception as e:
            print(f"⚠️ Translation failed: {e}, using original query")
            english_query = query
    
    # Query LightRAG with English query (no language instruction appended)
    payload = {
        "query": english_query,
        "mode": mode,
        "conversation_history": history,
        "response_type": "Multiple Paragraphs"
    }
    
    res = requests.post(LIGHTRAG_URL, json=payload, timeout=60)
    english_response = res.json().get("response", "")
    
    # If language is not English, translate the response
    if language != "english" and english_response and "[no-context]" not in english_response.lower():
        try:
            # Map language codes to translator codes
            lang_code_map = {
                "telugu": "te",
                "tamil": "ta", 
                "kannada": "kn",
                "malayalam": "ml",
                "hindi": "hi",
                "marathi": "mr",
                "bengali": "bn",
                "gujarati": "gu",
                "punjabi": "pa",
                "odia": "or"
            }
            
            target_lang = lang_code_map.get(language, "en")
            translator = GoogleTranslator(source='en', target=target_lang)
            translated_response = translator.translate(english_response)
            print(f"🌐 Response translated from English to {language}")
            return translated_response
        except Exception as e:
            print(f"⚠️ Translation of response failed: {e}, returning English response")
            return english_response
    
    return english_response

