# Getting Started: Complete End-to-End Pipeline

This guide walks through the entire task resumption pipeline from raw input to extracted events.

## Quick Overview

```
Input File → Slice-1: Capture+Preprocess → Chunks → Slice-2: Event Extraction → Events
       ↓                                        ↓                                      ↓
[.txt/.diff]                              [chunkset_index.json]              [events.json]
                                                                                      ↓
                                          Next: Slice-3 (Dhyey) - Retrieval
                                                    ↓
                                          Next: Slice-4 (Gaurav) - Summarization
```

---

## Setup

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 1: Run Slice-1 (Capture + Preprocess)

Slice-1 reads a file, cleans it, splits into sentences, and chunks by token budget.

### Command
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/slice1_run.py \
  --source <source_type> \
  --path <input_file> \
  --task_id <task_id> \
  --outdir outputs \
  --token_budget 220
```

### Parameters

| Parameter | Options | Example |
|-----------|---------|---------|
| `--source` | `reading`, `transcript`, `code` | `reading` |
| `--path` | Path to input file | `data/samples/reading_sample.txt` |
| `--task_id` | Unique task identifier | `TASK001` |
| `--token_budget` | Max tokens per chunk (default: 220) | `220` |

---

## Example 1: Reading Source

### Input File
**File:** `data/samples/reading_sample.txt`
```
Today I resumed reading a chapter on transformer models. The key idea is self-attention, which allows each token to attend to all others.
I want a quick recap of what I understood last time. I also noted that long documents require chunking strategies.
Finally, I planned to compare BART and T5 as baselines.
```

### Run Command
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/slice1_run.py \
  --source reading \
  --path data/samples/reading_sample.txt \
  --task_id TASK001 \
  --outdir outputs
```

### Output
```
DONE
Session output directory: outputs/aff68022-e76e-4042-b657-2784d276dea6
```

### Output Files
```
outputs/aff68022-e76e-4042-b657-2784d276dea6/
├── session.json
├── chunkset_index.json        (Main output - chunks)
└── chunks.jsonl               (Alternative format)
```

### Sample Output: chunkset_index.json
```json
{
  "schema_version": "v1",
  "session_id": "aff68022-e76e-4042-b657-2784d276dea6",
  "task_id": "TASK001",
  "source_type": "reading",
  "source_path": "data/samples/reading_sample.txt",
  "chunks": [
    {
      "schema_version": "v1",
      "session_id": "aff68022-e76e-4042-b657-2784d276dea6",
      "chunk_id": "chunk_0001",
      "source_type": "reading",
      "text": "Today I resumed reading a chapter on transformer models. The key idea is self-attention, which allows each token to attend to all others. I want a quick recap of what I understood last time. I also noted that long documents require chunking strategies. Finally, I planned to compare BART and T5 as baselines.",
      "token_count": 66,
      "char_start": 0,
      "char_end": 308
    }
  ]
}
```

---

## Example 2: Transcript Source

### Input File
**File:** `data/samples/transcript_sample.txt`
```
Speaker 1: Today we discussed the project plan. The main decision was to build a thin vertical slice first.
Speaker 2: Yes, and we agreed the first slice should include capture, preprocess, and chunking.
Speaker 1: Next steps are to implement adapters and save chunk sets to disk.
```

### Run Command
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/slice1_run.py \
  --source transcript \
  --path data/samples/transcript_sample.txt \
  --task_id TASK002 \
  --outdir outputs
```

### Output
```
outputs/73ad18e3-4743-49bf-99ff-1b70fea154b9/
├── session.json
└── chunkset_index.json
```

---

## Example 3: Code/Diff Source

### Input File
**File:** `data/samples/coding_sample.diff`
```diff
diff --git a/app.py b/app.py
index 2c174a1..a9d19af 100644
--- a/app.py
+++ b/app.py
@@ -1,5 +1,12 @@
 def main():
-    print("Hello")
+    print("Hello")
+    # TODO: Add preprocessing pipeline
+    # NOTE: Use chunking with token budget
+
+def preprocess(text):
+    # placeholder
+    return text
```

### Run Command
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/slice1_run.py \
  --source code \
  --path data/samples/coding_sample.diff \
  --task_id TASK003 \
  --outdir outputs
```

### Output
```
outputs/ff93b3cf-f14d-48be-9651-497a1ee9822e/
├── session.json
└── chunkset_index.json
```

---

## Step 2: Run Slice-2 (Event Extraction)

Slice-2 extracts structured events from chunks and scores them by importance.

### Command
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/03_extract_events.py \
  --session_dir outputs/<session_uuid>
```

### Example: Extract Events from Reading

```bash
PYTHONPATH=$PYTHONPATH:. python scripts/03_extract_events.py \
  --session_dir outputs/aff68022-e76e-4042-b657-2784d276dea6
```

### Console Output
```
Loading chunks from outputs/aff68022-e76e-4042-b657-2784d276dea6...
Loaded 1 chunks
Extracting events...
Extracted 1 raw events
Scoring events by importance...
Enriching with entity extraction...
Saving events to outputs/aff68022-e76e-4042-b657-2784d276dea6/events/events.json...

Extracted 1 events from reading source
Breakdown: NOTE=1

Top 5 events by importance:
1. [NOTE] (score=0.85) Today I resumed reading a chapter on transformer models...

Done.
Event file: outputs/aff68022-e76e-4042-b657-2784d276dea6/events/events.json
```

### Output Files
```
outputs/aff68022-e76e-4042-b657-2784d276dea6/
├── events/
│   └── events.json            (Main output - extracted events)
├── chunkset_index.json        (From Slice-1)
└── session.json
```

### Sample Output: events.json
```json
{
  "schema_version": "v1",
  "session_id": "aff68022-e76e-4042-b657-2784d276dea6",
  "task_id": "TASK001",
  "events": [
    {
      "schema_version": "v1",
      "session_id": "aff68022-e76e-4042-b657-2784d276dea6",
      "event_id": "evt_4824f9e47154",
      "event_type": "NOTE",
      "text": "Today I resumed reading a chapter on transformer models The key idea is self-attention, which allows each token to attend to all others",
      "source_refs": [
        {
          "chunk_id": "chunk_0001",
          "char_start": null,
          "char_end": null
        }
      ],
      "created_utc": "2026-03-03T11:46:46+00:00",
      "entities": null,
      "score": 0.85
    }
  ]
}
```

---

## Example: Code Events with Entities

### Run Command
```bash
PYTHONPATH=$PYTHONPATH:. python scripts/03_extract_events.py \
  --session_dir outputs/ff93b3cf-f14d-48be-9651-497a1ee9822e
```

### Console Output
```
Loading chunks from outputs/ff93b3cf-f14d-48be-9651-497a1ee9822e...
Loaded 1 chunks
Extracting events...
Extracted 1 raw events
Scoring events by importance...
Enriching with entity extraction...
Saving events to outputs/ff93b3cf-f14d-48be-9651-497a1ee9822e/events/events.json...

Extracted 1 events from code source
Breakdown: TODO=1

Top 5 events by importance:
1. [TODO] (score=1.00) py @@ -1,5 +1,12 @@ def main(): print("Hello...

Done.
Event file: outputs/ff93b3cf-f14d-48be-9651-497a1ee9822e/events/events.json
```

### Sample Output: events.json (Code)
```json
{
  "schema_version": "v1",
  "session_id": "ff93b3cf-f14d-48be-9651-497a1ee9822e",
  "task_id": "TASK003",
  "events": [
    {
      "schema_version": "v1",
      "session_id": "ff93b3cf-f14d-48be-9651-497a1ee9822e",
      "event_id": "evt_377d2ffa3a73",
      "event_type": "TODO",
      "text": "Add preprocessing pipeline",
      "source_refs": [
        {
          "chunk_id": "chunk_0001",
          "char_start": 153,
          "char_end": 157
        }
      ],
      "created_utc": "2026-03-03T11:47:13+00:00",
      "entities": [
        "fn:main",
        "fn:preprocess"
      ],
      "score": 1.0
    }
  ]
}
```

---

## Event Types Reference

| Type | Patterns | Example |
|------|----------|---------|
| **TODO** | `TODO`, `FIXME`, `TBD`, `need to`, `to do` | "TODO: Add error handling" |
| **DECISION** | `decided`, `agreed`, `will`, `plan to` | "We decided to use BART" |
| **ACTION** | `implemented`, `fixed`, `added`, `created` | "Fixed the tokenizer bug" |
| **ISSUE** | `bug`, `error`, `failed`, `crash`, `problem` | "Error in preprocessing" |
| **NOTE** | (fallback for all text) | "The API is slow" |

---

## Interpreting Scores

Events are scored 0.0 to 1.0 based on:
- **Recency:** Newer events score higher
- **Type weight:** DECISION/ISSUE/TODO scored higher than NOTE
- **Salience:** Keyword frequency, entity presence, text length

| Score Range | Interpretation |
|---|---|
| 0.8 - 1.0 | High importance |
| 0.6 - 0.8 | Medium importance |
| 0.4 - 0.6 | Low-medium importance |
| 0.0 - 0.4 | Low importance |

---

## Interpreting Entities (Code)

For code diffs, entity extraction finds:
- `fn:function_name` — Function definitions
- `file:path/to/file.py` — Modified files
- `error_code:E123` — Error codes

Example from coding sample:
```json
"entities": ["fn:main", "fn:preprocess"]
```

---

## Complete End-to-End Example

### Run All Steps
```bash
# Step 1: Capture + Preprocess
PYTHONPATH=$PYTHONPATH:. python scripts/slice1_run.py \
  --source reading \
  --path data/samples/reading_sample.txt \
  --task_id TASK_COMPLETE_TEST \
  --outdir outputs

# Save the session UUID
SESSION_UUID="aff68022-e76e-4042-b657-2784d276dea6"  # From output above

# Step 2: Extract Events
PYTHONPATH=$PYTHONPATH:. python scripts/03_extract_events.py \
  --session_dir outputs/$SESSION_UUID

# View Final Output
cat outputs/$SESSION_UUID/events/events.json | python -m json.tool
```

---

## Understanding the File Structure

```
project/
├── src/
│   ├── adapters/
│   │   ├── reading_adapter.py     (Load .txt files)
│   │   ├── transcript_adapter.py  (Load transcript .txt)
│   │   ├── coding_adapter.py      (Load .diff files)
│   │   └── base.py                (Abstract adapter)
│   │
│   ├── preprocess/
│   │   ├── cleaner.py             (Normalize text)
│   │   ├── sentence_splitter.py   (Split sentences)
│   │   ├── chunker.py             (Chunk by token budget)
│   │   └── __init__.py
│   │
│   ├── events/
│   │   ├── extractor.py           (Pattern-based extraction)
│   │   ├── scorer.py              (Importance scoring)
│   │   ├── entity_extractor.py    (Code entity extraction)
│   │   └── __init__.py
│   │
│   ├── pipeline/
│   │   └── capture_preprocess.py  (Orchestrate Slice-1)
│   │
│   ├── schemas.py                 (Data structures)
│   ├── session_manager.py         (Session handling)
│   └── utils.py                   (Utilities)
│
├── scripts/
│   ├── slice1_run.py              (CLI for Slice-1)
│   └── 03_extract_events.py       (CLI for Slice-2)
│
├── schemas/
│   ├── Chunk.json
│   ├── EventRecord.json
│   ├── SessionPayload.json
│   └── (other schema definitions)
│
├── data/
│   └── samples/
│       ├── reading_sample.txt
│       ├── transcript_sample.txt
│       └── coding_sample.diff
│
└── outputs/                       (Generated during runs)
    └── <session_uuid>/
        ├── session.json
        ├── chunkset_index.json
        └── events/
            └── events.json
```

---

## Next Steps

### For Slice-3 (Retrieval - Dhyey)
- Input: `outputs/<session_id>/events/events.json` + `chunkset_index.json`
- Output: `context_bundle.json` with ranked/retrieved events

### For Slice-4 (Summarization - Gaurav)
- Input: `context_bundle.json` from Slice-3
- Output: `summary_state.json` with structured resume

---

## Troubleshooting

### ModuleNotFoundError: No module named 'src'
```bash
# Solution: Add PYTHONPATH
PYTHONPATH=$PYTHONPATH:. python scripts/slice1_run.py ...
```

### No chunks extracted
- Check input file exists
- Check file format matches source type (reading=.txt, code=.diff)

### No events extracted
- Check chunks were created (chunkset_index.json exists)
- Check patterns match your text (patterns are case-insensitive regex)

---

## Documentation Files

- **EVENT_EXTRACTION_README.md** — Details on Slice-2 (event extraction)
- **FULL_ARCHITECTURE.md** — System design and integration
- **This file** — Getting started guide with examples
