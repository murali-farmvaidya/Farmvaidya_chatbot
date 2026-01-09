import requests
from app.core.config import LIGHTRAG_URL
from deep_translator import GoogleTranslator
from app.utils.domain_translator import translate_to_english, translate_to_telugu

def query_lightrag(query, history, mode="mix", language="english", factual=False):
    """
    Query LightRAG with language awareness and domain-specific term translation
    
    Args:
        query: The user's question
        history: Conversation history
        mode: LightRAG mode (mix, local, global, bypass)
        language: Language to respond in (english, telugu, hindi, etc.)
        factual: If True, use softer language instruction to avoid forcing wrong answers
    """
    
    print(f"🎯 query_lightrag called with:")
    print(f"   📝 query: {query[:100]}...")
    print(f"   📚 history length: {len(history)} messages")
    print(f"   🔧 mode: {mode}")
    print(f"   🌍 language: {language}")
    print(f"   ℹ️ factual: {factual}")
    
    # Step 1: Translate domain-specific Telugu terms to English for better LLM understanding
    query_with_english_terms = translate_to_english(query)
    if query != query_with_english_terms:
        print(f"🔄 Domain translation: {query} → {query_with_english_terms}")
    
    # Step 2: Translate non-English queries to English for LightRAG search
    english_query = query_with_english_terms
    if language != "english":
        print(f"🔄 Query language is {language}, translating to English...")
        try:
            translator = GoogleTranslator(source='auto', target='en')
            english_query = translator.translate(query_with_english_terms)
            print(f"✅ Translated query: {query_with_english_terms} → {english_query}")
        except Exception as e:
            print(f"⚠️ Translation failed: {e}, using original query")
            english_query = query_with_english_terms
    else:
        print(f"✅ Query language is English, no translation needed")
    
    # Query LightRAG with English query (no language instruction appended)
    payload = {
        "query": english_query,
        "mode": mode,
        "conversation_history": history,
        "response_type": "Multiple Paragraphs"
    }
    
    res = requests.post(LIGHTRAG_URL, json=payload, timeout=60)
    english_response = res.json().get("response", "")
    print(f"📥 LightRAG response (first 150 chars): {english_response[:150]}...")
    
    # Step 3: Translate domain-specific English terms back to Telugu in response (if Telugu conversation)
    response_with_telugu_terms = translate_to_telugu(english_response, language)
    if english_response != response_with_telugu_terms:
        print(f"🔄 Domain translation applied to response")
    
    # Step 4: If language is not English, translate the entire response
    if language != "english" and response_with_telugu_terms and "[no-context]" not in response_with_telugu_terms.lower():
        print(f"🔄 Response language is {language}, translating from English...")
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
            translated_response = translator.translate(response_with_telugu_terms)
            print(f"✅ Response translated from English to {language}")
            return translated_response
        except Exception as e:
            print(f"⚠️ Translation of response failed: {e}, returning response with Telugu terms")
            return response_with_telugu_terms
    else:
        print(f"✅ Language is English, returning response without translation")
    
    return response_with_telugu_terms

