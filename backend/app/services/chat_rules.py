# app/services/chat_rules.py

import re

def normalize(text: str) -> str:
    return text.lower().replace(" ", "").replace("-", "")


# ---------------- GREETINGS & ACKNOWLEDGMENTS ----------------
def is_greeting_or_acknowledgment(text: str) -> bool:
    """
    Detect greetings, acknowledgments, and casual conversation
    """
    t = text.lower().strip()
    
    greetings = [
        "hi", "hello", "hey", "good morning", "good afternoon", 
        "good evening", "good night", "namaste", "namaskar"
    ]
    
    acknowledgments = [
        "ok", "okay", "noted", "thanks", "thank you", "got it",
        "sure", "alright", "fine", "cool", "nice", "great",
        "wonderful", "awesome", "perfect", "understood"
    ]
    
    # Telugu greetings/acknowledgments
    telugu_patterns = [
        "నమస్కారం", "హలో", "హాయ్", "శుభోదయం", "శుభ రాత్రి",
        "సరే", "ఓకే", "థాంక్స్", "థాంక్యూ", "బాగుంది"
    ]
    
    # Hindi greetings/acknowledgments
    hindi_patterns = [
        "नमस्ते", "नमस्कार", "हेलो", "शुभ प्रभात", "शुभ रात्रि",
        "ठीक है", "धन्यवाद", "शुक्रिया", "अच्छा", "बढ़िया"
    ]
    
    all_patterns = greetings + acknowledgments + telugu_patterns + hindi_patterns
    
    # Check if the entire message is just a greeting/acknowledgment (< 5 words)
    word_count = len(t.split())
    if word_count <= 5:
        return any(pattern in t for pattern in all_patterns)
    
    return False


# ---------------- DOSAGE ----------------
def is_dosage_question(text: str) -> bool:
    keywords = [
        "dosage", "dose", "how much",
        "quantity", "per acre", "for acres",
        "application rate", "మోతాదు", "ఎంత వాడాలి",
        "कितना", "मात्रा", "खुराक"
    ]
    t = text.lower()
    return any(k in t for k in keywords)


# ---------------- FACTUAL / COMPANY ----------------
def is_factual_company_question(text: str) -> bool:
    keywords = [
        "who is", "ceo", "founder", "director",
        "how many", "number of", "count",
        "patents", "years", "established",
        "headquarters", "పేటెంట్", "ఎన్ని",
        "कितने", "पेटेंट"
    ]

    entities = [
        "biofactor",
        "farmvaidya",
        "aadhaar",
        "poshak",
        "invictus",
        "బయోఫ్యాక్టర్",
        "फार्मवैद्य"
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
    Questions about plant problems, pests, diseases that need diagnosis
    """
    problem_keywords = [
        "problem", "issue", "pest", "disease", "infection",
        "insect", "bug", "damaged", "dying", "yellow",
        "wilting", "spots", "కీటకం", "సమస్య", "వ్యాధి",
        "कीट", "समस्या", "रोग", "बीमारी"
    ]
    
    t = text.lower()
    return any(k in t for k in problem_keywords)

