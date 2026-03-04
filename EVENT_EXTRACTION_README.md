# Slice-2: Event Extraction & Importance Scoring

## Overview

This module extracts structured events from preprocessed text chunks and ranks them by importance. It's the second stage of the task resumption pipeline.

**Input:** Chunks from Slice-1 (capture + preprocess)  
**Output:** Structured events with importance scores and evidence links

---

## Features

### Event Types Extracted
- **TODO**: Tasks to be done (`TODO`, `FIXME`, `TBD`)
- **DECISION**: Decisions made (`agreed`, `decided`, `will`)
- **ACTION**: Completed actions (`implemented`, `fixed`, `added`)
- **ISSUE**: Problems found (`bug`, `error`, `failed`)
- **NOTE**: General observations (fallback category)

### Processing Pipeline

1. **Rule-based Extraction** — Regex patterns detect events in text
2. **Evidence Linking** — Each event links back to source chunk + character position
3. **Importance Scoring** — Events ranked by:
   - Recency (newer events score higher)
   - Salience (keyword frequency, entity presence)
   - Type weight (DECISION/ISSUE weighted higher than NOTE)
4. **Entity Extraction** — For code: extracts function names, file paths, error codes

---

## Usage

### Basic Command
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/03_extract_events.py \
  --session_dir outputs/<session_uuid>
```

### Output Structure
```
outputs/<session_uuid>/
├── events/
│   └── events.json          # Extracted events with scores
├── chunkset_index.json      # Input chunks (from Slice-1)
└── session.json             # Session metadata
```

### Sample Output (events.json)
```json
{
  "schema_version": "v1",
  "session_id": "abc-def-ghi",
  "task_id": "TASK001",
  "events": [
    {
      "event_id": "evt_abc123",
      "event_type": "TODO",
      "text": "Add preprocessing pipeline",
      "score": 0.95,
      "source_refs": [{"chunk_id": "chunk_0001", "char_start": 100, "char_end": 127}],
      "entities": ["fn:preprocess"],
      "created_utc": "2026-03-03T11:47:13+00:00"
    }
  ]
}
```

---

## Options

```bash
--session_dir PATH          # Required: Path to Slice-1 output
--outdir PATH               # Output directory (default: <session_dir>/events/)
--skip_scoring              # Skip importance scoring step
--skip_entities             # Skip entity extraction (for code)
```

---

## Expected Output Quality

| Source Type | Expected Events | Typical Score Range |
|---|---|---|
| **Reading** | NOTE, TODO, DECISION | 0.6 - 0.95 |
| **Transcript** | DECISION, ACTION, NOTE | 0.7 - 1.0 |
| **Code** | TODO, ISSUE, ACTION | 0.8 - 1.0 (with entities) |

---

## Integration with Other Slices

**Upstream (Slice-1):** Provides chunks  
**Downstream (Slice-3+):**
- Slice-3 (Dhyey): Uses events for embedding + retrieval
- Slice-4 (Gaurav): Summarizes retrieved events into resume

---

## Dependencies

- Python 3.8+
- No external dependencies (uses only stdlib regex + json)

---

## Files

- `src/events/extractor.py` — Pattern-based event extraction
- `src/events/scorer.py` — Importance scoring engine
- `src/events/entity_extractor.py` — Code entity extraction
- `scripts/03_extract_events.py` — CLI orchestrator
