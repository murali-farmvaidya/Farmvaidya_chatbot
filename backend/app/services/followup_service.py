from app.services.lightrag_service import query_lightrag
from app.db.mongo import sessions, messages
from bson import ObjectId

MAX_FOLLOWUPS = 3

def needs_follow_up(session_id: str, language: str = "english") -> bool:
    """
    Determine if a follow-up question is needed
    
    Args:
        session_id: The session ID
        language: The detected language of the user's question
    """
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages.find({"session_id": session_id}).sort("created_at", 1)
    ]

    language_instructions = {
        "telugu": "మీరు వ్యవసాయ సహాయకుడు. రైతు నిర్దిష్ట వివరాలు (పంట, పెరుగుదల దశ, నేల, లక్షణాలు, స్థానం) అవసరమైతే మాత్రమే ఫాలో-అప్ ప్రశ్న అడగండి. ANSWER_DIRECTLY లేదా ASK_FOLLOW_UP మాత్రమే సమాధానం ఇవ్వండి.",
        "hindi": "आप एक कृषि सहायक हैं। केवल तभी अनुवर्ती प्रश्न पूछें जब किसान-विशिष्ट इनपुट (फसल, विकास चरण, मिट्टी, लक्षण, स्थान) की आवश्यकता हो। केवल ANSWER_DIRECTLY या ASK_FOLLOW_UP के साथ उत्तर दें।",
        "english": "You are an agriculture assistant. Ask a follow-up question ONLY IF the answer depends on farmer-specific inputs (crop, growth stage, soil, symptoms, location). Reply ONLY with: ANSWER_DIRECTLY or ASK_FOLLOW_UP"
    }

    query_text = language_instructions.get(language, language_instructions["english"])
    
    res = query_lightrag(query_text, history, mode="bypass", language=language)
    decision = res.strip().upper()
    
    # Be more strict - only ask follow-up if explicitly needed
    return "ASK_FOLLOW_UP" in decision or "FOLLOW" in decision


def extract_provided_info(conversation_history: list) -> dict:
    """
    Extract information already provided across ALL messages in the conversation
    Args:
        conversation_history: List of message dicts with 'role' and 'content' keys
    Returns dict with keys: crop_provided, stage_provided, soil_provided, irrigation_provided, fertilizer_provided
    """
    # Combine all user messages to analyze
    all_user_text = " ".join([msg["content"].lower() for msg in conversation_history if msg["role"] == "user"])
    
    # Common crop names
    crop_keywords = ["paddy", "rice", "wheat", "cotton", "tomato", "chili", "maize", "corn", 
                     "వరి", "పనస", "రైస్", "వరి", "టమాటా", "మొక్కజొన్న",
                     "धान", "गेहूं", "कपास", "टमाटर", "मिर्च", "मक्का"]
    
    # Growth stages
    stage_keywords = {
        "early": ["early", "initial", "starting", "beginning", "vegetative", "ప్రారంభ", "शुरुआत"],
        "mid": ["mid", "middle", "flowering", "మధ్య", "मध्य"],
        "final": ["final", "near harvest", "harvest", "mature", "ripening", "పండిన", "अंतिम", "कटाई"]
    }
    
    # Soil types
    soil_keywords = ["red", "black", "loam", "clay", "sandy", "soil",
                     "ఎర్ర", "నల్ల", "నేల", "लाल", "काली", "मिट्टी"]
    
    # Irrigation methods
    irrigation_keywords = ["drip", "sprinkler", "flood", "irrigation", 
                          "డ్రిప్", "स्प्रिंकलर"]
    
    # Fertilizer mentions
    fertilizer_keywords = ["fertilizer", "fertiliser", "npk", "urea", "dap", "not used", "no fertilizer",
                          "nothing", "none", "not", "no spray",
                          "ఎరువు", "उर्वरक", "వాడలేదు", "इस्तेमाल", "లేదు"]
    
    info = {
        "crop_provided": any(kw in all_user_text for kw in crop_keywords),
        "stage_provided": any(any(kw in all_user_text for kw in stages) for stages in stage_keywords.values()),
        "soil_provided": any(kw in all_user_text for kw in soil_keywords),
        "irrigation_provided": any(kw in all_user_text for kw in irrigation_keywords),
        "fertilizer_provided": any(kw in all_user_text for kw in fertilizer_keywords)
    }
    
    return info


def generate_followup(session_id: str, language: str = "english", user_message: str = "") -> str:
    """
    Generate an intelligent follow-up question based on what's already provided
    
    Args:
        session_id: The session ID
        language: The detected language of the user's question
        user_message: The user's original message (not used anymore, kept for compatibility)
    """
    # Get what's already been asked/provided
    session_doc = sessions.find_one({"_id": ObjectId(session_id)}) or {}
    current_count = session_doc.get("followup_count", 0)
    
    # Get conversation history to see what's been provided
    history = list(messages.find({"session_id": session_id}).sort("created_at", 1))
    
    # Convert to dict format for extract_provided_info
    history_dicts = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    
    # Extract info from ALL user messages in the conversation
    provided_info = extract_provided_info(history_dicts)
    
    print(f"📊 Provided info analysis: {provided_info}")
    
    # Define questions in each language
    questions = {
        "telugu": {
            "crop_stage": "మీ పంట పేరు మరియు పెరుగుదల దశ (ప్రారంభం/మధ్య/పండిన తర్వాత) ఏమిటి?",
            "soil_irrigation": "మీ నేల రకం (ఎర్ర/నల్ల/లోమీ) మరియు నీటిపారుదల విధానం (డ్రిప్/స్ప్రింక్లర్/వరద) ఏమిటి?",
            "fertilizers": "ఇప్పటివరకు ఏ ఎరువులు లేదా మందులు వాడారా? ఉంటే పేర్లు/మోతాదులు చెప్పండి."
        },
        "hindi": {
            "crop_stage": "आपकी फसल का नाम और विकास चरण (शुरुआत/मध्य/कटाई के पास) क्या है?",
            "soil_irrigation": "आपकी मिट्टी का प्रकार (लाल/काली/दोमट) और सिंचाई विधि (ड्रिप/स्प्रिंकलर/बाढ़) क्या है?",
            "fertilizers": "अब तक कौन-कौन से उर्वरक या दवाइयाँ इस्तेमाल की हैं? नाम/मात्रा बताएं।"
        },
        "english": {
            "crop_stage": "What is your crop name and growth stage (early/mid/near harvest)?",
            "soil_irrigation": "What is your soil type (red/black/loam) and irrigation method (drip/sprinkler/flood)?",
            "fertilizers": "What fertilizers or sprays have you already used? Please mention names and doses."
        }
    }
    
    lang_questions = questions.get(language, questions["english"])
    
    # Determine what to ask based on what's missing AND what's already been asked
    # Check assistant messages to see what questions were already asked
    asked_questions = {msg["content"] for msg in history if msg["role"] == "assistant"}
    
    # Build priority list of questions to ask (only ask if not already asked)
    questions_to_ask = []
    
    if not provided_info["crop_provided"] or not provided_info["stage_provided"]:
        if lang_questions["crop_stage"] not in asked_questions:
            questions_to_ask.append(lang_questions["crop_stage"])
    
    if not provided_info["soil_provided"] or not provided_info["irrigation_provided"]:
        if lang_questions["soil_irrigation"] not in asked_questions:
            questions_to_ask.append(lang_questions["soil_irrigation"])
    
    if not provided_info["fertilizer_provided"]:
        if lang_questions["fertilizers"] not in asked_questions:
            questions_to_ask.append(lang_questions["fertilizers"])
    
    # If no valid questions remain or all info is provided, return None to signal completion
    if not questions_to_ask or all(provided_info.values()):
        print("✅ All required information collected, skipping further follow-ups")
        # Force completion
        sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"followup_count": MAX_FOLLOWUPS, "awaiting_followup": False}}
        )
        return None
    
    # Ask the first remaining question
    question = questions_to_ask[0]
    print(f"❓ Asking follow-up: {question}")
    
    # Update counters/state
    sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$inc": {"followup_count": 1},
            "$set": {"awaiting_followup": True}
        }
    )
    
    return question


def can_finalize(session):
    """Check if we've asked enough follow-ups"""
    return session.get("followup_count", 0) >= MAX_FOLLOWUPS

