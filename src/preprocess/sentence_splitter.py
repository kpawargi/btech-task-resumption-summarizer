import re
from typing import List, Tuple


_SENT_BOUNDARY = re.compile(
    r"(?<=[.!?])\s+(?=[A-Z0-9\"\'])"
)

def split_sentences_with_spans(text: str) -> List[Tuple[str, int, int]]:
    """
    Returns list of (sentence, char_start, char_end) spans in the original text.
    Simple rule-based splitter (good enough for slice-1).
    """
    if not text:
        return []

    spans: List[Tuple[str, int, int]] = []
    start = 0

    # Split boundaries on punctuation followed by space + capital/number/quote
    parts = _SENT_BOUNDARY.split(text)

    idx = 0
    cursor = 0
    for p in parts:
        p = p.strip()
        if not p:
            continue

        # Find this part in original text starting from cursor
        found_at = text.find(p, cursor)
        if found_at == -1:
            # fallback: approximate
            found_at = cursor
        char_start = found_at
        char_end = found_at + len(p)
        spans.append((p, char_start, char_end))
        cursor = char_end
        idx += 1

    return spans
