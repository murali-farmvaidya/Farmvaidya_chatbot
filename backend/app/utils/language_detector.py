# app/utils/language_detector.py

import re

def detect_language(text: str) -> str:
    """
    Detect if the text is in Telugu, Hindi, or English.
    Returns: 'telugu', 'hindi', or 'english'
    """
    text = text.strip()
    
    # Telugu Unicode range: \u0C00-\u0C7F
    telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))
    
    # Hindi/Devanagari Unicode range: \u0900-\u097F
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    
    # Count total characters (excluding spaces and punctuation)
    total_chars = len(re.findall(r'[^\s\W\d]', text))
    
    if total_chars == 0:
        return 'english'
    
    # If more than 30% characters are Telugu
    if telugu_chars / total_chars > 0.3:
        return 'telugu'
    
    # If more than 30% characters are Hindi
    if hindi_chars / total_chars > 0.3:
        return 'hindi'
    
    return 'english'


def get_language_instruction(language: str) -> str:
    """
    Get instruction to append to prompt for language-specific responses
    """
    if language == 'telugu':
        return "\n\nIMPORTANT: Respond ONLY in Telugu (తెలుగు) language. Do not use English."
    elif language == 'hindi':
        return "\n\nIMPORTANT: Respond ONLY in Hindi (हिंदी) language. Do not use English."
    else:
        return "\n\nIMPORTANT: Respond ONLY in English language."
