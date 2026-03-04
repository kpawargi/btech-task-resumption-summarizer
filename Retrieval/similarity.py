"""
similarity.py
Pure-numpy cosine similarity utilities.

Both query and document vectors are assumed to already be L2-normalised
(as produced by Embedder.embed), so cosine similarity reduces to a
simple dot-product matrix multiplication.
"""

from __future__ import annotations

import numpy as np


def cosine_similarity_matrix(
    query_vectors: np.ndarray,
    doc_vectors: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between every query and every document.

    Args:
        query_vectors : (Q, H) float32, L2-normalised
        doc_vectors   : (D, H) float32, L2-normalised

    Returns:
        (Q, D) float32 similarity matrix, values in [-1, 1].
    """
    if query_vectors.ndim != 2 or doc_vectors.ndim != 2:
        raise ValueError("Both inputs must be 2-D arrays of shape (N, hidden_dim).")
    if query_vectors.shape[1] != doc_vectors.shape[1]:
        raise ValueError(
            f"Dimension mismatch: query dim={query_vectors.shape[1]}, "
            f"doc dim={doc_vectors.shape[1]}"
        )

    # For L2-normalised vectors: cos(u, v) = u · v
    return np.dot(query_vectors, doc_vectors.T).astype(np.float32)


def top_k_indices(similarity_row: np.ndarray, k: int) -> np.ndarray:
    """
    Return the indices of the top-k highest similarity scores (descending).

    Args:
        similarity_row : 1-D array of similarity scores (one query vs all docs).
        k              : Number of top results to return.

    Returns:
        1-D int array of length min(k, len(similarity_row)).
    """
    k = min(k, len(similarity_row))
    # argpartition is O(N) but we need sorted order, so sort the partition
    partition = np.argpartition(similarity_row, -k)[-k:]
    sorted_partition = partition[np.argsort(similarity_row[partition])[::-1]]
    return sorted_partition