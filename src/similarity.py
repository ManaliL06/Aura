"""
similarity.py
-------------
Semantic similarity search using TF-IDF cosine similarity.

Given a user query and the full dataset, this module finds the most
semantically similar question and returns its pre-written answer.
This is the primary answer-retrieval mechanism of the hybrid chatbot.

Key function
------------
    find_best_match(query, df, vectorizer) -> dict
"""

from __future__ import annotations

from typing import Optional

import numpy as np                                                      # type: ignore[import]
import pandas as pd                                                     # type: ignore[import]
from sklearn.metrics.pairwise import cosine_similarity                  # type: ignore[import]
from sklearn.feature_extraction.text import TfidfVectorizer             # type: ignore[import]

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import preprocess                                        # type: ignore[import]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def build_corpus_matrix(df: pd.DataFrame, vectorizer: TfidfVectorizer):
    """
    Pre-compute the TF-IDF matrix for every question in the dataset.

    Parameters
    ----------
    df         : pd.DataFrame with a 'clean_question' column
    vectorizer : already-fitted TfidfVectorizer (from training)

    Returns
    -------
    corpus_matrix : scipy sparse matrix  (n_samples × n_features)
    """
    return vectorizer.transform(df["clean_question"].values)


def find_best_match(
    query: str,
    df: pd.DataFrame,
    vectorizer: TfidfVectorizer,
    corpus_matrix,
    top_n: int = 1,
) -> dict:
    """
    Find the dataset question(s) most semantically similar to *query*
    using cosine similarity on TF-IDF vectors.

    Parameters
    ----------
    query         : str   — raw user input
    df            : pd.DataFrame — full dataset (question, answer, category, clean_question)
    vectorizer    : fitted TfidfVectorizer
    corpus_matrix : pre-computed TF-IDF matrix of the corpus
    top_n         : int   — number of top matches to return (default 1)

    Returns
    -------
    dict with keys:
        similarity   (float)        — cosine similarity of the best match [0, 1]
        question     (str)          — matched dataset question
        answer       (str)          — matched answer
        category     (str)          — matched category
        top_matches  (list[dict])   — top_n matches with their scores
    """
    cleaned  = preprocess(query)

    if not cleaned:
        return _empty_result()

    # Vectorise the query using the SAME fitted vectorizer
    query_vec = vectorizer.transform([cleaned])

    # Compute cosine similarity against every row in the corpus
    sims = cosine_similarity(query_vec, corpus_matrix).flatten()

    if sims.max() == 0.0:
        return _empty_result()

    # Build sorted top-N result list
    top_indices = np.argsort(sims)[::-1][:top_n]
    top_matches = [
        {
            "rank":       int(rank + 1),
            "similarity": float(int(float(sims[idx]) * 10000) / 10000),  # avoids round() overload
            "question":   df.iloc[idx]["question"],
            "answer":     df.iloc[idx]["answer"],
            "category":   df.iloc[idx]["category"],
        }
        for rank, idx in enumerate(top_indices)
    ]

    best = top_matches[0]
    return {
        "similarity":  best["similarity"],
        "question":    best["question"],
        "answer":      best["answer"],
        "category":    best["category"],
        "top_matches": top_matches,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _empty_result() -> dict:
    """Return a zero-similarity result when no match can be found."""
    return {
        "similarity":  0.0,
        "question":    None,
        "answer":      None,
        "category":    None,
        "top_matches": [],
    }


def similarity_report(results: dict) -> str:
    """Format the top similarity matches as a readable string for debugging."""
    lines = ["  Similarity Report:"]
    for m in results.get("top_matches", []):
        lines.append(
            f"  #{m['rank']}  [{m['similarity']:.3f}]  "
            f"[{m['category']}]  {m['question'][:70]}"
        )
    return "\n".join(lines) if len(lines) > 1 else "  No matches found."
