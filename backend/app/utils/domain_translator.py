"""
Domain-specific dictionary translator for agricultural terms
Translates Telugu ↔ English for better LLM understanding
"""

# Dictionary mapping Telugu agricultural terms to English and vice versa
DOMAIN_DICTIONARY = {

    # Products
    "Invictus": ["ఇన్విక్టస్"],
    "ఇన్విక్టస్": ["Invictus"],
    "Poshak": ["పోషక్"],
    "పోషక్": ["Poshak"],
    
    "ఎఫ్‌వైఎమ్": ["పశువుల ఎరువు"],
    "మట్టి": ["నేల"],
    "శిలీంద్ర వ్యాధికారక క్రిములను":["శిలీంద్రాలను"], 
    "Black-headed Caterpillar": ["నల్ల ముట్టే పురుగు", "నల్ల గొంగళి పురుగు"],
    "నల్ల ముట్టే పురుగు": ["Black-headed Caterpillar"],
    "నల్ల గొంగళి పురుగు": ["Black-headed Caterpillar"],

    "Rhinoceros Beetle": ["కొమ్ము పురుగు", "పేడ పురుగు", "పెంకు పురుగు", "నల్ల దుక్కపురుగు", "ఖడ్గ మృగపురుగు"],
    "కొమ్ము పురుగు": ["Rhinoceros Beetle"],
    "పేడ పురుగు": ["Rhinoceros Beetle"],
    "పెంకు పురుగు": ["Rhinoceros Beetle"],
    "నల్ల దుక్కపురుగు": ["Rhinoceros Beetle"],
    "ఖడ్గ మృగపురుగు": ["Rhinoceros Beetle"],

    "Red Palm Weevil": ["ఎర్రముక్కు పురుగు"],
    "ఎర్రముక్కు పురుగు": ["Red Palm Weevil"],

    "Eriophyid Mite": ["ఎర్ర నల్లి"],
    "ఎర్ర నల్లి": ["Eriophyid Mite"],

    "Slug Caterpillar": ["ఆకు తేలు"],
    "ఆకు తేలు": ["Slug Caterpillar"],

    "Spiraling Whitefly": ["సర్పిలాకార తెల్ల దోమ", "స్పైర్లింగ్ తెల్ల దోమ"],
    "సర్పిలాకార తెల్ల దోమ": ["Spiraling Whitefly"],
    "స్పైర్లింగ్ తెల్ల దోమ": ["Spiraling Whitefly"],

    "Stem Bleeding Disease": ["నల్ల మచ్చ తెగులు"],
    "నల్ల మచ్చ తెగులు": ["Stem Bleeding Disease", "Stem bleeding"],

    "Bud Rot Disease": ["మువ్వ కుళ్ళు తెగులు", "మొవ్వకుళ్ళు"],
    "మువ్వ కుళ్ళు తెగులు": ["Bud Rot Disease"],
    "మొవ్వకుళ్ళు": ["Bud Rot Disease"],

    "Leaf Blight": ["ఆకు ఎండు తెగులు"],
    "ఆకు ఎండు తెగులు": ["Leaf Blight"],

    "Button Shedding": ["పిందె రాలడం"],
    "పిందె రాలడం": ["Button Shedding"],

    "Nuts": ["కాయలు"],
    "కాయలు": ["Nuts"],

    "Barren nuts": ["తట్టు కాయలు", "దయ్యం కాయలు", "డొల్ల కాయలు", "నీళ్లు లేని కాయలు"],
    "తట్టు కాయలు": ["Barren nuts"],
    "దయ్యం కాయలు": ["Barren nuts"],
    "డొల్ల కాయలు": ["Barren nuts"],
    "నీళ్లు లేని కాయలు": ["Barren nuts"],

    "Granules": ["గుళికలు"],
    "గుళికలు": ["Granules"],

    "Ganoderma": ["సిగ తెగులు", "ఎర్ర లెక్క తెగులు", "బంక కారు తెగులు", "పొత్తులక్క తెగులు", "తంజావూరు తెగులు", "కాండం తెగులు"],
    "సిగ తెగులు": ["Ganoderma"],
    "ఎర్ర లెక్క తెగులు": ["Ganoderma"],
    "బంక కారు తెగులు": ["Ganoderma"],
    "పొత్తులక్క తెగులు": ["Ganoderma"],
    "తంజావూరు తెగులు": ["Ganoderma"],
    "కాండం తెగులు": ["Ganoderma"],

    "Fertilisers": ["ఎరువులు", "గుండ", "పిండి"],
    "ఎరువులు": ["Fertilisers"],
    "గుండ": ["Fertilisers"],
    "పిండి": ["Fertilisers"],

    "Spindle": ["మొవ్వ", "మొవ్వు", "తల", "అంకురం"],
    "మొవ్వ": ["Spindle"],
    "మొవ్వు": ["Spindle"],
    "తల": ["Spindle"],
    "అంకురం": ["Spindle"],

    "Growth": ["ఏపూ", "బలం", "ఆరోగ్యం"],
    "ఏపూ": ["Growth"],
    "బలం": ["Growth"],
    "ఆరోగ్యం": ["Growth"],

    "Spathe, flower panicle": ["పూత", "పొత్తు", "డొక్కా"],
    "పూత": ["Spathe, flower panicle"],
    "పొత్తు": ["Spathe, flower panicle"],
    "డొక్కా": ["Spathe, flower panicle"],

    "Robust": ["మంచి"],
    "మంచి": ["Robust"],

    "Coconut palm, palm": ["కొబ్బరి చెట్టు"],
    "కొబ్బరి చెట్టు": ["Coconut palm", "palm"],

    "FYM": ["సేంద్రీయ ఎరువు", "గేత్తం", "పశువుల పెంట"],
    "సేంద్రీయ ఎరువు": ["FYM"],
    "గేత్తం": ["FYM"],
    "పశువుల పెంట": ["FYM"],

    "Green manure": ["పచ్చిరొట్ట ఎరువులు"],
    "పచ్చిరొట్ట ఎరువులు": ["Green manure"],

    "Fungus": ["శిలీంద్రం"],
    "శిలీంద్రం": ["Fungus"],

    "Sweet potato": ["చిలకడదుంప"],
    "చిలకడదుంప": ["Sweet potato"],

    "Tapioca": ["కర్ర పెండలం"],
    "కర్ర పెండలం": ["Tapioca"],

    "Elephant foot yam": ["కంద", "సార కంద"],
    "కంద": ["Elephant foot yam"],
    "సార కంద": ["Elephant foot yam"],

    "Yam": ["దుంపలు"],
    "దుంపలు": ["Yam"],

    "Coconut tree crown portion": ["కొబ్బరి చెట్టు తలభాగం"],
    "కొబ్బరి చెట్టు తలభాగం": ["Coconut tree crown portion"],

    "Adult beetles": ["పెద్ద పురుగులు"],
    "పెద్ద పురుగులు": ["Adult beetles"],
    "Adult": ["పెద్ద"],
    "పెద్ద": ["Adult"],

    "Native": ["దేశవాళీ"],
    "దేశవాళీ": ["Native"],

    "Early crops": ["త్వరగా దిగుబడినిచ్చే పంటలు"],
    "త్వరగా దిగుబడినిచ్చే పంటలు": ["Early crops"],

    "Thick base": ["మొదలు లావుగా ఉండి"],
    "మొదలు లావుగా ఉండి": ["Thick base"],

    "Plant": ["మొక్క"],
    "మొక్క": ["Plant"],

    "Tree": ["చెట్టు"],
    "చెట్టు": ["Tree"],

    "Planting material": ["నాటుకునే మొక్కలు"],
    "నాటుకునే మొక్కలు": ["Planting material"],

    "Rainfed": ["వర్షాదారిత"],
    "వర్షాదారిత": ["Rainfed"],

    "Button": ["పిందెలు"],
    "పిందెలు": ["Button"],

    "PH": ["ఉదకజని సూచిక"],
    "ఉదకజని సూచిక": ["PH"],

    "EC": ["ఎలక్ట్రాన్ల వాహకత"],
    "ఎలక్ట్రాన్ల వాహకత": ["EC"],

    "Most appropriate": ["ముఖ్యమైన"],
    "ముఖ్యమైన": ["Most appropriate"],

    "Basin": ["పళ్లెం"],
    "పళ్లెం": ["Basin", "Circular trench"],

    "Disease": ["తెగులు"],
    "తెగులు": ["Disease"],
    "Diseases": ["తెగుళ్లు"],
    "తెగుళ్లు": ["Diseases"],

    "Infestation": ["నష్టం"],
    "నష్టం": ["Infestation"],

    "Absorption": ["లభ్యత"],
    "లభ్యత": ["Absorption"],

    "Population": ["సంఖ్య"],
    "సంఖ్య": ["Population"],

    "Starch": ["గంజి"],
    "గంజి": ["Starch"],

    "Sap sucking": ["రసం పీల్చే"],
    "రసం పీల్చే": ["Sap sucking"],

    "Formulations": ["రసాయనాలు"],
    "రసాయనాలు": ["Formulations"],
}


def translate_to_english(text: str) -> str:
    """
    Translate Telugu agricultural terms to English before sending to LLM
    Step 1: Normalize Telugu terms (colloquial → standard)
    Step 2: Translate Telugu terms to English
    This helps LLM understand domain-specific terminology better
    """
    translated_text = text
    
    # Sort by length (longest first) to avoid partial matches
    terms = sorted(DOMAIN_DICTIONARY.keys(), key=len, reverse=True)
    
    # Step 1: Telugu→Telugu normalization (colloquial terms to standard terms)
    for term in terms:
        if term in translated_text:
            # Check if this is a Telugu term mapping to another Telugu term
            if any('\u0C00' <= c <= '\u0C7F' for c in term):
                translations = DOMAIN_DICTIONARY[term]
                if translations:
                    first_translation = translations[0]
                    # If target is also Telugu (normalization), apply it
                    if any('\u0C00' <= c <= '\u0C7F' for c in first_translation):
                        translated_text = translated_text.replace(term, first_translation)
                        print(f"📖 Normalized Telugu: '{term}' → '{first_translation}'")
    
    # Step 2: Telugu→English translation for LLM
    terms = sorted(DOMAIN_DICTIONARY.keys(), key=len, reverse=True)
    for term in terms:
        if term in translated_text:
            # Check if this is a Telugu term (has Telugu characters)
            if any('\u0C00' <= c <= '\u0C7F' for c in term):
                # Get English translation
                english_terms = DOMAIN_DICTIONARY[term]
                if english_terms:
                    # Find first English translation (no Telugu characters)
                    for english_term in english_terms:
                        if not any('\u0C00' <= c <= '\u0C7F' for c in english_term):
                            translated_text = translated_text.replace(term, english_term)
                            print(f"📖 Translated to English: '{term}' → '{english_term}'")
                            break
    
    return translated_text


def translate_to_telugu(text: str, original_language: str = "telugu") -> str:
    """
    Translate English agricultural terms back to Telugu in LLM response
    Only translate if original question was in Telugu
    """
    if original_language != "telugu":
        return text  # Don't translate if not Telugu conversation
    
    translated_text = text
    
    # Sort by length (longest first) to avoid partial matches
    terms = sorted(DOMAIN_DICTIONARY.keys(), key=len, reverse=True)
    
    for term in terms:
        if term in translated_text:
            # Check if this is an English term (no Telugu characters)
            if not any('\u0C00' <= c <= '\u0C7F' for c in term):
                # Get Telugu translation
                telugu_terms = DOMAIN_DICTIONARY[term]
                if telugu_terms and any('\u0C00' <= c <= '\u0C7F' for c in telugu_terms[0]):
                    telugu_term = telugu_terms[0]  # Use first translation
                    translated_text = translated_text.replace(term, telugu_term)
                    print(f"📖 Translated back: '{term}' → '{telugu_term}'")
    
    return translated_text


def get_telugu_equivalent(english_term: str) -> str:
    """Get Telugu equivalent for an English term if exists"""
    if english_term in DOMAIN_DICTIONARY:
        telugu_terms = DOMAIN_DICTIONARY[english_term]
        if telugu_terms and any('\u0C00' <= c <= '\u0C7F' for c in telugu_terms[0]):
            return telugu_terms[0]
    return english_term


def get_english_equivalent(telugu_term: str) -> str:
    """Get English equivalent for a Telugu term if exists"""
    if telugu_term in DOMAIN_DICTIONARY:
        english_terms = DOMAIN_DICTIONARY[telugu_term]
        if english_terms:
            return english_terms[0]
    return telugu_term
