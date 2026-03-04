"""
load_events.py
Traverse the outputs/ directory, load all events.json files,
and extract event text + metadata into a flat list.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def load_all_events(outputs_dir: str | Path = "outputs") -> list[dict[str, Any]]:
    """
    Walk every TASK*/events/events.json under `outputs_dir` and return
    a flat list of event dicts, each enriched with its parent task_id.

    Args:
        outputs_dir: Path to the root outputs directory.

    Returns:
        List of dicts with keys:
            task_id, event_id, event_type, text, created_utc, score (original)
    """
    outputs_path = Path(outputs_dir)
    if not outputs_path.exists():
        raise FileNotFoundError(f"Outputs directory not found: {outputs_path.resolve()}")

    events: list[dict[str, Any]] = []

    for task_dir in sorted(outputs_path.iterdir()):
        if not task_dir.is_dir():
            continue

        events_file = task_dir / "events" / "events.json"
        if not events_file.exists():
            continue

        try:
            payload = json.loads(events_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[load_events] WARNING: could not read {events_file}: {exc}")
            continue

        task_id = payload.get("task_id", task_dir.name)

        for evt in payload.get("events", []):
            text = evt.get("text", "").strip()
            if not text:
                continue  # skip empty events

            events.append(
                {
                    "task_id": task_id,
                    "event_id": evt.get("event_id", ""),
                    "event_type": evt.get("event_type", ""),
                    "text": text,
                    "created_utc": evt.get("created_utc", ""),
                    "original_score": evt.get("score"),
                }
            )

    return events