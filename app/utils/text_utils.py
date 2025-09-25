def clean_text(text: str) -> str:
    return text.replace("\u200c", " ").strip()
