from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class SourceRef:
    chunk_id: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"chunk_id": self.chunk_id}
        if self.char_start is not None:
            d["char_start"] = self.char_start
        if self.char_end is not None:
            d["char_end"] = self.char_end
        return d


@dataclass
class EventRecord:
    schema_version: str
    session_id: str
    event_id: str
    event_type: str
    text: str
    source_refs: List[SourceRef]
    created_utc: str
    entities: Optional[List[str]] = None
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "text": self.text,
            "source_refs": [r.to_dict() for r in self.source_refs],
            "created_utc": self.created_utc,
        }
        if self.entities is not None:
            d["entities"] = self.entities
        if self.score is not None:
            d["score"] = self.score
        return d
