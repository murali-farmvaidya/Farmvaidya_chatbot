from app.services.lightrag_service import query_lightrag
from app.db.mongo import sessions, messages
from bson import ObjectId

MAX_FOLLOWUPS = 2

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
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages.find({"session_id": session_id}).sort("created_at", 1)
    ]

    # Language-specific instructions for generating follow-ups
    followup_instructions = {
        "telugu": "రైతుకు తప్పిపోయిన నిర్దిష్ట వివరాలను పొందడానికి ఒక స్పష్టమైన, సరళమైన ఫాలో-అప్ ప్రశ్న అడగండి. తెలుగులో మాత్రమే సమాధానం ఇవ్వండి.",
        "hindi": "किसान से छूटी हुई विशिष्ट जानकारी प्राप्त करने के लिए एक स्पष्ट, सरल अनुवर्ती प्रश्न पूछें। केवल हिंदी में उत्तर दें।",
        "english": "Ask ONE clear, simple follow-up question to get the missing farmer-specific details. Be specific and contextual."
    }

    query_text = followup_instructions.get(language, followup_instructions["english"])

    question = query_lightrag(query_text, history, mode="bypass", language=language)

    sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$inc": {"followup_count": 1},
            "$set": {"awaiting_followup": True}
        }
    )

    return question.strip()


def can_finalize(session):
    """Check if we've asked enough follow-ups"""
    return session.get("followup_count", 0) >= MAX_FOLLOWUPS

