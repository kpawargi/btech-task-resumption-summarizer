"""Event importance scoring based on recency and salience"""

from typing import List, Dict, Optional
import math
from src.schemas import EventRecord


class EventScorer:
    """Score events by importance (recency + salience)"""

    # Keyword weights for salience
    DEFAULT_KEYWORD_WEIGHTS = {
        "critical": 2.0,
        "urgent": 1.8,
        "important": 1.5,
        "error": 1.6,
        "bug": 1.7,
        "fail": 1.5,
        "issue": 1.4,
        "decision": 1.3,
        "action": 1.2,
    }

    # Type weights (rare/important types score higher)
    TYPE_WEIGHTS = {
        "DECISION": 1.5,
        "ISSUE": 1.4,
        "ACTION": 1.2,
        "TODO": 1.3,
        "NOTE": 1.0,
    }

    def score_events(
        self,
        events: List[EventRecord],
        recency_decay: float = 0.95,
        keyword_weights: Optional[Dict[str, float]] = None,
    ) -> List[EventRecord]:
        """
        Score events by importance.

        Args:
            events: List of EventRecord objects (in chronological order)
            recency_decay: Decay factor per event (newer = higher score)
            keyword_weights: Custom keyword weights (merged with defaults)

        Returns:
            Same list with scores populated (0.0 - 1.0 range)
        """
        if not events:
            return events

        # Merge keyword weights
        kw_weights = {**self.DEFAULT_KEYWORD_WEIGHTS}
        if keyword_weights:
            kw_weights.update(keyword_weights)

        # Calculate scores
        for idx, event in enumerate(events):
            recency_score = self._calculate_recency_score(
                idx, len(events), recency_decay
            )
            salience_score = self._calculate_salience_score(event, kw_weights)
            type_weight = self.TYPE_WEIGHTS.get(event.event_type, 1.0)

            # Combine: type_weight * (recency + salience)
            combined = type_weight * (recency_score * 0.5 + salience_score * 0.5)
            event.score = min(1.0, max(0.0, combined))  # Clamp to [0, 1]

        return events

    def _calculate_recency_score(
        self, event_index: int, total_events: int, decay: float
    ) -> float:
        """
        Calculate recency score (later events score higher).
        Range: [decay, 1.0]
        """
        if total_events == 1:
            return 1.0
        # Earlier events get decayed, later events get higher scores
        position_ratio = event_index / (total_events - 1)
        recency = decay + (1 - decay) * position_ratio
        return recency

    def _calculate_salience_score(
        self, event: EventRecord, keyword_weights: Dict[str, float]
    ) -> float:
        """
        Calculate salience score based on:
        - Keyword frequency
        - Entity count
        - Text length (longer = more detailed = higher)
        """
        text_lower = event.text.lower()
        score = 0.5  # Base score

        # Keyword matching
        keyword_hits = 0
        for keyword, weight in keyword_weights.items():
            if keyword.lower() in text_lower:
                keyword_hits += weight
        keyword_score = min(1.0, keyword_hits / 5.0)  # Normalize
        score += keyword_score * 0.3

        # Entity count (if present)
        if event.entities and len(event.entities) > 0:
            entity_score = min(1.0, len(event.entities) / 3.0)  # 3+ entities = max
            score += entity_score * 0.2

        # Text length (longer = more informative)
        text_length = len(event.text.split())
        length_score = min(1.0, text_length / 20.0)  # 20+ words = max
        score += length_score * 0.2

        return min(1.0, score)

    def sort_by_importance(self, events: List[EventRecord]) -> List[EventRecord]:
        """Sort events by score (descending) and return"""
        return sorted(events, key=lambda e: e.score or 0.0, reverse=True)
