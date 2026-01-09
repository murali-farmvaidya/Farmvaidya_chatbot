import re

def clean_response(text):
    """
    Clean LightRAG response by removing:
    - References section (in any language)
    - Citation numbers [1], [2], etc.
    - Markdown formatting symbols
    """
    
    # Remove references section (English, Telugu, Hindi, etc.)
    # Patterns: ### References, ### సూచనలు, ### संदर्भ, etc.
    reference_patterns = [
        r"\n\s*(###\s*)?references\s*\n",  # English
        r"\n\s*(###\s*)?సూచనలు\s*\n",     # Telugu
        r"\n\s*(###\s*)?संदर्भ\s*\n",      # Hindi
        r"\n\s*(###\s*)?குறிப்புகள்\s*\n", # Tamil
        r"\n\s*(###\s*)?ಉಲ್ಲೇಖಗಳು\s*\n",  # Kannada
        r"\n\s*(###\s*)?റഫറൻസുകൾ\s*\n",   # Malayalam
    ]
    
    for pattern in reference_patterns:
        parts = re.split(pattern, text, flags=re.I)
        if len(parts) > 1:
            text = parts[0]
            break
    
    # Remove citation numbers like [1], [2], etc.
    text = re.sub(r"\[\d+\]", "", text)
    
    # Remove markdown bold/italic markers
    text = re.sub(r"\*\*", "", text)  # Remove ** (bold)
    text = re.sub(r"__", "", text)    # Remove __ (bold)
    text = re.sub(r"(?<!\*)\*(?!\*)", "", text)  # Remove single * (italic) but not **
    
    # Remove bullet point asterisks at line start and replace with proper bullets
    text = re.sub(r"^\*\s+", "• ", text, flags=re.MULTILINE)
    
    # Remove any remaining standalone ### at the start of lines
    text = re.sub(r"^###\s*", "", text, flags=re.MULTILINE)
    
    return text.strip()
