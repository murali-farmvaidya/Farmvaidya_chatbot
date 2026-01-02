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


def generate_followup(session_id: str, language: str = "english") -> str:
    """
    Generate a contextual follow-up question in the appropriate language
    
    Args:
        session_id: The session ID
        language: The detected language of the user's question
    """
    # Deterministic follow-up sequence to avoid noisy/irrelevant questions
    followup_sequences = {
        "telugu": [
            "మీ కొబ్బరి చెట్ల పెరుగుదల దశ (ఆరంభం/మధ్య/కోలేక) ఏమిటి?",
            "మీ నేల రకం (ఎర్ర, నల్ల, లోమీ) మరియు నీటిపారుదల విధానం (డ్రిప్/స్ప్రింక్లర్/ఎద్దులు) ఏమిటి?",
            "ఇప్పటివరకు ఏ ఎరువులు లేదా మందులు వాడారా? ఉంటే పేర్లు/మోతాదులు చెప్పండి."
        ],
        "hindi": [
            "आपकी नारियल की पेड़ों का विकास चरण (शुरुआत/मध्य/कटाई के पास) क्या है?",
            "आपकी मिट्टी का प्रकार (काली/लाल/दोमट) और सिंचाई विधि (ड्रिप/स्प्रिंकलर/बाढ़) क्या है?",
            "अब तक कौन-कौन से उर्वरक या दवाइयाँ इस्तेमाल की हैं? नाम/मात्रा बताएं।"
        ],
        "english": [
            "What is the growth stage of your coconut trees (early/mid/near harvest)?",
            "What is your soil type (red/black/loam) and irrigation method (drip/sprinkler/flood)?",
            "What fertilizers or sprays have you already used? Please mention names and doses."
        ]
    }

    sequence = followup_sequences.get(language, followup_sequences["english"])

    # Get current follow-up count
    session_doc = sessions.find_one({"_id": ObjectId(session_id)}) or {}
    current_count = session_doc.get("followup_count", 0)

    # Pick the next question, capped at last question in sequence
    index = min(current_count, len(sequence) - 1)
    question = sequence[index]

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

