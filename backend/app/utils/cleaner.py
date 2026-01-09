import re


def clean_response(text):
    # Remove reference sections, pdf filenames, citations, and markdown noise
    lines = text.splitlines()
    cleaned_lines = []

    reference_keywords = [
        "references", "reference",
        "సూచనలు", "संदर्भ", "सन्दर्भ",
        "குறிப்புகள்", "ಉಲ್ಲೇಖಗಳು", "റഫറൻസുകൾ"
    ]

    for line in lines:
        lower = line.lower()

        # Drop any line that looks like a reference header
        if any(k in lower for k in reference_keywords):
            continue

        # Drop any line containing pdf file names (any language)
        if ".pdf" in lower or "पीडीएफ" in line:
            continue

        # Remove citation numbers like [1]
        line = re.sub(r"\[\d+\]", "", line)

        # Remove markdown bold/italic markers
        line = line.replace("**", "").replace("__", "")
        line = re.sub(r"(?<!\*)\*(?!\*)", "", line)

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
