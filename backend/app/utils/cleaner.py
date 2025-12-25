import re

def clean_response(text):
    text = re.split(r"\n\s*(###\s*)?references\s*\n", text, flags=re.I)[0]
    return re.sub(r"\[\d+\]", "", text).strip()
