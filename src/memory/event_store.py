import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from src.event_schemas import EventRecord, SourceRef


def _source_refs_to_json(refs: List[SourceRef]) -> str:
    return json.dumps([r.to_dict() for r in refs])


def _source_refs_from_json(s: str) -> List[SourceRef]:
    data = json.loads(s)
    return [SourceRef(chunk_id=x["chunk_id"], char_start=x.get("char_start"), char_end=x.get("char_end")) for x in data]


class EventStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _conn(self):
        return sqlite3.connect(str(self.db_path))

    def _ensure_schema(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    task_id TEXT,
                    event_type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    source_refs_json TEXT NOT NULL,
                    created_utc TEXT NOT NULL,
                    entities_json TEXT,
                    score REAL
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_task ON events(task_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_score ON events(score DESC)")

    def insert(self, event: EventRecord, task_id: Optional[str] = None):
        with self._conn() as c:
            c.execute(
                """
                INSERT OR REPLACE INTO events
                (event_id, session_id, task_id, event_type, text, source_refs_json, created_utc, entities_json, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.session_id,
                    task_id,
                    event.event_type,
                    event.text,
                    _source_refs_to_json(event.source_refs),
                    event.created_utc,
                    json.dumps(event.entities) if event.entities else None,
                    event.score,
                ),
            )

    def insert_many(self, events: List[EventRecord], task_id: Optional[str] = None):
        for e in events:
            self.insert(e, task_id=task_id)

    def get_by_session_id(self, session_id: str) -> List[EventRecord]:
        return self._query("SELECT * FROM events WHERE session_id = ? ORDER BY score DESC", (session_id,))

    def get_by_task_id(self, task_id: str, limit: Optional[int] = None) -> List[EventRecord]:
        sql = "SELECT * FROM events WHERE task_id = ? ORDER BY score DESC"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return self._query(sql, (task_id,))

    def get_by_event_type(self, session_id: str, event_type: str) -> List[EventRecord]:
        return self._query(
            "SELECT * FROM events WHERE session_id = ? AND event_type = ? ORDER BY score DESC",
            (session_id, event_type),
        )

    def get_top_by_score(self, session_id: str, k: int = 20) -> List[EventRecord]:
        return self._query(
            "SELECT * FROM events WHERE session_id = ? ORDER BY score DESC LIMIT ?",
            (session_id, k),
        )

    def _query(self, sql: str, params: tuple) -> List[EventRecord]:
        with self._conn() as c:
            c.row_factory = sqlite3.Row
            rows = c.execute(sql, params).fetchall()
        out: List[EventRecord] = []
        for r in rows:
            out.append(
                EventRecord(
                    schema_version="v1",
                    session_id=r["session_id"],
                    event_id=r["event_id"],
                    event_type=r["event_type"],
                    text=r["text"],
                    source_refs=_source_refs_from_json(r["source_refs_json"]),
                    created_utc=r["created_utc"],
                    entities=json.loads(r["entities_json"]) if r["entities_json"] else None,
                    score=r["score"],
                )
            )
        return out
