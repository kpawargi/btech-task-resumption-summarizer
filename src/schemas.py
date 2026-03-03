from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List


@dataclass
class SessionRecord:
    schema_version: str
    session_id: str
    task_id: str
    source_type: str
    source_path: str
    created_utc: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChunkRecord:
    schema_version: str
    session_id: str
    chunk_id: str
    source_type: str
    text: str
    token_count: int
    char_start: int
    char_end: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChunkSet:
    schema_version: str
    session_id: str
    task_id: str
    source_type: str
    source_path: str
    chunks: List[ChunkRecord]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "source_type": self.source_type,
            "source_path": self.source_path,
            "chunks": [c.to_dict() for c in self.chunks],
        }


@dataclass
class SourceRef:
    """Evidence reference back to a chunk"""
    chunk_id: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EventRecord:
    """Extracted event (TODO, DECISION, ACTION, ISSUE, NOTE)"""
    schema_version: str
    session_id: str
    event_id: str
    event_type: str  # "TODO" | "DECISION" | "ACTION" | "ISSUE" | "NOTE"
    text: str
    source_refs: List[SourceRef]
    created_utc: str
    entities: Optional[List[str]] = None
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "text": self.text,
            "source_refs": [ref.to_dict() for ref in self.source_refs],
            "created_utc": self.created_utc,
            "entities": self.entities,
            "score": self.score,
        }


@dataclass
class EventSet:
    """Collection of extracted events from a session"""
    schema_version: str
    session_id: str
    task_id: str
    events: List[EventRecord]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "events": [e.to_dict() for e in self.events],
        }
