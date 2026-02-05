import re
from typing import List

_RE_FILE = re.compile(r"\b(?:[\w\-]+/)*[\w\-]+\.[a-zA-Z0-9]{2,6}\b")
_RE_FUNCTION = re.compile(r"\b(def|function|func)\s+(\w+)\b", re.IGNORECASE)
_RE_FUNC_CALL = re.compile(r"\b([a-z_][a-z0-9_]*)\s*\(")
_TOOLS = {"git", "python", "pytest", "npm", "docker", "preprocessing", "chunking", "BART", "T5"}


def extract_entities(text: str, source_type: str) -> List[str]:
    entities: List[str] = []
    text_lower = text.lower()

    if source_type == "code":
        for m in _RE_FILE.finditer(text):
            entities.append(m.group(0))
        for m in _RE_FUNCTION.finditer(text):
            entities.append(m.group(2))
        for m in _RE_FUNC_CALL.finditer(text):
            name = m.group(1)
            if name not in ("def", "if", "for", "while", "with"):
                entities.append(name)
        for t in _TOOLS:
            if t.lower() in text_lower:
                entities.append(t)
    else:
        for t in _TOOLS:
            if t.lower() in text_lower:
                entities.append(t)
        for m in re.finditer(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b", text):
            entities.append(m.group(1))
        for m in re.finditer(r"\b([A-Z]{2,})\b", text):
            entities.append(m.group(1))

    seen = set()
    out: List[str] = []
    for e in entities:
        e = e.strip()
        if e and e not in seen and len(e) < 80:
            seen.add(e)
            out.append(e)
    return out[:50]
