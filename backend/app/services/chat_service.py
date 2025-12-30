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
