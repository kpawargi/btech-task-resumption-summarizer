"""
retriever.py
Orchestrates the full retrieval pipeline:

  User query
      │
      ▼
  Embed query
      │
      ▼
  Load all events.json
      │
      ▼
  Extract event texts
      │
      ▼
  Embed event texts
      │
      ▼
  Compute cosine similarity
      │
      ▼
  Rank results
      │
      ▼
  Return top-k events
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from embedder import Embedder
from load_events import load_all_events
from similarity import cosine_similarity_matrix, top_k_indices


class Retriever:
    """
    Semantic event retriever.

    Args:
        outputs_dir : Path to the root outputs/ directory.
        model_name  : HuggingFace model identifier for the Embedder.
    """

    def __init__(self, outputs_dir: str | Path = "outputs") -> None:
        self.outputs_dir = Path(outputs_dir)
        self.embedder = Embedder()

    def retrieve(self, query: str, k: int = 5) -> dict[str, Any]:
        """
        Run the full retrieval pipeline for a single query.

        Args:
            query : Natural language question / search string.
            k     : Maximum number of results to return.

        Returns:
            Dict with keys:
                "query"     : the original query string
                "retrieved" : list of top-k event dicts, each containing
                              task_id, event_id, event_type, created_utc,
                              text, similarity_score
        """
        # ── 1. Load events ────────────────────────────────────────────
        events = load_all_events(self.outputs_dir)
        if not events:
            return {"query": query, "retrieved": [], "warning": "No events found in outputs/"}

        # ── 2. Extract texts & embed independently ────────────────────
        passage_texts = [evt["text"] for evt in events]

        print(f"[retriever] Embedding query …")
        query_vector = self.embedder.embed([query])               # (1, 384)

        print(f"[retriever] Embedding {len(passage_texts)} event(s) …")
        doc_vectors = self.embedder.embed(passage_texts)          # (N, 384)

        # ── 3. Cosine similarity ──────────────────────────────────────
        sim_matrix = cosine_similarity_matrix(query_vector, doc_vectors)  # (1, N)
        scores: np.ndarray = sim_matrix[0]                                # (N,)

        # ── 4. Rank & return top-k ────────────────────────────────────
        indices = top_k_indices(scores, k)

        retrieved = []
        for idx in indices:
            evt = events[idx]
            retrieved.append(
                {
                    "task_id": evt["task_id"],
                    "event_id": evt["event_id"],
                    "event_type": evt["event_type"],
                    "created_utc": evt["created_utc"],
                    "score": round(float(scores[idx]), 4),
                    "text": evt["text"],
                }
            )

        return {"query": query, "retrieved": retrieved}