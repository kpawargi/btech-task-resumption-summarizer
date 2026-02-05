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
