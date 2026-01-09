import requests
from app.core.config import LIGHTRAG_URL
from deep_translator import GoogleTranslator
from app.utils.domain_translator import translate_to_english, translate_to_telugu

def query_lightrag(query, history, mode="mix", language="english", factual=False):
    """
    Query LightRAG with ALWAYS translating to/from English to maintain language consistency.
    LightRAG knowledge base has mixed content, so we MUST translate both ways.
    
    Args:
        query: The user's question (any language)
        history: Conversation history
        mode: LightRAG mode (mix, local, global, bypass)
        language: Language to respond in (english, telugu, hindi, etc.)
        factual: Not used anymore, kept for backward compatibility
    """
    
    print(f"🎯 query_lightrag called with:")
    print(f"   📝 query: {query[:100]}...")
    print(f"   📚 history length: {len(history)} messages")
    print(f"   🔧 mode: {mode}")
    print(f"   🌍 language: {language}")
    
    # Step 1: Translate domain-specific terms to English (e.g., "ఇన్విక్టస్" → "Invictus")
    query_with_english_terms = translate_to_english(query)
    if query != query_with_english_terms:
        print(f"📖 Domain translation (query): {query[:50]} → {query_with_english_terms[:50]}")
    
    # Step 2: ALWAYS translate query to English for LightRAG (even if already English to ensure clean input)
    english_query = query_with_english_terms
    if language != "english":
        print(f"🔄 Translating {language} query to English...")
        try:
            translator = GoogleTranslator(source='auto', target='en')
            english_query = translator.translate(query_with_english_terms)
            print(f"✅ Query translated: {query_with_english_terms[:50]} → {english_query[:50]}")
        except Exception as e:
            print(f"⚠️ Translation failed: {e}, using original")
            english_query = query_with_english_terms
    
    # Step 3: Query LightRAG with PURE ENGLISH query (no language instructions)
    payload = {
        "query": english_query,
        "mode": mode,
        "conversation_history": history,
        "response_type": "Multiple Paragraphs"
    }
    
    res = requests.post(LIGHTRAG_URL, json=payload, timeout=60)
    english_response = res.json().get("response", "")
    print(f"📥 LightRAG English response: {english_response[:100]}...")
    
    # Step 4: Translate domain terms in response (e.g., "Invictus" → "ఇన్విక్టస్" for Telugu)
    response_with_terms = translate_to_telugu(english_response, language)
    if english_response != response_with_terms:
        print(f"📖 Domain translation applied to response")
    
    # Step 5: If language is not English, translate the entire response
    if language != "english":
        # Skip translation for "no information" responses to avoid mangling the message
        if "[no-context]" in response_with_terms.lower() or "no information" in response_with_terms.lower():
            print(f"⚠️ No-context response, using Google Translate for proper message")
        
        print(f"🔄 Translating response from English to {language}...")
        try:
            lang_code_map = {
                "telugu": "te", "tamil": "ta", "kannada": "kn", "malayalam": "ml",
                "hindi": "hi", "marathi": "mr", "bengali": "bn", "gujarati": "gu",
                "punjabi": "pa", "odia": "or"
            }
            
            target_lang = lang_code_map.get(language, "en")
            translator = GoogleTranslator(source='en', target=target_lang)
            final_response = translator.translate(response_with_terms)
            print(f"✅ Response translated to {language}: {final_response[:100]}...")
            return final_response
        except Exception as e:
            print(f"⚠️ Translation failed: {e}, returning English with domain terms")
            return response_with_terms
    
    # For English, return response with domain terms
    print(f"✅ English response ready")
    return response_with_terms

