import pytest
from src.memory.event_extractor import extract_events_from_text, EVENT_TYPES


def test_extract_todo():
    text = "We have TODO: add preprocessing pipeline and FIXME: handle empty input."
    events = extract_events_from_text(text)
    todos = [e for e in events if e[0] == "TODO"]
    assert len(todos) >= 1
    assert any("preprocessing" in e[1] or "add" in e[1] for e in todos)


def test_extract_note():
    text = "NOTE: Use chunking with token budget. Note: keep overlap configurable."
    events = extract_events_from_text(text)
    notes = [e for e in events if e[0] == "NOTE"]
    assert len(notes) >= 1


def test_extract_decision():
    text = "The main decision was to build a thin vertical slice first. We agreed to start with capture."
    events = extract_events_from_text(text)
    decs = [e for e in events if e[0] == "DECISION"]
    assert len(decs) >= 1


def test_extract_planned_action():
    text = "I planned to compare BART and T5 as baselines. Next steps are to implement adapters."
    events = extract_events_from_text(text)
    assert len(events) >= 1
    types = {e[0] for e in events}
    assert types.intersection({"ACTION", "DECISION"})


def test_extract_from_reading_sample():
    text = (
        "Today I resumed reading a chapter on transformer models. "
        "Finally, I planned to compare BART and T5 as baselines."
    )
    events = extract_events_from_text(text)
    assert len(events) >= 1
    for event_type, _ in events:
        assert event_type in EVENT_TYPES


def test_empty_text():
    assert extract_events_from_text("") == []
    assert extract_events_from_text("   \n  ") == []
