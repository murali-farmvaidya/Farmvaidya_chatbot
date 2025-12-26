def is_direct_knowledge_question(text: str) -> bool:
    keywords = [
        "what is", "explain", "tell me",
        "usage", "how is it used",
        "dosage", "benefits", "features"
    ]
    products = [
        "aadhaar gold", "poshak", "invictus",
        "zn-factor", "biofactor", "farmvaidya"
    ]
    t = text.lower()
    return any(k in t for k in keywords) and any(p in t for p in products)


def is_program_or_fee_question(text: str) -> bool:
    keywords = [
        "fee", "fees", "cost", "price",
        "timing", "duration", "schedule",
        "program", "course", "training",
        "workshop", "certification",
        "ai in agriculture"
    ]
    return any(k in text.lower() for k in keywords)


def is_logistics_question(text: str) -> bool:
    keywords = [
        "register", "join", "link",
        "contact", "phone", "number",
        "zoom", "session link"
    ]
    return any(k in text.lower() for k in keywords)


def is_dosage_question(text: str) -> bool:
    keywords = [
        "dosage",
        "dose",
        "how much",
        "quantity",
        "per acre",
        "for acres",
        "application rate"
    ]
    return any(k in text.lower() for k in keywords)
