# JSONL Chunk File Contract (chunks.jsonl)

## Purpose
`chunks.jsonl` is the primary output artifact of Slice-1 (Capture + Preprocess).  
It contains one JSON object per line, where each object represents a **single Chunk**.

This file acts as a stable contract so downstream modules (memory builder, retrieval, summarizer, UI) can work independently.

---

## File Location
For a given session:

outputs/<session_id>/chunks.jsonl

---

## Format
- Encoding: UTF-8
- Newline: `\n`
- Each line MUST be a valid JSON object.
- There MUST be no commas between lines (this is not a JSON array).
- Empty lines are not allowed.

---

## Schema
Each JSON object MUST validate against:

schemas/Chunk.json

---

## Required Fields Per Line (Chunk)
Each line MUST include:

- `schema_version` (string, e.g., "v1")
- `session_id` (string UUID)
- `chunk_id` (string like `chunk_0001`)
- `source_type` (one of: `reading`, `transcript`, `code`)
- `text` (non-empty string)
- `token_count` (integer >= 1)
- `char_start` (integer >= 0)
- `char_end` (integer >= 0)

Optional:
- `meta` (object)

---

## Chunk Ordering Rules
- Recommended: chunks should be written in increasing order of `chunk_id` (chunk_0001, chunk_0002, …).
- `char_start` should be non-decreasing with chunk order.
- Overlap is allowed if overlap chunking is enabled (then `char_start` may move backward slightly).

---

## Consistency Rules
- All chunks in the same file MUST have the same `session_id`.
- All chunks in the same file SHOULD have the same `source_type`.
- `char_end` must be >= `char_start`.
- The `text` should correspond to the substring span from the cleaned text version (best-effort).

---

## Example (2 lines)
{"schema_version":"v1","session_id":"7c6d...","chunk_id":"chunk_0001","source_type":"reading","text":"First chunk text...","token_count":120,"char_start":0,"char_end":480}
{"schema_version":"v1","session_id":"7c6d...","chunk_id":"chunk_0002","source_type":"reading","text":"Second chunk text...","token_count":110,"char_start":481,"char_end":940}

---

## Downstream Expectations
Downstream modules MAY assume:
- They can stream-read `chunks.jsonl` line-by-line.
- Each line is independently parseable (no need to load full file into memory).
- Each line conforms to `Chunk.json`.

Downstream modules MUST NOT assume:
- A fixed tokenization library was used (token_count is an estimate).
- Perfect sentence boundaries (depends on splitter).
- No overlap (overlap may be configured).

---

## Validation Recommendation
A simple validator should:
1. Read file line-by-line
2. Parse JSON
3. Validate each object with `schemas/Chunk.json`
4. Assert all `session_id` values are identical
