# Slice-1: Capture + Preprocess (Thin Vertical Slice)

This repo implements:
- Input adapters (reading text, transcript text, coding diff)
- Session manager (creates session_id, stores metadata)
- Preprocess: clean -> sentence split -> chunk by token budget
- Output: ChunkSet saved to disk

## Setup (Windows 11)
```bat
cd slice1_capture_preprocess
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
