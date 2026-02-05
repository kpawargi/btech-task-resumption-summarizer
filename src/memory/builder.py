import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from src.event_schemas import EventRecord, SourceRef
from src.memory.event_extractor import extract_events_from_text
from src.memory.entity_extractor import extract_entities
from src.memory.evidence_linker import link_evidence
from src.memory.importance_scorer import score_events

SCHEMA_VERSION = "v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _new_event_id() -> str:
    return "evt_" + uuid.uuid4().hex[:12]


def _load_session_and_chunkset(session_dir: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
    session_path = session_dir / "session.json"
    chunkset_path = session_dir / "chunkset_index.json"
    if not session_path.exists():
        raise FileNotFoundError(f"Session file not found: {session_path}")
    if not chunkset_path.exists():
        raise FileNotFoundError(f"Chunkset file not found: {chunkset_path}")
    with session_path.open(encoding="utf-8") as f:
        session = json.load(f)
    with chunkset_path.open(encoding="utf-8") as f:
        chunkset = json.load(f)
    return session, chunkset


def run_memory_build(session_dir: Path) -> Tuple[List[EventRecord], Optional[str]]:
    session, chunkset = _load_session_and_chunkset(session_dir)
    session_id = session["session_id"]
    task_id = session.get("task_id") or chunkset.get("task_id")
    source_type = chunkset.get("source_type", "reading")
    created_utc = _utc_now_iso()

    events: List[EventRecord] = []
    for chunk in chunkset.get("chunks", []):
        chunk_id = chunk["chunk_id"]
        text = chunk.get("text", "")
        char_start = chunk.get("char_start", 0)
        char_end = chunk.get("char_end")

        raw_events = extract_events_from_text(text)
        chunk_entities = extract_entities(text, source_type)

        for event_type, event_text in raw_events:
            source_refs = link_evidence(
                chunk_id=chunk_id,
                chunk_text=text,
                event_text=event_text,
                chunk_char_start=char_start,
                chunk_char_end=char_end,
            )
            entities = extract_entities(event_text, source_type) or chunk_entities[:10]

            ev = EventRecord(
                schema_version=SCHEMA_VERSION,
                session_id=session_id,
                event_id=_new_event_id(),
                event_type=event_type,
                text=event_text,
                source_refs=source_refs,
                created_utc=created_utc,
                entities=entities if entities else None,
            )
            events.append(ev)

    score_events(events)
    return events, task_id
