from bson import ObjectId
from datetime import datetime
from app.db.mongo import messages, sessions
from app.models.message import message_doc
from app.services.lightrag_service import query_lightrag
from app.utils.cleaner import clean_response
from app.utils.language_detector import detect_language
from app.services.chat_rules import (
    is_dosage_question,
    is_factual_company_question,
    is_direct_knowledge_question,
    is_greeting_or_acknowledgment,
    is_problem_diagnosis_question
)
from app.services.followup_service import (
    needs_follow_up,
    generate_followup,
    can_finalize
)

def generate_title(text: str) -> str:
    words = text.strip().split()
    return " ".join(words[:6]).capitalize()

def get_history(session_id):
    cursor = messages.find({"session_id": session_id}).sort("created_at", 1)
    return [{"role": m["role"], "content": m["content"]} for m in cursor]

def handle_greeting(user_message, language):
    """Handle greetings and acknowledgments in appropriate language"""
    greetings_map = {
        "english": "Hello! I'm FarmVaidya, your agricultural assistant. How can I help you today?",
        "telugu": "హలో! నేను ఫార్మ్ వైద్య, మీ వ్యవసాయ సహాయకుడిని. ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?",
        "hindi": "नमस्ते! मैं फार्मवैद्य हूं, आपका कृषि सहायक। मैं आज आपकी कैसे मदद कर सकता हूं?"
    }
    
    acknowledgments_map = {
        "english": "Great! Is there anything else I can help you with?",
        "telugu": "బాగుంది! నేను మీకు ఇంకా ఏదైనా సహాయం చేయగలనా?",
        "hindi": "बढ़िया! क्या मैं आपकी और किसी चीज़ में मदद कर सकता हूं?"
    }
    
    # Check if it's a greeting or acknowledgment
    msg_lower = user_message.lower().strip()
    
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", 
                 "namaste", "నమస్కారం", "హలో", "नमस्ते"]
    
    acknowledgments = ["ok", "okay", "noted", "thanks", "thank", "సరే", "ఓకే", "ठीक है"]
    
    is_greeting = any(g in msg_lower for g in greetings)
    is_ack = any(a in msg_lower for a in acknowledgments)
    
    if is_greeting:
        return greetings_map.get(language, greetings_map["english"])
    elif is_ack:
        return acknowledgments_map.get(language, acknowledgments_map["english"])
    
    return greetings_map.get(language, greetings_map["english"])

def handle_chat(session_id, user_message):
    print("🔥 NEW HANDLE_CHAT EXECUTED")
    
    # Detect language of user's message
    detected_language = detect_language(user_message)
    print(f"🌍 Detected language: {detected_language}")
    
    # Save user message
    messages.insert_one(message_doc(session_id, "user", user_message))

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
        return answer

    session = sessions.find_one({"_id": ObjectId(session_id)})

    # 🚫 DOSAGE → direct answer always
    if is_dosage_question(user_message):
        print("✅ DOSAGE BRANCH RETURNING LIGHTRAG ANSWER")
        history = get_history(session_id)[:-1]
        answer = clean_response(query_lightrag(user_message, history, language=detected_language))
        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 📊 FACTUAL / COMPANY QUESTIONS → NEVER FOLLOW-UP
    if is_factual_company_question(user_message):
        print("✅ FACTUAL/COMPANY QUESTION - DIRECT ANSWER")
        history = get_history(session_id)[:-1]
        answer = clean_response(query_lightrag(user_message, history, language=detected_language))
        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 📚 DIRECT PRODUCT / KNOWLEDGE → answer directly
    if is_direct_knowledge_question(user_message):
        print("✅ DIRECT KNOWLEDGE QUESTION")
        history = get_history(session_id)[:-1]
        answer = clean_response(query_lightrag(user_message, history, language=detected_language))
        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 🔁 FOLLOW-UP LOGIC FOR PROBLEM DIAGNOSIS
    # Only ask follow-ups for problem diagnosis questions that need context
    if is_problem_diagnosis_question(user_message) or session.get("awaiting_followup"):
        
        if not can_finalize(session) and needs_follow_up(session_id, detected_language):
            print("✅ GENERATING FOLLOW-UP QUESTION")
            followup_q = generate_followup(session_id, detected_language)
            messages.insert_one(message_doc(session_id, "assistant", followup_q))
            return followup_q

        # Enough followups → finalize
        print("✅ FINALIZING AFTER FOLLOW-UPS")
        sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"awaiting_followup": False}}
        )

    # ✅ FINAL ANSWER
    print("✅ GENERATING FINAL ANSWER")
    history = get_history(session_id)[:-1]
    answer = clean_response(query_lightrag(user_message, history, language=detected_language))
    messages.insert_one(message_doc(session_id, "assistant", answer))
    return answer
