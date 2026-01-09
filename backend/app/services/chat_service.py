from bson import ObjectId
from datetime import datetime
import time
from app.db.mongo import messages, sessions
from app.models.message import message_doc
from app.services.lightrag_service import query_lightrag
from app.services.local_knowledge_base import synthesize_answer
from app.utils.cleaner import clean_response
from app.utils.language_detector import detect_language
from deep_translator import GoogleTranslator
from app.utils.domain_translator import translate_to_telugu
from app.services.chat_rules import (
    is_dosage_question,
    is_factual_company_question,
    is_direct_knowledge_question,
    is_greeting_or_acknowledgment,
    is_problem_diagnosis_question,
    is_summary_or_list_question
)
from app.services.followup_service import (
    needs_follow_up,
    generate_followup,
    can_finalize,
    MAX_FOLLOWUPS
)

def generate_title(text: str) -> str:
    words = text.strip().split()
    return " ".join(words[:6]).capitalize()

def get_history(session_id):
    cursor = messages.find({"session_id": session_id}).sort("created_at", 1)
    return [{"role": m["role"], "content": m["content"]} for m in cursor]

def ensure_language_match(response: str, target_language: str) -> str:
    """Ensure the response matches the target language by force-translating if needed."""
    print(f"🔄 Final translation: Ensuring response is in {target_language}...")
    try:
        # Apply domain translation only for non-English targets to keep product names localized
        response_with_terms = response if target_language == "english" else translate_to_telugu(response, target_language)

        # Then translate the full response (even for English, to normalize mixed-language output)
        lang_code_map = {
            "telugu": "te", "tamil": "ta", "kannada": "kn", "malayalam": "ml",
            "hindi": "hi", "marathi": "mr", "bengali": "bn", "gujarati": "gu",
            "punjabi": "pa", "odia": "or",
            "english": "en"
        }
        target_code = lang_code_map.get(target_language, "en")
        translator = GoogleTranslator(source='auto', target=target_code)
        final_response = translator.translate(response_with_terms)
        print(f"✅ Response translated to {target_language}")
        return final_response
    except Exception as e:
        print(f"⚠️ Final translation failed: {e}")
        return response

def handle_greeting(user_message, language):
    """Handle greetings and acknowledgments in appropriate language with contextual responses"""
    msg_lower = user_message.lower().strip()
    
    # English greetings with contextual responses
    if language == "english":
        if "good morning" in msg_lower or "morning" in msg_lower:
            return "Good morning! I'm FarmVaidya, your agricultural assistant. How can I help you with your farming needs today?"
        elif "good afternoon" in msg_lower or "afternoon" in msg_lower:
            return "Good afternoon! I'm FarmVaidya, here to assist you with your agricultural queries. What can I help you with?"
        elif "good evening" in msg_lower or "evening" in msg_lower:
            return "Good evening! I'm FarmVaidya, your farming expert. How may I assist you today?"
        elif "good night" in msg_lower or "night" in msg_lower:
            return "Good night! Feel free to reach out anytime you need farming assistance. Have a great evening!"
        elif "hi" in msg_lower or "hey" in msg_lower:
            return "Hi there! I'm FarmVaidya, your agricultural assistant. What farming question can I help you with today?"
        elif "hello" in msg_lower or "hii" in msg_lower:
            return "Hello! I'm FarmVaidya, ready to help with all your farming questions. How can I assist you?"
        elif "namaste" in msg_lower:
            return "Namaste! I'm FarmVaidya, your agricultural guide. What can I help you with today?"
        elif "ok" in msg_lower or "okay" in msg_lower or "noted" in msg_lower:
            return "Great! Is there anything else I can help you with regarding your crops or farming?"
        elif "thank" in msg_lower or "thanks" in msg_lower:
            return "You're welcome! Feel free to ask if you need any more farming advice."
        else:
            return "Hello! I'm FarmVaidya, your agricultural assistant. How can I help you today?"
    
    # Telugu greetings with contextual responses
    elif language == "telugu":
        if "శుభోదయం" in user_message or "morning" in msg_lower:
            return "శుభోదయం! నేను ఫార్మ్ వైద్య, మీ వ్యవసాయ సహాయకుడిని. ఈరోజు మీ వ్యవసాయ అవసరాలకు నేను ఎలా సహాయపడగలను?"
        elif "శుభ మధ్యాహ్నం" in user_message or "afternoon" in msg_lower:
            return "శుభ మధ్యాహ్నం! నేను ఫార్మ్ వైద్య. మీ వ్యవసాయ ప్రశ్నలకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను. నేను మీకు ఏమి సహాయం చేయగలను?"
        elif "శుభ సాయంత్రం" in user_message or "evening" in msg_lower:
            return "శుభ సాయంత్రం! నేను ఫార్మ్ వైద్య, మీ వ్యవసాయ నిపుణుడు. నేను ఈరోజు మీకు ఎలా సహాయపడగలను?"
        elif "శుభ రాత్రి" in user_message or "night" in msg_lower:
            return "శుభ రాత్రి! మీకు వ్యవసాయ సహాయం అవసరమైనప్పుడు ఎప్పుడైనా సంప్రదించండి. మంచి సాయంత్రం!"
        elif "హాయ్" in user_message or "hi" in msg_lower or "hey" in msg_lower:
            return "హాయ్! నేను ఫార్మ్ వైద్య, మీ వ్యవసాయ సహాయకుడు. ఈరోజు నేను మీకు ఏ వ్యవసాయ ప్రశ్నలో సహాయం చేయగలను?"
        elif "హలో" in user_message or "hello" in msg_lower:
            return "హలో! నేను ఫార్మ్ వైద్య, మీ అన్ని వ్యవసాయ ప్రశ్నలకు సహాయం చేయడానికి సిద్ధంగా ఉన్నాను. నేను మీకు ఎలా సహాయపడగలను?"
        elif "నమస్కారం" in user_message or "namaste" in msg_lower:
            return "నమస్కారం! నేను ఫార్మ్ వైద్య, మీ వ్యవసాయ మార్గదర్శి. ఈరోజు నేను మీకు ఏమి సహాయం చేయగలను?"
        elif "సరే" in user_message or "ఓకే" in user_message or "ok" in msg_lower or "noted" in msg_lower:
            return "బాగుంది! మీ పంటలు లేదా వ్యవసాయానికి సంబంధించి నేను మీకు ఇంకా ఏదైనా సహాయం చేయగలనా?"
        elif "థాంక్" in user_message or "ధన్యవాద" in user_message or "thank" in msg_lower:
            return "మీకు స్వాగతం! మీకు మరింత వ్యవసాయ సలహా అవసరమైతే అడగడానికి సంకోచించకండి."
        else:
            return "హలో! నేను ఫార్మ్ వైద్య, మీ వ్యవసాయ సహాయకుడిని. ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?"
    
    # Hindi greetings with contextual responses
    elif language == "hindi":
        if "शुभ प्रभात" in user_message or "सुप्रभात" in user_message or "morning" in msg_lower:
            return "शुभ प्रभात! मैं फार्मवैद्य हूं, आपका कृषि सहायक। आज मैं आपकी खेती की जरूरतों में कैसे मदद कर सकता हूं?"
        elif "शुभ दोपहर" in user_message or "afternoon" in msg_lower:
            return "शुभ दोपहर! मैं फार्मवैद्य हूं। मैं आपके कृषि प्रश्नों में सहायता के लिए यहां हूं। मैं आपकी कैसे मदद कर सकता हूं?"
        elif "शुभ संध्या" in user_message or "evening" in msg_lower:
            return "शुभ संध्या! मैं फार्मवैद्य हूं, आपका कृषि विशेषज्ञ। मैं आज आपकी कैसे सहायता कर सकता हूं?"
        elif "शुभ रात्रि" in user_message or "night" in msg_lower:
            return "शुभ रात्रि! जब भी आपको खेती में सहायता की आवश्यकता हो, बेझिझक संपर्क करें। शुभ संध्या!"
        elif "हाय" in user_message or "hi" in msg_lower or "hey" in msg_lower:
            return "हाय! मैं फार्मवैद्य हूं, आपका कृषि सहायक। आज मैं आपके किस खेती के सवाल में मदद कर सकता हूं?"
        elif "हेलो" in user_message or "hello" in msg_lower:
            return "हेलो! मैं फार्मवैद्य हूं, आपके सभी खेती के सवालों में मदद के लिए तैयार। मैं आपकी कैसे सहायता कर सकता हूं?"
        elif "नमस्ते" in user_message or "नमस्कार" in user_message or "namaste" in msg_lower:
            return "नमस्ते! मैं फार्मवैद्य हूं, आपका कृषि मार्गदर्शक। आज मैं आपकी क्या मदद कर सकता हूं?"
        elif "ठीक है" in user_message or "ओके" in user_message or "ok" in msg_lower or "noted" in msg_lower:
            return "बढ़िया! क्या मैं आपकी फसलों या खेती के बारे में और किसी चीज़ में मदद कर सकता हूं?"
        elif "धन्यवाद" in user_message or "शुक्रिया" in user_message or "thank" in msg_lower:
            return "आपका स्वागत है! यदि आपको और खेती की सलाह चाहिए तो बेझिझक पूछें।"
        else:
            return "नमस्ते! मैं फार्मवैद्य हूं, आपका कृषि सहायक। मैं आज आपकी कैसे मदद कर सकता हूं?"
    
    # Default fallback
    return "Hello! I'm FarmVaidya, your agricultural assistant. How can I help you today?"

def handle_chat(session_id, user_message):
    print("🔥 NEW HANDLE_CHAT EXECUTED")
    start_time = time.time()
    
    # Detect language of user's message
    t1 = time.time()
    detected_language = detect_language(user_message)
    print(f"🌍 Detected language: {detected_language} (took {time.time()-t1:.2f}s)")
    print(f"📝 User message: {user_message}")
    print(f"🔤 Message length: {len(user_message)} characters")
    
    # Count non-English characters for debugging
    non_english_chars = sum(1 for c in user_message if ord(c) > 127)
    print(f"🔤 Non-English characters: {non_english_chars}")
    
    # Save user message
    t2 = time.time()
    messages.insert_one(message_doc(session_id, "user", user_message))
    print(f"💾 Saved user message (took {time.time()-t2:.2f}s)")

    # Update session timestamp and language
    sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$set": {
                "updated_at": datetime.utcnow(),
                "language": detected_language
            }
        }
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

    # 👋 GREETING / ACKNOWLEDGMENT → Respond politely in same language
    if is_greeting_or_acknowledgment(user_message):
        print("✅ GREETING/ACKNOWLEDGMENT DETECTED")
        answer = handle_greeting(user_message, detected_language)
        messages.insert_one(message_doc(session_id, "assistant", answer))
        print(f"⏱️ Total time: {time.time()-start_time:.2f}s")
        return answer

    # Fetch session data early for all subsequent logic
    session = sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        # Session not found - create a new one or handle gracefully
        print(f"⚠️ Session {session_id} not found in database")
        session = {}

    # � FACTUAL / COMPANY QUESTIONS → NEVER FOLLOW-UP, NO HISTORY
    # Don't pass history for factual questions to avoid entity confusion
    # Use factual=True to avoid forcing answers when no information exists
    if is_factual_company_question(user_message):
        print("✅ FACTUAL/COMPANY QUESTION - DIRECT ANSWER (NO HISTORY)")
        t3 = time.time()
        answer = clean_response(query_lightrag(user_message, [], language=detected_language, factual=True))
        answer = ensure_language_match(answer, detected_language)
        print(f"🤖 LightRAG query (took {time.time()-t3:.2f}s)")
        messages.insert_one(message_doc(session_id, "assistant", answer))
        print(f"⏱️ Total time: {time.time()-start_time:.2f}s")
        return answer

    # 📚 DIRECT PRODUCT / KNOWLEDGE → answer directly (CHECK BEFORE DOSAGE!)
    # This must come BEFORE dosage to handle "what is P-Factor" correctly
    if is_direct_knowledge_question(user_message):
        print("✅ DIRECT KNOWLEDGE QUESTION")
        t3 = time.time()
        
        # Use detected language (not session) - English question gets English answer
        print(f"🌐 Using detected language for KNOWLEDGE: {detected_language}")
        print(f"🔍 Original question: {user_message}")
        
        # Check if this is a follow-up reference
        from app.services.chat_rules import is_followup_reference
        is_followup = is_followup_reference(user_message)
        print(f"🔗 Is follow-up? {is_followup}")
        
        # Always get recent context for product/knowledge questions - needed for crop context
        recent_history = get_history(session_id)[-10:]  # Get more context (last 10 messages)
        print(f"📚 History available: {len(recent_history)} messages")
        
        # Build context from user messages in history (crop mentions, conditions, etc.)
        user_messages = [msg["content"] for msg in recent_history if msg["role"] == "user"]
        context_text = " ".join(user_messages[-4:])  # Last 4 user messages for context
        
        if is_followup:
            # Use recent context for follow-ups and yes/no answers
            print("🔗 Follow-up/context-dependent response detected, using recent context")
            
            # Build contextual query with conversation history
            context_messages = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in recent_history[-5:]
            ])
            
            comprehensive_query = f"""You are FarmVaidya, an agricultural advisory assistant in an ongoing conversation.

Recent Conversation:
{context_messages}

Current User Question: {user_message}

Task: Answer the current question using the context from recent conversation. The user is referring to something discussed earlier. Be specific and helpful.

Guidelines:
- If user says "yes", "no", "okay" - understand what they're responding to from context
- If user asks about "it", "that product", "its dosage" - refer to the product mentioned earlier
- Provide specific information (exact dosages, timings, methods)
- Respond in the same language as the user's question
- Be conversational and acknowledge the ongoing discussion"""
            
            print(f"📝 Comprehensive query: {comprehensive_query[:150]}...")
            
            # Use 'local' mode for follow-ups - pass empty history since we built comprehensive query
            answer = clean_response(query_lightrag(comprehensive_query, [], mode="local", language=detected_language))
        else:
            # General knowledge/advice question - use crop context if available, but don't demand it
            print("📝 General knowledge/advice question")
            
            # Check if crop/context is mentioned in current message or recent history
            from app.services.followup_service import extract_provided_info
            history_with_current = recent_history + [{"role": "user", "content": user_message}]
            provided_info = extract_provided_info(history_with_current)
            
            # Build optional context if crop info available
            crop_context = ""
            if provided_info["crop_provided"] or context_text.strip():
                context_messages = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in recent_history[-4:]
                ])
                if context_messages.strip():
                    crop_context = f"""

Conversation Context (farmer mentioned some details):
{context_messages}

Use the context if relevant to the question, otherwise provide general advice."""
            
            # General advice/knowledge query with optional context
            comprehensive_query = f"""You are FarmVaidya, an expert agricultural advisor helping farmers.

User Question: {user_message}
{crop_context}

Task: Provide practical, actionable agricultural advice.

Guidelines:
- If crop/conditions mentioned in context, tailor advice accordingly
- If no specific context, provide general best practices
- Include specific recommendations (fertilizers, timing, doses when applicable)
- Be comprehensive but organized - step-by-step advice
- Explain WHY each recommendation works
- Consider growth stages, soil health, water management
- Mention specific products from knowledge base if available and relevant
- Respond in the same language as the question
- Be farmer-friendly and practical"""
            
            print(f"📝 General advice with optional context: {comprehensive_query[:150]}...")
            
            # Use 'mix' mode for comprehensive retrieval with context awareness
            answer = clean_response(query_lightrag(comprehensive_query, [], mode="mix", language=detected_language))
            
            # If no crop context was provided, add interactive follow-up question
            if not provided_info["crop_provided"]:
                print("💬 No crop mentioned, adding interactive follow-up")
                
                # Language-specific follow-up questions
                followup_questions = {
                    "english": "\n\nIs there any specific crop you'd like to know about?",
                    "telugu": "\n\nమీరు ఏదైనా నిర్దిష్ట పంట గురించి తెలుసుకోవాలనుకుంటున్నారా?",
                    "hindi": "\n\nक्या आप किसी विशेष फसल के बारे में जानना चाहेंगे?",
                    "tamil": "\n\nநீங்கள் ஏதேனும் குறிப்பிட்ட பயிரைப் பற்றி அறிய விரும்புகிறீர்களா?",
                    "kannada": "\n\nನೀವು ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಬೆಳೆಯ ಬಗ್ಗೆ ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೀರಾ?",
                    "malayalam": "\n\nനിങ്ങൾക്ക് ഏതെങ്കിലും പ്രത്യേക വിളയെക്കുറിച്ച് അറിയണോ?",
                    "marathi": "\n\nतुम्हाला कोणत्याही विशिष्ट पिकाबद्दल जाणून घ्यायचे आहे का?",
                    "bengali": "\n\nআপনি কি কোনো নির্দিষ্ট ফসল সম্পর্কে জানতে চান?",
                    "gujarati": "\n\nશું તમે કોઈ વિશિષ્ટ પાક વિશે જાણવા માંગો છો?",
                    "punjabi": "\n\nਕੀ ਤੁਸੀਂ ਕਿਸੇ ਖਾਸ ਫਸਲ ਬਾਰੇ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ?"
                }
                
                interactive_followup = followup_questions.get(detected_language, followup_questions["english"])
                answer = answer + interactive_followup
            
            answer = ensure_language_match(answer, detected_language)
        
        print(f"🤖 LightRAG query (took {time.time()-t3:.2f}s)")
        messages.insert_one(message_doc(session_id, "assistant", answer))
        print(f"⏱️ Total time: {time.time()-start_time:.2f}s")
        return answer

    # � DOSAGE → direct answer (AFTER knowledge check)
    if is_dosage_question(user_message):
        print("✅ DOSAGE BRANCH RETURNING LIGHTRAG ANSWER")
        t3 = time.time()
        
        # Check if this is a follow-up reference (e.g., "its dosage", "that product")
        from app.services.chat_rules import is_followup_reference
        is_followup = is_followup_reference(user_message)
        
        # Use detected language for dosage questions
        # English question → English answer, Telugu → Telugu
        print(f"🌐 Using detected language for DOSAGE: {detected_language}")
        print(f"🔍 Original question: {user_message}")
        print(f"🔗 Is follow-up? {is_followup}")
        
        if is_followup:
            # For follow-up questions, extract product from history and build comprehensive query
            print("🔗 Follow-up reference detected, extracting product from context")
            recent_history = get_history(session_id)[-6:]  # Last 6 messages for more context
            
            # Build comprehensive query using ONLY user messages (not assistant responses)
            user_messages = [msg["content"] for msg in recent_history if msg["role"] == "user"]
            context_text = " ".join(user_messages[-3:])  # Last 3 user messages
            comprehensive_query = f"{context_text}. Now answer: {user_message}"
            
            print(f"📝 Comprehensive query (user messages only): {comprehensive_query[:150]}...")
            answer = clean_response(query_lightrag(comprehensive_query, [], mode="local", language=detected_language))
        else:
            # For direct dosage questions, no history needed
            print("📝 Direct dosage question, no context needed")
            answer = clean_response(query_lightrag(user_message, [], mode="naive", language=detected_language))
        
        print(f"🤖 LightRAG query (took {time.time()-t3:.2f}s)")
        messages.insert_one(message_doc(session_id, "assistant", answer))
        print(f"⏱️ Total time: {time.time()-start_time:.2f}s")
        return answer
    # 📋 SUMMARY OR LIST QUESTIONS → COMPILE FROM CONVERSATION HISTORY
    # These ask for recaps/lists of previously discussed information
    if is_summary_or_list_question(user_message):
        print("✅ SUMMARY/LIST QUESTION - COMPILING FROM HISTORY")
        t3 = time.time()
        
        # Get conversation history
        history = get_history(session_id)
        print(f"📚 Total conversation messages: {len(history)}")
        
        import re
        
        # Product keywords with variants (English and local language)
        product_variants = {
            "invictus": ["invictus", "ఇన్విక్టస్"],
            "poshak": ["poshak", "పోషక్"],
            "p-factor": ["p-factor", "pfactor", "p factor", "పీ-ఫాక్టర్", "పీ ఫ్యాక్టర్"],
            "n-factor": ["n-factor", "nfactor", "n factor", "ఎన్-ఫాక్టర్", "ఎన్ ఫ్యాక్టర్"],
            "k-factor": ["k-factor", "kfactor", "k factor", "కె-ఫాక్టర్"],
            "aadhaar": ["aadhaar", "aadhaar gold", "అధార్"],
            "biofactor": ["biofactor", "బయోఫ్యాక్టర్"],
            "zn-factor": ["zn-factor", "జెడ్ఎన్-ఫాక్టర్"]
        }
        
        # Step 1: Identify which products USER explicitly asked about
        print("🔍 Identifying products USER asked about...")
        asked_products = {}  # normalized_name: (original_name, count)
        
        for msg in history:
            if msg["role"] == "user":
                user_text = msg["content"].lower()
                for norm_name, variants in product_variants.items():
                    for variant in variants:
                        if variant.lower() in user_text:
                            if norm_name not in asked_products:
                                asked_products[norm_name] = (norm_name, 0)
                            asked_products[norm_name] = (norm_name, asked_products[norm_name][1] + 1)
        
        print(f"📊 Products USER asked about: {list(asked_products.keys())}")
        
        # Step 2: Extract dosage info ONLY for products user explicitly asked about
        dosage_info = {}
        
        # Units in different languages - including actual forms found in responses
        unit_patterns = [
            # English variants
            "litre", "liter", "lt", "ltr",
            # Hindi variants  
            "लीटर", "किलोग्राम", "ग्राम", "मिली",
            # Telugu variants - actual forms found in responses
            "లీటరు", "కిలోల", "గ్రాముల", "మిల్లీ",
            # Generic forms
            "kg", "kilo", "ml", "gm", "gram"
        ]
        
        for msg in history:
            if msg["role"] == "assistant":
                content = msg["content"]
                
                # For each product the user asked about
                for norm_name, variants in product_variants.items():
                    # Only process if user asked about this product
                    if norm_name not in asked_products:
                        continue
                    
                    # Skip if already extracted
                    if norm_name in dosage_info:
                        continue
                    
                    # Look for dosage pattern in response
                    for variant in variants:
                        # Build pattern with all unit types
                        units_pattern = "|".join(unit_patterns)
                        pattern = rf'{re.escape(variant)}.*?(\d+(?:\.\d+)?)\s*({units_pattern})'
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            dosage_amount = match.group(1)
                            dosage_unit = match.group(2)
                            dosage_info[norm_name] = f"{dosage_amount} {dosage_unit}"
                            print(f"📍 Found {norm_name}: {dosage_amount} {dosage_unit}")
                            break  # Move to next product once found
        
        print(f"📊 Extracted dosages for asked products: {dosage_info}")
        
        # Step 3: Format the compiled response
        if dosage_info:
            # Build formatted response in user's detected language
            response_lines = ["Here are all the dosages we have discussed:"]
            
            # Maintain order of asked products
            for product_name in asked_products.keys():
                if product_name in dosage_info:
                    dosage = dosage_info[product_name]
                    # Normalize product name for display
                    display_product = product_name.upper().replace("-", "-")
                    response_lines.append(f"- {display_product}: {dosage} per acre")
            
            compiled_answer = "\n".join(response_lines)
            
            # Ensure response is in user's language
            compiled_answer = ensure_language_match(compiled_answer, detected_language)
        else:
            # No dosage info found, still ask LightRAG but with context
            print("⚠️ No dosage info found in history, querying LightRAG with context")
            recent_history = get_history(session_id)[-6:]
            user_messages = [msg["content"] for msg in recent_history if msg["role"] == "user"]
            context_text = " ".join(user_messages)
            comprehensive_query = f"User's previous questions and context: {context_text}\nNow answer: {user_message}"
            compiled_answer = clean_response(query_lightrag(comprehensive_query, [], mode="mix", language=detected_language))
            compiled_answer = ensure_language_match(compiled_answer, detected_language)
        
        print(f"✅ Compiled response (took {time.time()-t3:.2f}s)")
        messages.insert_one(message_doc(session_id, "assistant", compiled_answer))
        print(f"⏱️ Total time: {time.time()-start_time:.2f}s")
        return compiled_answer
    # �🔁 FOLLOW-UP LOGIC FOR PROBLEM DIAGNOSIS
    # Always ask follow-ups for diagnosis until we have enough context (language-agnostic)
    t_followup = time.time()
    if is_problem_diagnosis_question(user_message) or session.get("awaiting_followup"):
        # If this is a NEW problem diagnosis question and we're not already in follow-up mode,
        # reset the follow-up state (user asking a new question after previous conversation)
        if is_problem_diagnosis_question(user_message) and not session.get("awaiting_followup"):
            # Check if user already provided comprehensive information in their question
            # OR if we can use info from recent conversation history
            from app.services.followup_service import extract_provided_info
            
            # Check both current message AND recent history (last 10 messages to capture recent context)
            t_hist = time.time()
            recent_history = get_history(session_id)[-10:]  # Last 10 messages
            provided = extract_provided_info(recent_history)
            print(f"🔍 Extracted provided info (took {time.time()-t_hist:.2f}s)")
            print(f"📊 Provided info: {provided}")
            
            # If user provided crop+stage AND soil info, skip follow-ups
            has_crop_info = provided["crop_provided"] and provided["stage_provided"]
            has_soil_info = provided["soil_provided"]
            
            # Check if we have ENOUGH information to answer (not necessarily ALL fields)
            # Essential: crop + stage OR problem description with symptoms
            # Nice to have: soil, irrigation, fertilizers (can still answer without these)
            has_essential_info = has_crop_info or (provided["soil_provided"] and provided["irrigation_provided"])
            
            if has_essential_info:
                # User gave enough info, skip follow-ups entirely
                print("✅ USER PROVIDED SUFFICIENT INFO, SKIPPING FOLLOW-UPS AND ANSWERING DIRECTLY")
                sessions.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$set": {"followup_count": MAX_FOLLOWUPS, "awaiting_followup": False}}
                )
                session["followup_count"] = MAX_FOLLOWUPS
                session["awaiting_followup"] = False
                # Continue to final answer generation (don't ask follow-ups)
            else:
                # Check if crop+stage is in the CURRENT message specifically
                current_msg_history = [{"role": "user", "content": user_message}]
                current_provided = extract_provided_info(current_msg_history)
                
                if current_provided["crop_provided"] and current_provided["stage_provided"]:
                    # User mentioned crop+stage in current question, use lighter follow-up flow
                    # Only need to ask for missing info (soil/irrigation/fertilizers)
                    print("✅ USER PROVIDED CROP+STAGE IN QUESTION, REDUCED FOLLOW-UPS")
                    # Start at count 1 (skip crop/stage question)
                    sessions.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$set": {"followup_count": 1, "awaiting_followup": False}}
                    )
                    session["followup_count"] = 1
                    session["awaiting_followup"] = False
                else:
                    # Reset for new question - need to ask follow-ups
                    sessions.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$set": {"followup_count": 0, "awaiting_followup": False}}
                    )
                    session["followup_count"] = 0
                    session["awaiting_followup"] = False
        
        # Default followup counter to 0 if missing
        if session.get("followup_count") is None:
            session["followup_count"] = 0

        # Only generate follow-ups if we haven't reached finalization threshold
        if not can_finalize(session):
            print("✅ GENERATING FOLLOW-UP QUESTION")
            t_gen = time.time()
            # For diagnosis questions, pass is_diagnosis=True to skip soil/irrigation/fertilizer questions
            followup_q = generate_followup(session_id, detected_language, user_message, is_diagnosis=is_problem_diagnosis_question(user_message))
            print(f"❓ Generated follow-up (took {time.time()-t_gen:.2f}s)")
            
            # If generate_followup returns None, it means all info is collected
            if followup_q is None:
                print("✅ ALL INFO COLLECTED BY generate_followup, PROCEEDING TO FINAL ANSWER")
                sessions.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$set": {"awaiting_followup": False, "followup_count": MAX_FOLLOWUPS}}
                )
                # Don't return, continue to final answer generation
            else:
                messages.insert_one(message_doc(session_id, "assistant", followup_q))
                return followup_q

        # Enough followups → finalize and continue to final answer
        print("✅ FINALIZING AFTER FOLLOW-UPS - HAVE SUFFICIENT CONTEXT")
        sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"awaiting_followup": False}}
        )

    # ✅ FINAL ANSWER - synthesize all collected context
    print("✅ GENERATING FINAL ANSWER WITH COLLECTED CONTEXT")
    history = get_history(session_id)[:-1]
    
    # For diagnosis questions, build comprehensive query from follow-up context
    if is_problem_diagnosis_question(user_message) and session.get("followup_count", 0) > 0:
        # Only use messages from AFTER the last reset (the current question's follow-ups)
        # Find the index of the current user question (the one that started this follow-up flow)
        messages_list = list(history)
        
        # Find the last occurrence of a problem diagnosis question before this one
        # Work backwards to find where the current follow-up sequence started
        current_question_idx = -1
        for i in range(len(messages_list) - 1, -1, -1):
            if messages_list[i]["role"] == "user":
                current_question_idx = i
                break
        
        # Now look backwards from current question to find where this follow-up sequence started
        # It starts with the first user message that triggered follow-ups
        followup_start_idx = current_question_idx
        for i in range(current_question_idx - 1, -1, -1):
            if messages_list[i]["role"] == "assistant":
                # Check if this is a follow-up question
                msg_content = messages_list[i]["content"]
                is_followup_q = any(q in msg_content for q in [
                    "What is your crop name and growth stage",
                    "What is your soil type",
                    "What fertilizers",
                    "మీ పంట పేరు",
                    "మీ నేల రకం",
                    "ఏ ఎరువులు",
                    "आपकी फसल का नाम",
                    "आपकी मिट्टी का प्रकार",
                    "कौन-कौन से उर्वरक"
                ])
                if not is_followup_q:
                    # This is not a follow-up question, so the sequence starts after this
                    followup_start_idx = i + 1
                    break
            elif messages_list[i]["role"] == "user":
                followup_start_idx = i
        
        # Extract only the user messages from the current follow-up sequence
        recent_user_messages = [msg["content"] for msg in messages_list[followup_start_idx:] if msg["role"] == "user"]
        
        # Pattern: [original_question, ans1, ans2, ans3, ...]
        original_question = recent_user_messages[0] if len(recent_user_messages) > 0 else user_message
        ans1 = recent_user_messages[1] if len(recent_user_messages) > 1 else "Not provided"
        ans2 = recent_user_messages[2] if len(recent_user_messages) > 2 else "Not provided"
        ans3 = recent_user_messages[3] if len(recent_user_messages) > 3 else "Not provided"
        
        # Build comprehensive query with ALL context
        comprehensive_query = f"""You are FarmVaidya, an expert agricultural diagnostic advisor. Provide a DETAILED, ACTIONABLE solution.

FARMER'S SITUATION:
Problem: {original_question}
Crop & Stage: {ans1}
Soil & Irrigation: {ans2}
Fertilizers/Sprays Used: {ans3}

RESPONSE REQUIREMENTS (MUST INCLUDE ALL):
1. DIAGNOSIS: Identify the specific problem based on symptoms and conditions provided
2. ROOT CAUSE: Explain WHY this problem occurred (soil deficiency, improper watering, etc.)
3. IMMEDIATE ACTIONS: What to do RIGHT NOW to stop the problem
   - Specific product names
   - Exact doses (kg, ml, liters per acre)
   - Application method (soil, foliar spray, drip)
4. TIMELINE: When to apply (days, growth stage)
5. PREVENTION: How to prevent this in future crops
6. MONITORING: What to watch for to confirm treatment is working

BE SPECIFIC:
- Do NOT say "use appropriate dose" - say "use 50 kg per acre"
- Do NOT say "spray when needed" - say "spray at 7am or 5pm, avoid noon"
- Mention exact product names if relevant (P-Factor, K-Factor, Invictus, etc.)
- Include expected results and timeframe to see improvement

LANGUAGE: Respond in the farmer's language (not English unless original was English).
TONE: Practical, encouraging, solution-focused.
"""
        
        print(f"📝 Original Question: {original_question}")
        print(f"📝 Q1 Answer: {ans1}")
        print(f"📝 Q2 Answer: {ans2}")
        print(f"📝 Q3 Answer: {ans3}")
        print(f"📝 Final Query to LightRAG: {comprehensive_query}")
        
        # Try LightRAG first
        t_rag = time.time()
        answer = clean_response(query_lightrag(comprehensive_query, [], language=detected_language))
        answer = ensure_language_match(answer, detected_language)
        print(f"🤖 LightRAG final answer (took {time.time()-t_rag:.2f}s)")
        
        # If LightRAG returns [no-context] or empty, use local knowledge base
        if "[no-context]" in answer or not answer or answer.strip() == "":
            print("⚠️ LightRAG returned no context, using local knowledge base...")
            
            # Parse the collected information
            soil_type = ans2.lower().split()[0] if ans2 and "not provided" not in ans2.lower() else "loam"
            growth_stage = ans1.lower().split()[0] if ans1 and "not provided" not in ans1.lower() else "mid"
            irrigation = "drip" if "drip" in ans2.lower() else ("sprinkler" if "sprinkler" in ans2.lower() else "flood")
            
            try:
                # Use local knowledge base
                t_synth = time.time()
                answer = synthesize_answer(soil_type, growth_stage, irrigation, ans3)
                answer = ensure_language_match(answer, detected_language)
                print(f"✅ Generated answer using local knowledge base (took {time.time()-t_synth:.2f}s)")
            except Exception as e:
                print(f"❌ Error in local knowledge base: {e}")
                answer = f"Based on your {growth_stage}-stage crop in {soil_type} soil with {irrigation} irrigation: Please consult our detailed guides or contact local agricultural experts for comprehensive fertilizer and irrigation recommendations."
                answer = ensure_language_match(answer, detected_language)
    else:
        # Not a diagnosis question or no follow-ups collected
        # Build a user-only context to avoid language contamination from assistant messages
        t_direct = time.time()
        recent_history = get_history(session_id)[-6:]
        user_context = [m["content"] for m in recent_history if m["role"] == "user"]
        context_block = " \n".join(user_context)
        comprehensive_query = (
            "You are an agronomy assistant. Use the provided user context and question. "
            "If the context already has enough details, give a direct, concise answer. "
            "If a critical detail is missing, ask ONLY one concise follow-up question to collect that specific detail. "
            "Never repeat follow-ups already asked.\n\n"
            f"Context:\n{context_block}\n\nQuestion:\n{user_message}\n\nAnswer:"
        )

        answer = clean_response(query_lightrag(comprehensive_query, [], language=detected_language))
        answer = ensure_language_match(answer, detected_language)
        print(f"🤖 Direct LightRAG query (took {time.time()-t_direct:.2f}s)")
    
    t_final_save = time.time()
    messages.insert_one(message_doc(session_id, "assistant", answer))
    print(f"💾 Final save (took {time.time()-t_final_save:.2f}s)")
    print(f"⏱️ Total handle_chat time: {time.time()-start_time:.2f}s")
    return answer
