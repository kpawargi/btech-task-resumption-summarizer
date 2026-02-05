import tempfile
from pathlib import Path

import pytest
from src.event_schemas import EventRecord, SourceRef
from src.memory.event_store import EventStore


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d) / "events.db"


@pytest.fixture
def sample_events():
    ref = SourceRef(chunk_id="chunk_0001", char_start=0, char_end=50)
    return [
        EventRecord(
            schema_version="v1",
            session_id="sess-12345678",
            event_id="evt_abc123",
            event_type="TODO",
            text="Add tests",
            source_refs=[ref],
            created_utc="2026-02-01T12:00:00Z",
            score=0.9,
        ),
        EventRecord(
            schema_version="v1",
            session_id="sess-12345678",
            event_id="evt_def456",
            event_type="DECISION",
            text="Use SQLite for event store",
            source_refs=[ref],
            created_utc="2026-02-01T12:00:00Z",
            score=0.85,
        ),
    ]


def test_insert_and_get_by_session(temp_db, sample_events):
    store = EventStore(temp_db)
    store.insert_many(sample_events, task_id="TASK001")

    out = store.get_by_session_id("sess-12345678")
    assert len(out) == 2
    ids = {e.event_id for e in out}
    assert "evt_abc123" in ids and "evt_def456" in ids
    assert all(e.source_refs for e in out)


def test_get_by_task_id(temp_db, sample_events):
    store = EventStore(temp_db)
    store.insert_many(sample_events, task_id="TASK001")
    out = store.get_by_task_id("TASK001")
    assert len(out) == 2
    out_lim = store.get_by_task_id("TASK001", limit=1)
    assert len(out_lim) == 1


def test_get_by_event_type(temp_db, sample_events):
    store = EventStore(temp_db)
    store.insert_many(sample_events, task_id="TASK001")
    todos = store.get_by_event_type("sess-12345678", "TODO")
    assert len(todos) == 1
    assert todos[0].event_type == "TODO"


def test_get_top_by_score(temp_db, sample_events):
    store = EventStore(temp_db)
    store.insert_many(sample_events, task_id="TASK001")
    top = store.get_top_by_score("sess-12345678", k=1)
    assert len(top) == 1
    assert top[0].event_type == "TODO"
