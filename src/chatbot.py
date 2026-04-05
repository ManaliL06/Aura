"""
chatbot.py
----------
Hybrid inference engine for the Fitness Chatbot.

Architecture (3-layer hybrid system)
-------------------------------------
  Layer 1 -- Rule-based  (triggered by keywords)
      Detected keywords ("bmi", "protein", "calorie") bypass
      the ML layers and invoke the corresponding calculator.

  Layer 2 -- Semantic Search  (primary answer source)
      TF-IDF cosine similarity finds the closest matching question
      in the dataset and returns its pre-written expert answer.

  Layer 3 -- Intent Classification  (metadata)
      Multinomial Naive Bayes classifies the query category and
      provides a confidence score displayed alongside the answer.

Fallback
--------
  If semantic similarity < SIMILARITY_THRESHOLD the chatbot returns:
  "Sorry, I am not trained on that yet."
"""

from __future__ import annotations

import os
import sys
import pickle
from typing import Optional, Any, cast

import numpy as np                               # type: ignore[import]
import pandas as pd                              # type: ignore[import]

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils      import DATA_PATH, MODEL_PATH, VEC_PATH, preprocess   # type: ignore[import]
from src.similarity import build_corpus_matrix, find_best_match           # type: ignore[import]


# ─────────────────────────────────────────────────────────────────────────────
# Thresholds
# ─────────────────────────────────────────────────────────────────────────────
SIMILARITY_THRESHOLD: float = 0.10   # below this → fallback response
CONFIDENCE_THRESHOLD: float = 0.20   # below this → low-confidence flag

FALLBACK_MSG: str = (
    "Sorry, I am not trained on that yet. "
    "Try asking about workouts, diet, fat loss, muscle gain, "
    "supplements, or injury prevention."
)


# ─────────────────────────────────────────────────────────────────────────────
# Rule-based trigger keywords
# ─────────────────────────────────────────────────────────────────────────────
_BMI_KEYWORDS     = {"bmi", "body mass index"}
_PROTEIN_KEYWORDS = {"protein calculator", "how much protein",
                     "daily protein", "protein requirement"}
_CALORIE_KEYWORDS = {"calorie calculator", "how many calories",
                     "tdee", "daily calories", "calorie requirement"}


def _detect_rule(text: str) -> Optional[str]:
    """
    Return 'bmi' | 'protein' | 'calorie' if *text* triggers a
    rule-based calculator, otherwise return None.
    """
    lower = text.lower()
    if any(kw in lower for kw in _BMI_KEYWORDS):
        return "bmi"
    if any(kw in lower for kw in _PROTEIN_KEYWORDS):
        return "protein"
    if any(kw in lower for kw in _CALORIE_KEYWORDS):
        return "calorie"
    return None


# ─────────────────────────────────────────────────────────────────────────────
# FitnessChatbot — hybrid engine
# ─────────────────────────────────────────────────────────────────────────────
class FitnessChatbot:
    """
    Loads trained artifacts once and answers queries via a 3-layer
    hybrid system: rule-based -> semantic search -> intent classification.
    """

    def __init__(self) -> None:
        # Typed as Optional so the static type checker understands
        # these are None until load() is called.
        self.vectorizer:    Optional[Any] = None   # fitted TfidfVectorizer
        self.model:         Optional[Any] = None   # fitted MultinomialNB
        self.df:            Optional[pd.DataFrame] = None
        self.corpus_matrix: Optional[Any] = None   # sparse TF-IDF corpus matrix
        self._loaded:       bool = False

    # ── Initialise ────────────────────────────────────────────────────────
    def load(self) -> None:
        """Load model, vectorizer, and dataset from disk. Called once."""
        if self._loaded:
            return

        for path in (MODEL_PATH, VEC_PATH):
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Required file not found: {path}\n"
                    "Run `python src/train.py` first."
                )

        with open(VEC_PATH, "rb") as f:
            self.vectorizer = pickle.load(f)

        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)

        # Load and preprocess the dataset for similarity search
        df: pd.DataFrame = pd.read_csv(DATA_PATH)
        df.dropna(subset=["question", "answer", "category"], inplace=True)
        df.drop_duplicates(subset=["question"], inplace=True)
        df["clean_question"] = df["question"].apply(preprocess)
        df = df[df["clean_question"].str.strip() != ""].reset_index(drop=True)
        self.df = df

        # Pre-compute corpus TF-IDF matrix for fast similarity search
        self.corpus_matrix = build_corpus_matrix(self.df, self.vectorizer)
        self._loaded = True

    # ── Main predict method ───────────────────────────────────────────────
    def predict(self, user_input: str, debug: bool = False) -> dict:
        """
        Process a user query through the 3-layer hybrid pipeline.

        Parameters
        ----------
        user_input : str  -- raw text from the user
        debug      : bool -- if True, include similarity top-3 in result

        Returns
        -------
        dict:
            answer            (str)         -- response text
            category          (str)         -- predicted category
            intent_category   (str)         -- NB classifier category
            intent_confidence (float)       -- classifier confidence 0-100
            similarity        (float)       -- cosine similarity score * 100
            is_fallback       (bool)        -- True if no confident match
            source            (str)         -- 'rule_based'|'semantic'|'fallback'
            matched_q         (str | None)  -- closest dataset question
            top_matches       (list)        -- top-3 matches (debug only)
        """
        self.load()

        # Pyre2 does not narrow Optional via assert; extract into typed locals instead.
        if (self.vectorizer is None or self.model is None
                or self.df is None or self.corpus_matrix is None):
            raise RuntimeError("Chatbot not loaded. Call load() first.")
        # cast() tells every type checker (including Pyre2) these are non-None Any
        vectorizer    = cast(Any, self.vectorizer)
        model         = cast(Any, self.model)
        df            = cast(Any, self.df)
        corpus_matrix = cast(Any, self.corpus_matrix)

        # ── Guard: empty input ─────────────────────────────────────────────
        cleaned = preprocess(user_input)
        if not cleaned:
            return self._fallback()

        # ── Layer 1: Rule-based detection ──────────────────────────────────
        rule = _detect_rule(user_input)
        if rule:
            return {
                "answer":            self._rule_prompt(rule),
                "category":          "rule_based",
                "intent_category":   "rule_based",
                "intent_confidence": 100.0,
                "similarity":        100.0,
                "is_fallback":       False,
                "source":            "rule_based",
                "matched_q":         None,
                "top_matches":       [],
            }

        # ── Layer 2: Semantic similarity search (primary answer) ───────────
        sim_result = find_best_match(
            user_input,
            df,
            vectorizer,
            corpus_matrix,
            top_n=3,
        )
        best_sim: float = float(sim_result["similarity"])

        # ── Layer 3: Intent classification (metadata) ──────────────────────
        query_vec    = vectorizer.transform([cleaned])
        proba        = model.predict_proba(query_vec)[0]
        top_idx: int = int(np.argmax(proba))
        raw_conf     = float(proba[top_idx]) * 100.0
        intent_conf: float = float(int(raw_conf * 10) / 10)  # avoids round() overload
        intent_cat: str    = str(model.classes_[top_idx])

        # ── Routing decision ───────────────────────────────────────────────
        # If similarity is too low, fall back with a helpful message.
        if best_sim < SIMILARITY_THRESHOLD:
            return self._fallback(
                extra={
                    "similarity":        float(int(best_sim * 1000) / 10),
                    "intent_confidence": intent_conf,
                    "intent_category":   intent_cat,
                }
            )

        return {
            "answer":            sim_result["answer"],
            "category":          sim_result["category"],
            "intent_category":   intent_cat,
            "intent_confidence": intent_conf,
            "similarity":        float(int(best_sim * 1000) / 10),
            "is_fallback":       False,
            "source":            "semantic",
            "matched_q":         sim_result["question"],
            "top_matches":       sim_result["top_matches"] if debug else [],
        }

    # ── Helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _fallback(extra: Optional[dict] = None) -> dict:
        """Build a standardised fallback response dict."""
        base: dict = {
            "answer":            FALLBACK_MSG,
            "category":          "unknown",
            "intent_category":   "unknown",
            "intent_confidence": 0.0,
            "similarity":        0.0,
            "is_fallback":       True,
            "source":            "fallback",
            "matched_q":         None,
            "top_matches":       [],
        }
        if extra:
            base.update(extra)
        return base

    @staticmethod
    def _rule_prompt(rule: str) -> str:
        prompts = {
            "bmi":     "Sure! I'll launch the BMI calculator for you.",
            "protein": "Sure! I'll launch the protein requirement calculator for you.",
            "calorie": "Sure! I'll launch the calorie requirement calculator for you.",
        }
        return prompts.get(rule, "Let me calculate that for you.")

    @property
    def categories(self) -> list:
        """Return list of known categories from the trained model."""
        self.load()
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        model = cast(Any, self.model)
        return list(model.classes_)

    @property
    def dataset_size(self) -> int:
        """Number of Q&A pairs in the loaded dataset."""
        self.load()
        if self.df is None:
            raise RuntimeError("Dataset not loaded.")
        df = cast(Any, self.df)
        return int(len(df))


# Singleton — shared across the application
chatbot = FitnessChatbot()
