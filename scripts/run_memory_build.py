import argparse
import json
from pathlib import Path

from src.memory.builder import run_memory_build
from src.memory.event_store import EventStore


def main():
    parser = argparse.ArgumentParser(description="Slice-2: Task Memory Builder (events + event store)")
    parser.add_argument("--session_dir", help="Path to session directory (e.g. outputs/<session_id>)")
    parser.add_argument("--session_id", help="Session UUID; used with --outdir to form session_dir")
    parser.add_argument("--outdir", default="outputs", help="Base output dir when using --session_id")
    parser.add_argument("--db", default="outputs/event_store.db", help="SQLite Event DB path")
    parser.add_argument("--write_events", action="store_true", help="Write events.jsonl into session dir")
    args = parser.parse_args()

    if args.session_dir:
        session_dir = Path(args.session_dir)
    elif args.session_id:
        session_dir = Path(args.outdir) / args.session_id
    else:
        raise SystemExit("Provide either --session_dir or --session_id")

    if not session_dir.is_dir():
        raise SystemExit(f"Session directory not found: {session_dir}")

    events, task_id = run_memory_build(session_dir)

    db_path = Path(args.db)
    store = EventStore(db_path)
    store.insert_many(events, task_id=task_id)

    print(f"Processed {len(events)} events for session {session_dir.name} (task_id={task_id})")
    print(f"Event DB: {db_path}")

    if args.write_events:
        out_path = session_dir / "events.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for ev in events:
                f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
        print(f"Wrote {out_path}")

    print("DONE")


if __name__ == "__main__":
    main()
