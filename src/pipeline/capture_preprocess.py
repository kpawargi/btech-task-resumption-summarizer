from pathlib import Path
from typing import List

from src.config import SliceConfig
from src.schemas import ChunkRecord, ChunkSet
from src.session_manager import create_session, SCHEMA_VERSION
from src.utils import append_jsonl, write_json

from src.adapters.reading_adapter import ReadingAdapter
from src.adapters.transcript_adapter import TranscriptAdapter
from src.adapters.coding_adapter import CodingDiffAdapter

from src.preprocess.cleaner import clean_text
from src.preprocess.sentence_splitter import split_sentences_with_spans
from src.preprocess.chunker import chunk_by_token_budget


def _get_adapter(source_type: str):
    if source_type == "reading":
        return ReadingAdapter()
    if source_type == "transcript":
        return TranscriptAdapter()
    if source_type == "code":
        return CodingDiffAdapter()
    raise ValueError(f"Unknown source_type: {source_type}")


def run_capture_preprocess(
    cfg: SliceConfig,
    source_type: str,
    input_path: Path,
    task_id: str,
) -> Path:
    # 1) Create session
    session, session_dir = create_session(
        output_base_dir=cfg.output_base_dir,
        task_id=task_id,
        source_type=source_type,
        source_path=str(input_path),
    )

    # 2) Capture (adapter load)
    adapter = _get_adapter(source_type)
    payload = adapter.load(input_path)
    raw_text: str = payload["raw_text"]

    # 3) Clean
    text = clean_text(raw_text) if cfg.text_cleaning else raw_text

    # 4) Sentence split (with spans)
    sentence_spans = split_sentences_with_spans(text)

    # 5) Chunk by token budget
    chunk_tuples = chunk_by_token_budget(
        sentence_spans=sentence_spans,
        token_budget=cfg.token_budget,
        overlap_tokens=cfg.overlap_tokens,
        min_chunk_tokens=cfg.min_chunk_tokens,
    )

    # 6) Build ChunkSet records
    chunks: List[ChunkRecord] = []
    for idx, (chunk_text, c_start, c_end, tok) in enumerate(chunk_tuples, start=1):
        chunks.append(
            ChunkRecord(
                schema_version=SCHEMA_VERSION,
                session_id=session.session_id,
                chunk_id=f"chunk_{idx:04d}",
                source_type=source_type,
                text=chunk_text,
                token_count=int(tok),
                char_start=int(c_start),
                char_end=int(c_end),
            )
        )

    chunkset = ChunkSet(
        schema_version=SCHEMA_VERSION,
        session_id=session.session_id,
        task_id=task_id,
        source_type=source_type,
        source_path=str(input_path),
        chunks=chunks,
    )

    # 7) Save to disk (JSONL chunks + index JSON)
    chunks_path = session_dir / "chunks.jsonl"
    for c in chunks:
        append_jsonl(chunks_path, c.to_dict())

    write_json(session_dir / "chunkset_index.json", chunkset.to_dict())

    return session_dir
