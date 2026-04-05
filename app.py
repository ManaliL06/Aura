"""
app.py
------
CLI entry-point for the Fitness AI Chatbot.

Hybrid system:
  • Intent classification (Multinomial Naive Bayes)
  • Semantic answer retrieval (TF-IDF cosine similarity)
  • Rule-based calculators (BMI, protein, calorie)

Usage:
    python app.py
    python app.py --debug      # show similarity top-3 for each query
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import chatbot          # type: ignore[import]
from src.utils   import bmi_cli, protein_cli, calorie_cli  # type: ignore[import]


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║         🏋️   FITNESS AI CHATBOT  — Hybrid NLP Engine     ║
║   Offline • Intent Classification • Semantic Search      ║
╚══════════════════════════════════════════════════════════╝
  Topics: workout · diet · fat loss · muscle gain
          supplements · injury prevention
"""

MENU = """
  ┌─────────────────────────────────────────────┐
  │  MAIN MENU                                  │
  │  1. 💬  Chat with FitBot                    │
  │  2. ⚖️   BMI Calculator                     │
  │  3. 🥩  Protein Requirement Calculator      │
  │  4. 🔥  Calorie Requirement Calculator      │
  │  5. 🚪  Exit                                │
  └─────────────────────────────────────────────┘"""

EXIT_WORDS = {"exit", "quit", "back", "menu", "q", ":q"}


# ─────────────────────────────────────────────────────────────────────────────
# Chat session
# ─────────────────────────────────────────────────────────────────────────────
def chat_session(debug: bool = False) -> None:
    """
    Run an interactive chat loop.

    Parameters
    ----------
    debug : bool — if True, prints top-3 similarity matches per query.
    """
    print("\n  💬  Chat started — type 'back' to return to the menu.\n")
    print("  " + "─" * 54)

    while True:
        # ── Read user input ────────────────────────────────────────────────
        try:
            raw = input("  You : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Returning to main menu …\n")
            return

        if not raw:
            print("  ⚠   Please enter a message.\n")
            continue

        if raw.lower() in EXIT_WORDS:
            print("  Returning to main menu …\n")
            return

        # ── Get response ───────────────────────────────────────────────────
        try:
            result = chatbot.predict(raw, debug=debug)
        except FileNotFoundError as e:
            print(f"\n  ❌  {e}\n")
            return
        except Exception as e:
            print(f"\n  ❌  Unexpected error: {e}\n")
            continue

        # ── Handle rule-based routing ──────────────────────────────────────
        if result["source"] == "rule_based":
            print(f"\n  🤖  FitBot: {result['answer']}")
            _run_calculator(raw)
            print("  " + "─" * 54)
            continue

        # ── Display fallback ───────────────────────────────────────────────
        if result["is_fallback"]:
            print(f"\n  🤖  FitBot: {result['answer']}")
            print(f"     [Similarity: {result['similarity']:.1f}% — too low to answer confidently]")
            print("  " + "─" * 54)
            continue

        # ── Display normal response ────────────────────────────────────────
        cat       = result["category"].replace("_", " ").title()
        sim       = result["similarity"]       # already ×100
        i_cat     = result.get("intent_category", cat).replace("_", " ").title()
        i_conf    = result.get("intent_confidence", 0.0)
        matched_q = result.get("matched_q", "")

        print()
        print(f"  📂  Semantic Category  : {cat}")
        print(f"  🧠  Intent Category    : {i_cat}  ({i_conf:.1f}% confidence)")
        print(f"  📊  Similarity Score   : {sim:.1f}%")
        if matched_q:
            print(f"  🔍  Matched Question   : {matched_q[:70]}")

        print(f"\n  🤖  FitBot: {result['answer']}")

        # Optional debug: top-3 similarity matches
        if debug and result.get("top_matches"):
            print("\n  ── Debug: Top-3 Similarity Matches ──────────────")
            for m in result["top_matches"]:
                score = m["similarity"] * 100
                print(f"    #{m['rank']}  {score:5.1f}%  [{m['category']}]  {m['question'][:60]}")

        print("\n  " + "─" * 54)


def _run_calculator(raw: str) -> None:
    """Dispatch to the appropriate CLI calculator based on the query."""
    lower = raw.lower()
    if "bmi" in lower or "body mass" in lower:
        bmi_cli()
    elif "protein" in lower:
        protein_cli()
    elif "calorie" in lower or "tdee" in lower:
        calorie_cli()


# ─────────────────────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────────────────────
def main(debug: bool = False) -> None:
    """Entry-point — show banner, pre-load model, run menu loop."""
    print(BANNER)

    # Pre-load model (validates files, builds corpus matrix)
    try:
        chatbot.load()
        print(f"  ✅  Model loaded  |  Dataset: {chatbot.dataset_size} Q&A pairs"
              f"  |  Categories: {len(chatbot.categories)}")
        print(f"  📚  {', '.join(chatbot.categories)}\n")
    except FileNotFoundError as e:
        print(f"  ❌  {e}")
        sys.exit(1)

    # Main menu loop
    while True:
        print(MENU)
        try:
            choice = input("  Choose an option (1–5) : ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye! Stay fit! 💪\n")
            sys.exit(0)

        if choice == "1":
            chat_session(debug=debug)
        elif choice == "2":
            bmi_cli()
        elif choice == "3":
            protein_cli()
        elif choice == "4":
            calorie_cli()
        elif choice == "5":
            print("\n  Goodbye! Stay fit! 💪\n")
            sys.exit(0)
        else:
            print("  ⚠   Invalid choice. Enter a number from 1 to 5.\n")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fitness AI Chatbot CLI")
    parser.add_argument(
        "--debug", action="store_true",
        help="Show top-3 similarity matches for each query"
    )
    args = parser.parse_args()
    main(debug=args.debug)
