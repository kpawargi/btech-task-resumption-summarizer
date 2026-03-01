import re
from src.utils import normalize_whitespace


def clean_text(text: str) -> str:
    # Normalize whitespace
    text = normalize_whitespace(text)

    # Remove obvious boilerplate artifacts (optional conservative)
    # Example: repeated page headers like "Page 1" (keep conservative)
    text = re.sub(r"\nPage\s+\d+\s*\n", "\n", text, flags=re.IGNORECASE)

    return text.strip()
