from bson import ObjectId
from datetime import datetime
from app.db.mongo import messages, sessions
from app.models.message import message_doc
from app.services.lightrag_service import query_lightrag
from app.services.local_knowledge_base import synthesize_answer
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
    can_finalize,
    MAX_FOLLOWUPS
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

    # Fetch session data early for all subsequent logic
    session = sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        # Session not found - create a new one or handle gracefully
        print(f"⚠️ Session {session_id} not found in database")
        session = {}

    # 🚫 DOSAGE → direct answer always (no history to avoid language contamination)
    if is_dosage_question(user_message):
        print("✅ DOSAGE BRANCH RETURNING LIGHTRAG ANSWER")
        # Don't pass history - prevents language contamination from previous messages
        answer = clean_response(query_lightrag(user_message, [], language=detected_language))
        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 📊 FACTUAL / COMPANY QUESTIONS → NEVER FOLLOW-UP, NO HISTORY
    # Don't pass history for factual questions to avoid entity confusion
    # Use factual=True to avoid forcing answers when no information exists
    if is_factual_company_question(user_message):
        print("✅ FACTUAL/COMPANY QUESTION - DIRECT ANSWER (NO HISTORY)")
        answer = clean_response(query_lightrag(user_message, [], language=detected_language, factual=True))
        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 📚 DIRECT PRODUCT / KNOWLEDGE → answer directly (no history to avoid language contamination)
    if is_direct_knowledge_question(user_message):
        print("✅ DIRECT KNOWLEDGE QUESTION")
        # Don't pass history - prevents language contamination from previous messages
        answer = clean_response(query_lightrag(user_message, [], language=detected_language))
        messages.insert_one(message_doc(session_id, "assistant", answer))
        return answer

    # 🔁 FOLLOW-UP LOGIC FOR PROBLEM DIAGNOSIS
    # Always ask follow-ups for diagnosis until we have enough context (language-agnostic)
    if is_problem_diagnosis_question(user_message) or session.get("awaiting_followup"):
        # If this is a NEW problem diagnosis question and we're not already in follow-up mode,
        # reset the follow-up state (user asking a new question after previous conversation)
        if is_problem_diagnosis_question(user_message) and not session.get("awaiting_followup"):
            # Check if user already provided comprehensive information in their question
            # OR if we can use info from recent conversation history
            from app.services.followup_service import extract_provided_info
            
            # Check both current message AND recent history (last 10 messages to capture recent context)
            recent_history = get_history(session_id)[-10:]  # Last 10 messages
            provided = extract_provided_info(recent_history)
            
            # If user provided crop+stage AND soil info, skip follow-ups
            has_crop_info = provided["crop_provided"] and provided["stage_provided"]
            has_soil_info = provided["soil_provided"]
            
            # For better UX: if crop is mentioned but from OLD conversation (more than 5 messages ago),
            # we should still ask follow-ups for the NEW question
            # Check if crop/stage is in the CURRENT message specifically
            current_msg_history = [{"role": "user", "content": user_message}]
            current_provided = extract_provided_info(current_msg_history)
            
            if has_crop_info and has_soil_info:
                # User gave enough info, skip follow-ups entirely
                print("✅ USER PROVIDED COMPREHENSIVE INFO, SKIPPING FOLLOW-UPS")
                sessions.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$set": {"followup_count": MAX_FOLLOWUPS, "awaiting_followup": False}}
                )
                session["followup_count"] = MAX_FOLLOWUPS
                session["awaiting_followup"] = False
            elif current_provided["crop_provided"] and current_provided["stage_provided"]:
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
                # Reset for new question
                sessions.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$set": {"followup_count": 0, "awaiting_followup": False}}
                )
                session["followup_count"] = 0
                session["awaiting_followup"] = False
        
        # Default followup counter to 0 if missing
        if session.get("followup_count") is None:
            session["followup_count"] = 0

        if not can_finalize(session):
            print("✅ GENERATING FOLLOW-UP QUESTION")
            followup_q = generate_followup(session_id, detected_language, user_message)
            
            # If generate_followup returns None, it means all info is collected
            if followup_q is None:
                print("✅ ALL INFO COLLECTED, PROCEEDING TO FINAL ANSWER")
                sessions.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$set": {"awaiting_followup": False}}
                )
                # Don't return, continue to final answer generation
            else:
                messages.insert_one(message_doc(session_id, "assistant", followup_q))
                return followup_q

        # Enough followups → finalize and continue to final answer
        print("✅ FINALIZING AFTER FOLLOW-UPS")
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
        comprehensive_query = f"""CROP PROBLEM DIAGNOSIS

Farmer's problem: {original_question}

Farmer provided the following information:
- Crop name and growth stage: {ans1}
- Soil type and irrigation method: {ans2}
- Fertilizers and sprays already used: {ans3}

Provide comprehensive recommendations including:
1. Specific fertilizer doses based on soil type and growth stage
2. Irrigation schedule and water management
3. Pest/disease management if applicable
4. Nutrient deficiency corrections if needed
5. Any other management practices

Be specific with product names, doses (kg/liters), timing (months), and application methods."""
        
        print(f"📝 Original Question: {original_question}")
        print(f"📝 Q1 Answer: {ans1}")
        print(f"📝 Q2 Answer: {ans2}")
        print(f"📝 Q3 Answer: {ans3}")
        print(f"📝 Final Query to LightRAG: {comprehensive_query}")
        
        # Try LightRAG first
        answer = clean_response(query_lightrag(comprehensive_query, [], language=detected_language))
        
        # If LightRAG returns [no-context] or empty, use local knowledge base
        if "[no-context]" in answer or not answer or answer.strip() == "":
            print("⚠️ LightRAG returned no context, using local knowledge base...")
            
            # Parse the collected information
            soil_type = ans2.lower().split()[0] if ans2 and "not provided" not in ans2.lower() else "loam"
            growth_stage = ans1.lower().split()[0] if ans1 and "not provided" not in ans1.lower() else "mid"
            irrigation = "drip" if "drip" in ans2.lower() else ("sprinkler" if "sprinkler" in ans2.lower() else "flood")
            
            try:
                # Use local knowledge base
                answer = synthesize_answer(soil_type, growth_stage, irrigation, ans3)
                print("✅ Generated answer using local knowledge base")
            except Exception as e:
                print(f"❌ Error in local knowledge base: {e}")
                answer = f"Based on your {growth_stage}-stage crop in {soil_type} soil with {irrigation} irrigation: Please consult our detailed guides or contact local agricultural experts for comprehensive fertilizer and irrigation recommendations."
    else:
        # Not a diagnosis question or no follow-ups collected, just use direct query with history
        answer = clean_response(query_lightrag(user_message, history, language=detected_language))
    
    messages.insert_one(message_doc(session_id, "assistant", answer))
    return answer
