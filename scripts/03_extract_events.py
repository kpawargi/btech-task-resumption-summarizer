"""
Slice-2: Event Extraction and Scoring

Reads chunks from Slice-1 output and extracts structured events (TODO, DECISION, ACTION, ISSUE, NOTE)
with importance scoring and entity extraction.
"""

import argparse
import json
from pathlib import Path
from typing import List, Optional

from src.schemas import ChunkRecord, ChunkSet, EventRecord, EventSet
from src.events.extractor import EventExtractor
from src.events.scorer import EventScorer
from src.events.entity_extractor import CodeEntityExtractor
from src.utils import write_json, safe_mkdir


def load_chunk_set_from_session(session_dir: Path) -> ChunkSet:
    """
    Load ChunkSet from session directory.
    Looks for chunkset_index.json in the session directory.
    """
    chunks_file = session_dir / "chunkset_index.json"
    if not chunks_file.exists():
        raise FileNotFoundError(f"chunkset_index.json not found in {session_dir}")

    with chunks_file.open("r") as f:
        data = json.load(f)

    # Reconstruct ChunkSet
    chunk_records = [
        ChunkRecord(
            schema_version=c["schema_version"],
            session_id=c["session_id"],
            chunk_id=c["chunk_id"],
            source_type=c["source_type"],
            text=c["text"],
            token_count=c["token_count"],
            char_start=c["char_start"],
            char_end=c["char_end"],
        )
        for c in data.get("chunks", [])
    ]

    chunk_set = ChunkSet(
        schema_version=data["schema_version"],
        session_id=data["session_id"],
        task_id=data["task_id"],
        source_type=data["source_type"],
        source_path=data["source_path"],
        chunks=chunk_records,
    )
    return chunk_set


def extract_events(chunk_set: ChunkSet) -> List[EventRecord]:
    """Extract events from chunks using rule-based extraction"""
    extractor = EventExtractor()
    events = extractor.extract_from_chunks(chunk_set.chunks, chunk_set.session_id)
    return events


def score_events(events: List[EventRecord]) -> List[EventRecord]:
    """Score events by importance"""
    scorer = EventScorer()
    events = scorer.score_events(events)
    events = scorer.sort_by_importance(events)
    return events


def enrich_with_entities(events: List[EventRecord], source_type: str) -> List[EventRecord]:
    """Add entity extraction (mainly for code)"""
    extractor = CodeEntityExtractor()
    events = extractor.enrich_events_with_entities(events, source_type)
    return events


def save_event_set(events: List[EventRecord], output_path: Path, task_id: str, session_id: str) -> None:
    """Save events to JSON file"""
    event_set = EventSet(
        schema_version="v1",
        session_id=session_id,
        task_id=task_id,
        events=events,
    )
    write_json(output_path, event_set.to_dict())


def print_event_summary(events: List[EventRecord], source_type: str) -> None:
    """Print summary of extracted events"""
    if not events:
        print("\nNo events extracted\n")
        return

    type_counts = {}
    for event in events:
        event_type = event.event_type
        type_counts[event_type] = type_counts.get(event_type, 0) + 1

    print(f"\nExtracted {len(events)} events from {source_type} source")
    print(f"Breakdown: {', '.join(f'{t}={c}' for t, c in sorted(type_counts.items()))}")

    # Show top 5 events by importance
    print("\nTop 5 events by importance:")
    for i, event in enumerate(events[:5], 1):
        score_str = f"{event.score:.2f}" if event.score else "N/A"
        print(f"{i}. [{event.event_type}] (score={score_str}) {event.text[:60]}...")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Slice-2: Event Extraction and Scoring"
    )
    parser.add_argument(
        "--session_dir",
        required=True,
        help="Path to session directory from slice1_run.py (e.g., outputs/<uuid>)",
    )
    parser.add_argument(
        "--outdir",
        default=None,
        help="Output directory (default: <session_dir>/events/)",
    )
    parser.add_argument(
        "--skip_scoring",
        action="store_true",
        help="Skip importance scoring step",
    )
    parser.add_argument(
        "--skip_entities",
        action="store_true",
        help="Skip entity extraction step",
    )
    args = parser.parse_args()

    session_dir = Path(args.session_dir)
    if not session_dir.exists():
        raise FileNotFoundError(f"Session directory not found: {session_dir}")

    # Load chunk set
    print(f"Loading chunks from {session_dir}...")
    chunk_set = load_chunk_set_from_session(session_dir)
    print(f"Loaded {len(chunk_set.chunks)} chunks")

    # Extract events
    print("Extracting events...")
    events = extract_events(chunk_set)
    print(f"Extracted {len(events)} raw events")

    # Score events
    if not args.skip_scoring:
        print("Scoring events by importance...")
        events = score_events(events)
    else:
        print("Skipping scoring")

    # Enrich with entities
    if not args.skip_entities:
        print("Enriching with entity extraction...")
        events = enrich_with_entities(events, chunk_set.source_type)
    else:
        print("Skipping entity extraction")

    # Save results
    output_dir = Path(args.outdir) if args.outdir else session_dir / "events"
    safe_mkdir(output_dir)
    output_file = output_dir / "events.json"

    print(f"Saving events to {output_file}...")
    save_event_set(events, output_file, chunk_set.task_id, chunk_set.session_id)

    # Print summary
    print_event_summary(events, chunk_set.source_type)
    print("Done.")
    print(f"Event file: {output_file}")


if __name__ == "__main__":
    main()
