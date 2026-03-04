"""Rule-based event extraction from chunks"""

import re
import uuid
from typing import List, Tuple, Dict, Any
from src.schemas import ChunkRecord, EventRecord, SourceRef
from src.utils import utc_now_iso


class EventExtractor:
    """Extract structured events (TODO, DECISION, ACTION, ISSUE, NOTE) from text chunks"""

    # Regex patterns for each event type
    PATTERNS = {
        "TODO": [
            r"TODO",
            r"FIXME",
            r"TBD",
            r"to do",
            r"need to",
        ],
        "DECISION": [
            r"decided to",
            r"we will",
            r"we chose",
            r"agreed on",
            r"decided that",
            r"we agreed",
            r"plan to",
        ],
        "ACTION": [
            r"implemented",
            r"fixed",
            r"added",
            r"created",
            r"removed",
            r"modified",
            r"updated",
            r"deployed",
            r"refactored",
            r"integrated",
            r"optimized",
        ],
        "ISSUE": [
            r"bug",
            r"error",
            r"failed",
            r"crash",
            r"broke",
            r"problem",
            r"issue",
            r"failure",
            r"exception",
        ],
    }

    def __init__(self):
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for event_type, patterns in self.PATTERNS.items():
            self.compiled_patterns[event_type] = [
                (re.compile(p, re.IGNORECASE), p) for p in patterns
            ]

    def extract_from_chunks(
        self, chunks: List[ChunkRecord], session_id: str
    ) -> List[EventRecord]:
        """
        Extract events from a list of chunks.

        Args:
            chunks: List of ChunkRecord objects
            session_id: Session ID for linking events

        Returns:
            List of EventRecord objects
        """
        events = []

        for chunk in chunks:
            chunk_events = self._extract_from_chunk(chunk, session_id)
            events.extend(chunk_events)

        return events

    def _extract_from_chunk(self, chunk: ChunkRecord, session_id: str) -> List[EventRecord]:
        """Extract events from a single chunk"""
        events = []
        text = chunk.text
        seen_positions = set()

        # Try each event type
        for event_type, compiled_patterns in self.compiled_patterns.items():
            for regex, _ in compiled_patterns:
                # Find all matches
                for match in regex.finditer(text):
                    match_pos = (match.start(), match.end(), event_type)
                    # Avoid duplicate extraction of overlapping matches
                    if match_pos in seen_positions:
                        continue
                    seen_positions.add(match_pos)

                    # Extract event text (sentence containing the match)
                    event_text = self._extract_event_sentence(text, match.start(), match.end())
                    if event_text:
                        event = EventRecord(
                            schema_version="v1",
                            session_id=session_id,
                            event_id=self._generate_event_id(),
                            event_type=event_type,
                            text=event_text,
                            source_refs=[
                                SourceRef(
                                    chunk_id=chunk.chunk_id,
                                    char_start=match.start(),
                                    char_end=match.end(),
                                )
                            ],
                            created_utc=utc_now_iso(),
                        )
                        events.append(event)

        # If no specific patterns matched, treat chunk as NOTE
        if not events and text.strip():
            events.append(
                EventRecord(
                    schema_version="v1",
                    session_id=session_id,
                    event_id=self._generate_event_id(),
                    event_type="NOTE",
                    text=self._extract_event_sentence(text, 0, len(text)),
                    source_refs=[SourceRef(chunk_id=chunk.chunk_id)],
                    created_utc=utc_now_iso(),
                )
            )

        return events

    def _extract_event_sentence(self, text: str, match_start: int, match_end: int) -> str:
        """
        Extract a full sentence containing the match.
        Returns up to 2 sentences for context.
        """
        # Sentence boundaries (., !, ?)
        sentence_pattern = r"[.!?]+"

        # Find sentence boundaries around the match
        sentences = re.split(sentence_pattern, text)
        if not sentences:
            return text[max(0, match_start - 50) : match_end + 50].strip()

        # Find which sentences contain the match
        current_pos = 0
        start_sentence_idx = 0
        end_sentence_idx = 0

        for i, sentence in enumerate(sentences):
            sentence_end = current_pos + len(sentence)
            if current_pos <= match_start < sentence_end:
                start_sentence_idx = i
            if current_pos < match_end <= sentence_end:
                end_sentence_idx = i
                break
            current_pos = sentence_end + 1  # +1 for separator

        # Join up to 2 sentences for context
        extracted_sentences = sentences[
            start_sentence_idx : min(end_sentence_idx + 2, len(sentences))
        ]
        event_text = " ".join(s.strip() for s in extracted_sentences if s.strip())

        return event_text[:200].strip() if event_text else ""  # Limit to 200 chars

    @staticmethod
    def _generate_event_id() -> str:
        """Generate a unique event ID"""
        return f"evt_{uuid.uuid4().hex[:12]}"
