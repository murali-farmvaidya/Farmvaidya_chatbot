# app/services/chat_rules.py

import re

def normalize(text: str) -> str:
    return text.lower().replace(" ", "").replace("-", "")


# ---------------- GREETINGS & ACKNOWLEDGMENTS ----------------
def is_greeting_or_acknowledgment(text: str) -> bool:
    """
    Detect greetings, acknowledgments, and casual conversation
    Returns True if the message is purely a greeting/acknowledgment
    """
    if not text or len(text.strip()) == 0:
        return False
    
    t = text.lower().strip()
    original = text.strip()
    
    # Exclude product-related queries that might contain 'k'
    product_keywords = ["factor", "aadhaar", "poshak", "invictus", "dosage", "dose", "product", "application"]
    if any(keyword in t for keyword in product_keywords):
        return False
    
    # English greetings (including common variations)
    greetings = [
        "hi", "hii", "hiiii", "hello", "helo", "hellooo", "hey", "heyy",
        "good morning", "morning", "good afternoon", "afternoon",
        "good evening", "evening", "good night", "night",
        "namaste", "namaskar", "namaskaram"
    ]
    
    # Acknowledgments
    acknowledgments = [
        "ok", "okay", "okk", "noted", "thanks", "thank you", "thankyou",
        "got it", "sure", "alright", "fine", "cool", "nice", "great",
        "wonderful", "awesome", "perfect", "understood", "k", "kk"
    ]
    
    # Telugu greetings/acknowledgments
    telugu_patterns = [
        "నమస్కారం", "హలో", "హాయ్", "శుభోదయం", "శుభ మధ్యాహ్నం",
        "శుభ సాయంత్రం", "శుభ రాత్రి", "సరే", "ఓకే", 
        "థాంక్స్", "థాంక్యూ", "ధన్యవాదాలు", "బాగుంది"
    ]
    
    # Hindi greetings/acknowledgments
    hindi_patterns = [
        "नमस्ते", "नमस्कार", "हेलो", "हाय", "शुभ प्रभात", "सुप्रभात",
        "शुभ दोपहर", "शुभ संध्या", "शुभ रात्रि", 
        "ठीक है", "धन्यवाद", "शुक्रिया", "अच्छा", "बढ़िया"
    ]
    
    all_patterns = greetings + acknowledgments + telugu_patterns + hindi_patterns
    
    # Check if the entire message is just a greeting/acknowledgment
    # Allow up to 6 words (e.g., "Good morning, how are you?")
    word_count = len(t.split())
    
    if word_count <= 6:
        # For each greeting pattern, check if message is EXACTLY that pattern (word-for-word)
        # This prevents "which" from matching "hi"
        for pattern in all_patterns:
            if pattern == t:
                return True
            # For multi-word patterns like "good morning", check exact phrase
            if len(pattern.split()) > 1 and pattern in t:
                return True
        
        # Check for Unicode patterns in original text (Telugu/Hindi)
        for pattern in telugu_patterns + hindi_patterns:
            if pattern in original:
                return True
    
    return False


# ---------------- HELPER: FOLLOW-UP DETECTION ----------------
def is_followup_reference(text: str) -> bool:
    """
    Detect if question is a follow-up using pronouns/references
    Examples: "its dosage", "what about it", "how much of that", "ఆది", "దాని"
    Must be SHORT and contain explicit pronouns to avoid false positives
    """
    t = text.lower().strip()
    
    # Require question to be relatively short (< 8 words) to be a follow-up
    # This prevents "Benefits of Bio NPK" from being treated as follow-up
    word_count = len(t.split())
    if word_count > 7:
        return False
    
    followup_keywords = [
        # English pronouns (more specific)
        " its ", "its ", " its",  # "its dosage", "what is its"
        " it ", " it's ",
        "that product", "that one", "the same",
        "about it", "of that", "of it",
        # English yes/no/confirmation responses
        " yes", "yes ", " yes ", " no", "no ", " no ",
        "yeah", "nope", " okay", "ok ", " ok ", " sure", "sure ",
        # Telugu pronouns
        "ఆది", "దాని", "అది", "ఇది", "అదే", "ఇదే",
        "అవును", "లేదు", "సరే",  # yes/no/ok in Telugu
        # Hindi pronouns  
        "उसका", "इसका", "वह", "यह", "उसी", "इसी",
        "हाँ", "नहीं", "ठीक है"  # yes/no/ok in Hindi
    ]
    
    # Add spaces for better matching
    text_with_spaces = f" {t} "
    return any(kw in text_with_spaces for kw in followup_keywords)


# ---------------- DOSAGE ----------------
def is_dosage_question(text: str) -> bool:
    keywords = [
        "dosage", "dose", "how much", "doage", "dosge",
        "quantity", "per acre", "for acres",
        "application rate", "మోతాదు", "ఎంత వాడాలి",
        "कितना", "मात्रा", "खुराक"
    ]
    
    # Product names that indicate dosage questions
    product_names = [
        "p-factor", "pfactor", "p factor",
        "k-factor", "kfactor", "k factor",
        "zn-factor", "znfactor", "zn factor",
        "aadhaar", "aadhar",
        "poshak", "పోషక్",
        "invictus",
        "bio npk", "bionpk",
        "bio double action"
    ]
    
    t = text.lower()
    original = text  # Keep original text for Unicode matching
    
    # Exclude knowledge questions UNLESS it's a follow-up reference (like "what is its dosage")
    knowledge_excludes = ["what is", "tell me", "explain", "about", "గురించి", "ఏమిటి", "चेप్पंది", "क्या है", "के बारे में"]
    has_knowledge_exclude = any(exc in t for exc in knowledge_excludes) or any(exc in original for exc in knowledge_excludes)
    if has_knowledge_exclude and not is_followup_reference(text):
        return False
    
    # Telugu product names that need Unicode matching
    telugu_products = ["ఇన్విక్టస్", "పోషక్"]
    
    # Check for dosage keywords in both lowercased and original text
    if any(k in t for k in keywords) or any(k in original for k in keywords):
        return True
    
    # Check if asking about product (likely wants dosage info)
    # If product name is mentioned alone or with minimal context, treat as dosage question
    for product in product_names:
        if product in t:
            # If it's just the product name or with very few words (like "k factor", "dosage of pfactor")
            word_count = len(t.split())
            if word_count <= 4:
                return True
    
    # Check Telugu product names in original text
    for product in telugu_products:
        if product in original:
            return True
    
    return False


# ---------------- FACTUAL / COMPANY ----------------
def is_factual_company_question(text: str) -> bool:
    keywords = [
        "who is", "ceo", "founder", "director", "chief",
        "how many", "number of", "count",
        "patents", "years", "established", "started",
        "headquarters", "location", "office",
        "సీఈఓ", "ఎవరు", "పేటెంట్", "ఎన్ని",
        "सीईओ", "कौन", "कितने", "पेटेंट"
    ]

    entities = [
        "biofactor", "bio factor",
        "farmvaidya", "farm vaidya",
        "aadhaar",
        "poshak",
        "invictus",
        "బయోఫ్యాక్టర్", "బయో ఫ్యాక్టర్",
        "ఫార్మ్ వైద్య", "ఫార్మ్వైద్య",
        "बायोफैक्टर", "बायो फैक्टर",
        "फार्मवैद्य", "फार्म वैद्य"
    ]

    t = normalize(text)

    return (
        any(k.replace(" ", "") in t for k in keywords)
        and any(e in t for e in entities)
    )


# ---------------- DIRECT PRODUCT / KNOWLEDGE ----------------
def is_direct_knowledge_question(text: str) -> bool:
    keywords = [
        "what is", "tell me", "explain",
        "usage", "how is it used", "how to use",
        "benefits", "features", "about",
        "fertilizer", "fertilizers",
        "గురించి", "చెప్పండి", "ఏమిటి", "వాడే", "వాడకం", "ఎరువుల", "ఎరువులు",
        "के बारे में", "बताइए", "क्या है", "खाद", "उर्वरक"
    ]

    products = [
        "aadhaar gold", "aadhaar", "aadhar",
        "poshak", "పోషక్",
        "invictus", "ఇన్విక్టస్",
        "zn-factor", "znfactor",
        "p-factor", "pfactor", "p factor",
        "k-factor", "kfactor", "k factor",
        "biofactor", "bio factor", "బయోఫ్యాక్టర్", "బయో ఫ్యాక్టర్",
        "farmvaidya", "ఫార్మ్ వైద్య",
        "bio double action", "biodoubleaction",
        "बायो डबल एक्शन", "बायोफैक्टर", "बायो फैक्टर"
    ]

    t = text.lower()
    original = text  # Keep original for Unicode matching
    
    # Check in both normalized and original text
    keyword_match = any(k in t for k in keywords) or any(k in original for k in keywords)
    product_match = any(p in t for p in products) or any(p in original for p in products)
    
    return keyword_match and product_match


# ---------------- PROBLEM DIAGNOSIS ----------------
def is_problem_diagnosis_question(text: str) -> bool:
    """
    Questions about plant problems, pests, diseases, yield issues that need diagnosis
    """
    problem_keywords = [
        "problem", "issue", "pest", "disease", "infection",
        "insect", "bug", "damaged", "dying", "yellow",
        "wilting", "spots", "not growing", "poor growth", "low yield",
        "not giving", "yield", "production", "harvest",
        "కీటకం", "సమస్య", "వ్యాధి", "దిగుబడి", "పంట రావడం లేదు",
        "कीट", "समस्या", "रोग", "बीमारी", "उपज", "पैदावार"
    ]
    
    t = text.lower()
    return any(k in t for k in problem_keywords)


# ---------------- SUMMARY & LIST QUESTIONS ----------------
def is_summary_or_list_question(text: str) -> bool:
    """
    Detect questions asking for summaries, lists, or recaps of previously discussed information.
    These should compile from conversation history rather than sending to LightRAG.
    """
    if not text or len(text.strip()) == 0:
        return False
    
    t = text.lower()
    original = text
    
    # English summary keywords
    summary_keywords = [
        "tell me all", "list all", "recap", "summary", "summarize",
        "all dosages", "all products", "all information",
        "until now", "so far", "discussed", "mention", "mentioned",
        "what we discussed", "everything about", "all about",
        "complete list", "full list", "entire list"
    ]
    
    # Telugu summary keywords
    telugu_keywords = [
        "అన్ని", "చెప్పు", "జాబితా", "ఇప్పటిదాకా", "చర్చించిన",
        "సారాంశం", "సమాచారం", "మోతాదులు", "ఉత్పత్తులు"
    ]
    
    # Hindi summary keywords
    hindi_keywords = [
        "सभी", "सूची", "सारांश", "अब तक", "जानकारी", "खुराक",
        "उत्पाद", "बताइए", "सबको", "चर्चा"
    ]
    
    all_keywords = summary_keywords + telugu_keywords + hindi_keywords
    
    # Check if any keyword matches
    match_count = sum(1 for k in all_keywords if k in t or k in original)
    
    return match_count >= 1

