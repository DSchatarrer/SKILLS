# backend\src\core\utils.py

import re
import unicodedata

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = text.casefold()         
    text = re.sub(r"\s+", " ", text).strip()
    return text.upper()