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
    
    # Common crop names (more comprehensive)
    crop_keywords = ["paddy", "rice", "wheat", "cotton", "tomato", "chili", "maize", "corn", 
                     "వరి", "పనస", "రైస్", "టమాటా", "మొక్కజొన్న",
                     "धान", "गेहूं", "कपास", "टमाटर", "मिर्च", "मक्का",
                     "crop", "పంట", "फसल"]
    
    # Growth stages (more comprehensive)
    stage_keywords = {
        "early": ["early", "initial", "starting", "beginning", "vegetative", "young", "seedling",
                  "ప్రారంభ", "प्रारंभिक", "शुरुआत", "मुळायम"],
        "mid": ["mid", "middle", "flowering", "budding", "growth",
                "మధ్య", "मध्य", "फूल"],
        "final": ["final", "near harvest", "harvest", "mature", "ripening", "late", "పండిన", "పండు",
                  "अंतिम", "कटाई", "पकना", "पका"]
    }
    
    # Soil types (more comprehensive)
    soil_keywords = ["red", "black", "loam", "clay", "sandy", "soil", "laterite",
                     "ఎర్ర", "నల్ల", "నేల", "मिट्टी", "लाल", "काली", "दोमट"]
    
    # Irrigation methods (more comprehensive)
    irrigation_keywords = ["drip", "sprinkler", "flood", "irrigation", "water", "watering",
                          "డ్రిప్", "స్ప్రింక్లర్", "నీరు", "పారుదల",
                          "ड्रिप", "स्प्रिंकलर", "पानी", "सिंचाई"]
    
    # Fertilizer mentions (including "not used")
    fertilizer_keywords = ["fertilizer", "fertiliser", "npk", "urea", "dap", "not used", "no fertilizer",
                          "nothing", "none", "not", "no spray", "haven't used", "didn't use",
                          "ఎరువు", "వాడలేదు", "లేదు", "उर्वरक", "इस्तेमाल", "नहीं"]
    
    info = {
        "crop_provided": any(kw in all_user_text for kw in crop_keywords),
        "stage_provided": any(any(kw in all_user_text for kw in stages) for stages in stage_keywords.values()),
        "soil_provided": any(kw in all_user_text for kw in soil_keywords),
        "irrigation_provided": any(kw in all_user_text for kw in irrigation_keywords),
        "fertilizer_provided": any(kw in all_user_text for kw in fertilizer_keywords)
    }
    
    return info


def generate_followup(session_id: str, language: str = "english", user_message: str = "", is_diagnosis: bool = False) -> str:
    """
    Generate ONLY ONE follow-up question. Never repeat information already asked.
    For DIAGNOSIS questions: Only need crop name (or symptom description which user already provided)
    For PRODUCT questions: May need crop, stage, soil, irrigation, fertilizers
    
    Args:
        session_id: The session ID
        language: The detected language of the user's question
        user_message: The user's original message
        is_diagnosis: Whether this is a problem diagnosis question (vs product recommendation)
    """
    # Get conversation history
    history = list(messages.find({"session_id": session_id}).sort("created_at", 1))
    history_dicts = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    
    # Extract what user has already provided
    provided_info = extract_provided_info(history_dicts)
    print(f"📊 Already provided: {provided_info}")
    print(f"💊 Question type: {'DIAGNOSIS' if is_diagnosis else 'PRODUCT/GENERAL'}")
    
    # Check what questions have ALREADY BEEN ASKED (critical to avoid repeats)
    asked_assistant_messages = [msg["content"] for msg in history_dicts if msg["role"] == "assistant"]
    
    # Define all possible questions
    crop_q = {
        "english": "Could you tell me your crop name?",
        "telugu": "మీ పంట పేరు ఏమిటో చెప్పగలరా?",
        "hindi": "आपकी फसल का नाम क्या है?"
    }
    
    stage_q = {
        "english": "What growth stage is it in (early/mid/near harvest)?",
        "telugu": "ఇది ఏ పెరుగుదల దశలో ఉంది (ప్రారంభం/మధ్య/పండిన)?",
        "hindi": "यह किस विकास चरण में है (शुरुआत/मध्य/कटाई के पास)?"
    }
    
    soil_irrigation_q = {
        "english": "What's your soil type (red/black/loamy) and irrigation method (drip/sprinkler/flood)?",
        "telugu": "మీ నేల రకం (ఎర్ర/నల్ల/లోమీ) మరియు నీటిపారుదల విధానం (డ్రిప్/స్ప్రింక్లర్/వరద) ఏమిటి?",
        "hindi": "आपकी मिट्टी का प्रकार (लाल/काली/दोमट) और सिंचाई विधि (ड्रिप/स्प्रिंकलर/बाढ़) क्या है?"
    }
    
    fertilizer_q = {
        "english": "Have you used any fertilizers or sprays? If yes, please share names and doses.",
        "telugu": "ఏవైనా ఎరువులు లేదా మందులు వాడారా? పేర్లు మరియు మోతాదులు చెప్పండి.",
        "hindi": "क्या आपने कोई उर्वरक या दवाइयाँ इस्तेमाल की हैं? नाम और मात्रा बताएं।"
    }
    
    # Track what's been asked
    asked_crop = any("crop name" in msg.lower() or "पंट" in msg or "పంట" in msg for msg in asked_assistant_messages)
    asked_stage = any("growth stage" in msg.lower() or "પેરુગુదల" in msg or "વિકાસ" in msg for msg in asked_assistant_messages)
    asked_soil_irr = any("soil type" in msg.lower() or "irrigation" in msg.lower() or "నేల" in msg or "मिट्टी" in msg for msg in asked_assistant_messages)
    asked_fert = any("fertilizer" in msg.lower() or "ఎరువు" in msg or "उर्वरक" in msg for msg in asked_assistant_messages)
    
    print(f"🔍 Already asked: crop={asked_crop}, stage={asked_stage}, soil_irr={asked_soil_irr}, fert={asked_fert}")
    
    lang = language
    
    # ======== DIAGNOSIS QUESTIONS ========
    # For problem diagnosis: ONLY need crop name (or symptom description which user already provided)
    # DO NOT ask for soil/irrigation/fertilizers - those are for product recommendations
    if is_diagnosis:
        # Only ask for crop if not provided
        if not provided_info["crop_provided"] and not asked_crop:
            return crop_q.get(lang, crop_q["english"])
        
        # For diagnosis, we have enough with just crop+symptom (or symptom alone)
        # Don't ask for stage, soil, irrigation, fertilizers
        print("✅ DIAGNOSIS MODE: All necessary information collected (crop + symptom description)")
        sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"followup_count": MAX_FOLLOWUPS, "awaiting_followup": False}}
        )
        return None
    
    # ======== PRODUCT/GENERAL KNOWLEDGE QUESTIONS ========
    # Priority: Ask ONLY missing information, NEVER repeat
    if not provided_info["crop_provided"] and not asked_crop:
        return crop_q.get(lang, crop_q["english"])
    
    if not provided_info["stage_provided"] and not asked_stage:
        # If crop already provided, ask for stage
        if provided_info["crop_provided"]:
            return stage_q.get(lang, stage_q["english"])
    
    if (not provided_info["soil_provided"] or not provided_info["irrigation_provided"]) and not asked_soil_irr:
        return soil_irrigation_q.get(lang, soil_irrigation_q["english"])
    
    # Only ask fertilizer if crop+stage+soil are complete
    if (provided_info["crop_provided"] and provided_info["stage_provided"] and 
        provided_info["soil_provided"] and provided_info["irrigation_provided"] and 
        not provided_info["fertilizer_provided"] and not asked_fert):
        return fertilizer_q.get(lang, fertilizer_q["english"])
    
    # All information collected
    print("✅ PRODUCT MODE: All essential information collected, ready for answer")
    sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"followup_count": MAX_FOLLOWUPS, "awaiting_followup": False}}
    )
    return None


def can_finalize(session):
    """Check if we've asked enough follow-ups"""
    return session.get("followup_count", 0) >= MAX_FOLLOWUPS

