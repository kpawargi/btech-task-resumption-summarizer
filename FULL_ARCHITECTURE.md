# Task Resumption Summarizer: Complete Architecture

## Project Goal

Build an end-to-end system that **extracts key information from task sessions** (reading, coding, meetings) and **summarizes progress, decisions, and TODOs** to help users resume work quickly.

---

## High-Level Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT: Text/Diff/Transcript                                    │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────┐
│ Slice-1: CAPTURE + PREPROCESS (Krish)       │
│ • Load file via adapter (reading/code/tx)   │
│ • Clean text + normalize                    │
│ • Split into sentences                      │
│ • Chunk by token budget (220 tokens)        │
│ • Save to disk with metadata                │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ Slice-2: EVENT EXTRACTION (Arush/You)       │
│ • Detect events: TODO, DECISION, ACTION...  │
│ • Link to source chunks (evidence)          │
│ • Score by importance                       │
│ • Extract code entities (functions, files)  │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ Slice-3: RETRIEVAL (Dhyey)                  │
│ • Embed events + chunks                     │
│ • Semantic + lexical retrieval (BM25)       │
│ • Pack top-k into ContextBundle             │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ Slice-4: SUMMARIZATION (Gaurav)             │
│ • LLM-based summary generation              │
│ • Output structured resume (TODO/Decision..)│
│ • Ground summary with evidence refs         │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ OUTPUT: Task Resume Summary + UI             │
│ Structured: Context | Progress | TODOs |... │
└──────────────────────────────────────────────┘
```

---

## Slice-1: Capture + Preprocess (Krish's Work)

### Purpose
Convert raw input files into **clean, chunked text** with metadata.

### Files
- `src/adapters/base.py` — Abstract adapter class
- `src/adapters/reading_adapter.py` — Load `.txt` files (articles, docs)
- `src/adapters/coding_adapter.py` — Load `.diff` files (code changes)
- `src/adapters/transcript_adapter.py` — Load transcript `.txt` (meeting notes)
- `src/preprocess/cleaner.py` — Text normalization
- `src/preprocess/sentence_splitter.py` — Split into sentences
- `src/preprocess/chunker.py` — Pack sentences into token-budget chunks
- `src/pipeline/capture_preprocess.py` — Orchestrate the flow
- `src/session_manager.py` — Create session directory + metadata
- `scripts/slice1_run.py` — CLI entry point

### Data Structures (src/schemas.py)

**Input:** Raw file (any source type)

**Output:** `ChunkSet` (saved as `chunkset_index.json`)
```python
ChunkSet {
  schema_version: "v1"
  session_id: "abc-123-def"     # UUID for this capture session
  task_id: "TASK001"             # Stable user task identifier
  source_type: "reading|code|transcript"
  source_path: "/path/to/file"
  chunks: [
    ChunkRecord {
      chunk_id: "chunk_0001"
      text: "..."                # Clean text
      token_count: 215           # Approx tokens
      char_start: 0
      char_end: 1250
    }
  ]
}
```

### Run Slice-1
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/slice1_run.py \
  --source reading \
  --path data/samples/reading_sample.txt \
  --task_id TASK001 \
  --outdir outputs
```

**Output:** `outputs/{uuid}/chunkset_index.json` + metadata

---

## Slice-2: Event Extraction (Arush/You)

### Purpose
Extract **structured events** from chunks and **rank by importance**.

### Files
- `src/events/extractor.py` — Rule-based pattern extraction
- `src/events/scorer.py` — Importance scoring (recency + salience)
- `src/events/entity_extractor.py` — Code entity extraction
- `scripts/03_extract_events.py` — CLI entry point

### Data Structures (src/schemas.py) - NEW

**Input:** `ChunkSet` (chunks from Slice-1)

**Output:** `EventSet` (saved as `events.json`)
```python
EventSet {
  schema_version: "v1"
  session_id: "abc-123-def"
  task_id: "TASK001"
  events: [
    EventRecord {
      event_id: "evt_abc123"
      event_type: "TODO|DECISION|ACTION|ISSUE|NOTE"
      text: "Add preprocessing pipeline"
      score: 0.95                # Importance (0.0 - 1.0)
      source_refs: [
        SourceRef {
          chunk_id: "chunk_0001"
          char_start: 50         # Evidence location
          char_end: 77
        }
      ]
      entities: ["fn:preprocess", "file:utils.py"]  # For code
      created_utc: "2026-03-03T11:47:13+00:00"
    }
  ]
}
```

### Event Types & Patterns

| Type | Patterns | Example |
|---|---|---|
| **TODO** | `TODO`, `FIXME`, `TBD` | "TODO: Add error handling" |
| **DECISION** | `decided`, `agreed`, `will` | "We decided to use BART" |
| **ACTION** | `implemented`, `fixed`, `added` | "Fixed the tokenizer bug" |
| **ISSUE** | `bug`, `error`, `failed`, `crash` | "Error in preprocessing step" |
| **NOTE** | (fallback for all text) | "The API is slow" |

### Scoring Algorithm

For each event:
```
score = type_weight × (0.5 × recency_score + 0.5 × salience_score)

recency_score ∈ [0.95, 1.0]  # Earlier events decayed
salience_score = 0.5 + keyword_hits/5 + entity_count/3 + text_length/20
```

### Run Slice-2
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/03_extract_events.py \
  --session_dir outputs/{session_uuid}
```

**Output:** `outputs/{uuid}/events/events.json`

---

## Slice-3: Retrieval (Dhyey - Future)

### Purpose
**Retrieve relevant events/chunks** to pass to summarizer.

### Expected Input
- `EventSet` from Slice-2 (events.json)
- `ChunkSet` from Slice-1 (chunkset_index.json)
- User query: "What did I work on?"

### Expected Output
**ContextBundle** (to be defined in schemas.json)
```json
{
  "selected_events": [... top-k events by relevance ...],
  "selected_chunks": [... top-k chunks by relevance ...],
  "evidence_map": {
    "evt_abc": ["chunk_001", "chunk_003"]
  }
}
```

### Tasks
- Embed events using an LLM/transformer
- Semantic retrieval (cosine similarity)
- Lexical retrieval (BM25 for code identifiers)
- Hybrid merge + rank
- MMR redundancy filtering

---

## Slice-4: Summarization (Gaurav - Future)

### Purpose
**Generate a readable resume summary** from retrieved context.

### Expected Input
- `ContextBundle` from Slice-3
- Previous `SummaryState` (for incremental updates)

### Expected Output
**SummaryState** (already defined in schemas.json)
```json
{
  "summary": {
    "context": "Working on transformer-based summarization...",
    "progress": "Completed chunking & event extraction",
    "decisions": ["Use BART as baseline", "220-token chunks"],
    "todos": ["Add retrieval", "Implement summarizer"],
    "blockers": [],
    "evidence_refs": [
      {"chunk_id": "chunk_0001", "note": "Defines project scope"}
    ]
  }
}
```

### Tasks
- Use HF Transformers (BART/T5) for abstractive summarization
- Ground summary with evidence
- Extract structured fields (TODO, Decision, etc.)
- Implement incremental updates (rolling summary)

---

## Project Structure Overview

```
project-root/
├── README.md                          # High-level overview
├── EVENT_EXTRACTION_README.md        # Slice-2 details (you created)
├── requirements.txt                   # Dependencies
│
├── schemas/                           # Data contracts (locked)
│   ├── SessionPayload.json
│   ├── Chunk.json
│   ├── ChunkSetIndex.json
│   ├── EventRecord.json               # YOUR data
│   ├── ContextBundle.json             # Dhyey's output
│   └── SummaryState.json              # Gaurav's output
│
├── src/
│   ├── __init__.py
│   ├── config.py                      # Configuration
│   ├── schemas.py                     # Python dataclasses (mirrors JSON schemas)
│   ├── utils.py                       # Utilities (JSON I/O, timestamps)
│   │
│   ├── adapters/                      # Slice-1 (Krish)
│   │   ├── base.py
│   │   ├── reading_adapter.py
│   │   ├── transcript_adapter.py
│   │   └── coding_adapter.py
│   │
│   ├── preprocess/                    # Slice-1 (Krish)
│   │   ├── cleaner.py
│   │   ├── sentence_splitter.py
│   │   └── chunker.py
│   │
│   ├── pipeline/                      # Slice-1 (Krish)
│   │   └── capture_preprocess.py
│   │
│   ├── session_manager.py             # Slice-1 (Krish)
│   │
│   └── events/                        # Slice-2 (You)
│       ├── __init__.py
│       ├── extractor.py               # Pattern-based extraction
│       ├── scorer.py                  # Importance scoring
│       └── entity_extractor.py        # Code entity extraction
│
├── scripts/
│   ├── __init__.py
│   ├── slice1_run.py                  # Slice-1 CLI (Krish)
│   └── 03_extract_events.py           # Slice-2 CLI (You)
│
└── data/
    └── samples/
        ├── reading_sample.txt
        ├── transcript_sample.txt
        └── coding_sample.diff
```

---

## Data Flow by Week

### Week 2 (Current - Event Extraction)
```
Slice-1 (chunks)
      ↓
  [03_extract_events.py]  ← You implement this
      ↓
Slice-2 (events) → Ready for Dhyey
```

### Week 3 (Improve Events + Dhyey Starts Retrieval)
```
Slice-2 (improved events with scoring)
      ↓
  [Dhyey's retrieval]
      ↓
Slice-3 (ContextBundle) → Ready for Gaurav
```

### Week 4+ (Full Pipeline)
```
Slice-1 → Slice-2 → Slice-3 → Slice-4 → UI
(Krish) → (You)   → (Dhyey) → (Gaurav)
```

---

## Testing & Validation

### Sample Runs (Already Done)

**Task 1 (Reading):**
```bash
outputs/aff68022-e76e-4042-b657-2784d276dea6/
└── events/events.json          # 1 NOTE event, score=0.85
```

**Task 2 (Transcript):**
```bash
outputs/73ad18e3-4743-49bf-99ff-1b70fea154b9/
└── events/events.json          # 1 DECISION event, score=1.00
```

**Task 3 (Code):**
```bash
outputs/ff93b3cf-f14d-48be-9651-497a1ee9822e/
└── events/events.json          # 1 TODO event with entities, score=1.00
```

---

## Key Design Decisions

1. **Contract-driven** — All slices use locked JSON schemas for I/O
2. **Modular** — Each slice is independent; can mock others' output
3. **CLI-based** — Each stage has a script (`slice1_run.py`, `03_extract_events.py`, etc.)
4. **Evidence-linked** — Events point back to source chunks (for grounding)
5. **Importance-scored** — Early ranking (Slice-2) to guide downstream retrieval

---

## Next Steps

### Immediate (Weeks 2-3)
- Implement event extraction
- Improve patterns & entity extraction
- Add salience scoring refinement

### Medium Term (Weeks 3-4)
- Dhyey: Embedding + retrieval (Slice-3)
- Integrate ContextBundle output
- Gaurav: Summarization pipeline (Slice-4)

### Long Term (Weeks 5-6)
- Optimization (quantization, caching)
- Evaluation on real task sessions
- Evidence grounding validation

---

## Dependencies

- Python 3.8+
- No external ML dependencies yet (Slice-3/4 will use HuggingFace)
- Uses only stdlib: `json`, `re`, `uuid`, `pathlib`, `datetime`

---

## Questions?

- **Krish:** How are chunks structured? → See `Chunk.json` schema
- **You (Arush):** What events should I extract? → See Event Types table above
- **Dhyey:** What input do I get? → `EventSet` from `03_extract_events.py`
- **Gaurav:** What should my summary look like? → See `SummaryState.json` schema
