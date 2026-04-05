"""
train.py
--------
Training pipeline for the Fitness Chatbot.

Pipeline:
  1. Load & validate fitness_dataset.csv
  2. Text preprocessing (tokenisation + stopword removal)
  3. TF-IDF vectorisation
  4. Train Multinomial Naive Bayes classifier
  5. Evaluate accuracy and print classification report
  6. Persist model.pkl and vectorizer.pkl

Usage:
    python src/train.py
"""

from __future__ import annotations

import os
import sys
import pickle

import pandas as pd                                                          # type: ignore[import]
from sklearn.feature_extraction.text import TfidfVectorizer                  # type: ignore[import]
from sklearn.naive_bayes import MultinomialNB                                 # type: ignore[import]
from sklearn.model_selection import train_test_split, cross_val_score        # type: ignore[import]
from sklearn.metrics import accuracy_score, classification_report            # type: ignore[import]

# Allow running from project root or from src/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import DATA_PATH, MODEL_DIR, MODEL_PATH, VEC_PATH, preprocess  # type: ignore[import]


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Load data
# ─────────────────────────────────────────────────────────────────────────────
def load_data(path: str) -> pd.DataFrame:
    """Load the CSV dataset and apply NLP preprocessing."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    required = {"question", "answer", "category"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}. Found: {set(df.columns)}")

    df.dropna(subset=list(required), inplace=True)
    df.drop_duplicates(subset=["question"], inplace=True)

    # Apply full NLP preprocessing pipeline
    df["clean_question"] = df["question"].apply(preprocess)

    # Drop rows that became empty after preprocessing
    df = df[df["clean_question"].str.strip() != ""].reset_index(drop=True)

    categories = sorted(df["category"].unique())
    print(f"    Rows     : {len(df)}")
    print(f"    Categories ({len(categories)}): {categories}")
    print()
    for cat in categories:
        # Using len() + list-comp avoids Pyre2 mistyping Series.__eq__ as bool
        count: int = len([v for v in df["category"].tolist() if v == cat])
        print(f"      {cat:<20s}: {count} samples")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Train
# ─────────────────────────────────────────────────────────────────────────────
def train(df: pd.DataFrame):
    """
    Fit TF-IDF vectoriser and Multinomial Naive Bayes classifier.

    Returns
    -------
    vectorizer : fitted TfidfVectorizer
    model      : fitted MultinomialNB
    """
    X = df["clean_question"].tolist()
    y = df["category"].tolist()

    # Stratified split (20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=list(y),
    )
    print(f"    Train samples : {len(X_train)}")
    print(f"    Test  samples : {len(X_test)}")

    # ── TF-IDF vectorisation ──────────────────────────────────────────────
    # NOTE: stop_words='english' in TfidfVectorizer is an additional safeguard
    # on top of our custom preprocessing stopword removal passed as input.
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),     # unigrams + bigrams
        max_features=8000,
        sublinear_tf=True,      # log(1 + tf) — improves results on short texts
        min_df=1,               # include features that appear even once (small dataset)
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    # ── Multinomial Naive Bayes ───────────────────────────────────────────
    model = MultinomialNB(alpha=0.3)   # lower smoothing for tighter vocabulary
    model.fit(X_train_vec, y_train)

    # ── Evaluation ────────────────────────────────────────────────────────
    y_pred   = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n    [OK] Hold-out Accuracy  : {accuracy * 100:.1f}%")

    # Cross-validation for a more robust estimate
    all_vec = vectorizer.transform(X)
    cv_scores = cross_val_score(model, all_vec, y, cv=5, scoring="accuracy")
    print(f"    [OK] 5-Fold CV Accuracy : {cv_scores.mean() * 100:.1f}% "
          f"(+/- {cv_scores.std() * 100:.1f}%)")

    print("\n    Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    return vectorizer, model


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Save artifacts
# ─────────────────────────────────────────────────────────────────────────────
def save_artifacts(vectorizer, model) -> None:
    """Persist the fitted vectorizer and model to disk with pickle."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    with open(VEC_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"    [SAVED] Vectorizer -> {VEC_PATH}")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"    [SAVED] Model      -> {MODEL_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SEP = "=" * 58

    print(SEP)
    print("  Fitness Chatbot — Model Training Pipeline")
    print(SEP)

    print("\n[1/3] Loading & preprocessing dataset …")
    df = load_data(DATA_PATH)

    print("\n[2/3] Training TF-IDF + Multinomial Naive Bayes …")
    vectorizer, model = train(df)

    print("\n[3/3] Saving artifacts …")
    save_artifacts(vectorizer, model)

    print(f"\n{SEP}")
    print("  Training complete!  Run `python app.py` to chat.")
    print(SEP + "\n")
