"""
embedder.py
Semantic embedder using sentence-transformers.

Model: all-MiniLM-L6-v2
  - ~80MB download, very fast on CPU
  - 384-dim embeddings with strong semantic understanding
  - Understands synonyms: "coding" ≈ "programming", "fixed" ≈ "debugged"

Embeddings are L2-normalised so cosine similarity = dot product.
"""

import warnings, logging
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)


from __future__ import annotations

from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

_DEFAULT_MODEL = "all-MiniLM-L6-v2"


class Embedder:
    """
    Sentence-Transformers semantic embedder.

    Usage
    -----
    embedder = Embedder()
    vectors = embedder.embed(["Hello world", "Another sentence"])
    # vectors.shape == (2, 384)  dtype float32, L2-normalised
    """

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        print(f"[embedder] Loading model '{model_name}' …")
        self.model = SentenceTransformer(model_name)
        print(f"[embedder] Model ready. Embedding dim: {self.model.get_sentence_embedding_dimension()}")

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        """
        Encode texts into L2-normalised semantic vectors.

        Args:
            texts: Non-empty list of strings.

        Returns:
            np.ndarray of shape (len(texts), 384), dtype float32.
        """
        if not texts:
            raise ValueError("texts must be a non-empty sequence.")

        vectors = self.model.encode(
            list(texts),
            normalize_embeddings=True,   # L2-normalise built-in
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return vectors.astype(np.float32)