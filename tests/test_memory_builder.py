from pathlib import Path

import pytest
from src.memory.builder import run_memory_build

SESSION_DIR = Path(__file__).resolve().parent.parent / "outputs" / "459ad443-6c0c-44dc-ad58-d2719c89803a"


@pytest.mark.skipif(not SESSION_DIR.is_dir(), reason="Session dir not found; run slice1 first")
def test_run_memory_build_on_krish_output():
    events, task_id = run_memory_build(SESSION_DIR)
    assert task_id == "TASK001"
    assert isinstance(events, list)
    assert len(events) >= 0
    for ev in events:
        assert ev.session_id
        assert ev.event_id.startswith("evt_")
        assert ev.event_type in ("ACTION", "DECISION", "TODO", "ISSUE", "NOTE")
        assert ev.text
        assert len(ev.source_refs) >= 1
        assert ev.source_refs[0].chunk_id == "chunk_0001"


def test_run_memory_build_missing_dir():
    with pytest.raises(FileNotFoundError):
        run_memory_build(Path("/nonexistent/session/dir"))
