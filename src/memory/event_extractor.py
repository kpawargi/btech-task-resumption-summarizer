import re
from typing import List, Tuple

EVENT_TYPES = ("ACTION", "DECISION", "TODO", "ISSUE", "NOTE")

_RE_TODO = re.compile(
    r"\b(TODO|FIXME|XXX|To-do|to do)\s*[:\-]?\s*(.+?)(?=[.\n]|$)",
    re.IGNORECASE | re.DOTALL,
)
_RE_NOTE = re.compile(
    r"\b(NOTE|Note)\s*[:\-]?\s*(.+?)(?=[.\n]|$)",
    re.IGNORECASE | re.DOTALL,
)
_RE_DECISION = re.compile(
    r"\b(?:decided to|decision was|we agreed|agreed to|the main decision was|agreed that)\s*(.+?)(?=[.\n]|$)",
    re.IGNORECASE | re.DOTALL,
)
_RE_ACTION_PLAN = re.compile(
    r"\b(?:planned to|plan to|want to|going to|I will|we will|next steps? are)\s*(.+?)(?=[.\n]|$)",
    re.IGNORECASE | re.DOTALL,
)
_RE_ISSUE = re.compile(
    r"\b(?:issue|problem|blocked|stuck|blocker)\s*[:\-]?\s*(.+?)(?=[.\n]|$)",
    re.IGNORECASE | re.DOTALL,
)
_RE_ACTION = re.compile(
    r"\b(?:resumed|discussed|implemented|added|noted|compared|understood)\s+(.+?)(?=[.\n]|$)",
    re.IGNORECASE | re.DOTALL,
)


def _clean_snippet(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s[:500] if len(s) > 500 else s


def _extract_with(regex: re.Pattern, text: str, event_type: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for m in regex.finditer(text):
        snippet = m.group(1).strip() if m.lastindex and m.lastindex >= 1 else m.group(0)
        snippet = _clean_snippet(snippet)
        if len(snippet) >= 3:
            out.append((event_type, snippet))
    return out


def extract_events_from_text(text: str) -> List[Tuple[str, str]]:
    results: List[Tuple[str, str]] = []
    seen: set = set()

    def add(dedup_key: str, event_type: str, snippet: str):
        if dedup_key in seen or not snippet:
            return
        seen.add(dedup_key)
        results.append((event_type, snippet))

    for m in _RE_TODO.finditer(text):
        snippet = _clean_snippet(m.group(2) if m.lastindex >= 2 else m.group(0))
        add(f"TODO:{snippet[:80]}", "TODO", snippet)
    for m in _RE_NOTE.finditer(text):
        snippet = _clean_snippet(m.group(2) if m.lastindex >= 2 else m.group(0))
        add(f"NOTE:{snippet[:80]}", "NOTE", snippet)
    for t, s in _extract_with(_RE_DECISION, text, "DECISION"):
        add(f"DEC:{s[:80]}", t, s)
    for t, s in _extract_with(_RE_ISSUE, text, "ISSUE"):
        add(f"ISS:{s[:80]}", t, s)
    for t, s in _extract_with(_RE_ACTION_PLAN, text, "ACTION"):
        add(f"PLAN:{s[:80]}", t, s)
    for t, s in _extract_with(_RE_ACTION, text, "ACTION"):
        add(f"ACT:{s[:80]}", t, s)

    return results
