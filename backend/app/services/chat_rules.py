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
        "invictus", "ఇన్విక్టస్",
        "bio npk", "bionpk",
        "bio double action"
    ]
    
    t = text.lower()
    
    # Check for dosage keywords
    if any(k in t for k in keywords):
        return True
    
    # Check if asking about product (likely wants dosage info)
    # If product name is mentioned alone or with minimal context, treat as dosage question
    for product in product_names:
        if product in t:
            # If it's just the product name or with very few words (like "k factor", "dosage of pfactor")
            word_count = len(t.split())
            if word_count <= 4:
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
        "గురించి", "చెప్పండి", "ఏమిటి",
        "के बारे में", "बताइए", "क्या है"
    ]

    products = [
        "aadhaar gold", "aadhaar", "aadhar",
        "poshak", "పోషక్",
        "invictus", "ఇన్విక్టస్",
        "zn-factor", "znfactor",
        "p-factor", "pfactor", "p factor",
        "k-factor", "kfactor", "k factor",
        "biofactor", "బయోఫ్యాక్టర్",
        "farmvaidya", "ఫార్మ్ వైద్య",
        "bio double action", "biodoubleaction",
        "बायो डबल एक्शन"
    ]

    t = text.lower()
    return any(k in t for k in keywords) and any(p in t for p in products)


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

