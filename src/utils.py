"""
utils.py
--------
Shared utilities for the Fitness Chatbot:

  1. Text preprocessing — tokenisation + stopword removal + cleaning
  2. Path constants
  3. BMI calculator
  4. Daily protein requirement calculator
  5. Calorie (TDEE) calculator — Harris-Benedict equation
"""

import re
import os

# ─────────────────────────────────────────────────────────────────────────────
# Path constants (relative to project root)
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "data", "fitness_dataset.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VEC_PATH   = os.path.join(MODEL_DIR, "vectorizer.pkl")


# ─────────────────────────────────────────────────────────────────────────────
# Stopword list (built-in — no external NLP library required)
# ─────────────────────────────────────────────────────────────────────────────
STOPWORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for", "of",
    "and", "or", "but", "if", "so", "as", "by", "be", "do", "we", "me",
    "my", "its", "i", "you", "he", "she", "they", "this", "that", "with",
    "was", "are", "were", "has", "have", "had", "not", "no", "can", "will",
    "would", "could", "should", "what", "which", "who", "when", "where",
    "how", "why", "am", "there", "their", "them", "than", "about", "from",
    "up", "out", "into", "your", "our", "any", "all", "been", "more",
    "also", "some", "just", "does", "did", "get", "use", "used", "make",
    "after", "before", "over", "then", "very", "much", "many", "even",
    "need", "want", "know", "like", "good", "well", "per", "each", "may",
}


# ─────────────────────────────────────────────────────────────────────────────
# Text preprocessing
# ─────────────────────────────────────────────────────────────────────────────
def tokenize(text: str) -> list[str]:
    """
    Tokenise *text* into a list of lower-case alphabetic tokens,
    removing punctuation and numbers.
    """
    # Keep only alphabetic characters and spaces
    cleaned = re.sub(r"[^a-z\s]", " ", text.lower())
    return [tok for tok in cleaned.split() if tok]


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Return *tokens* with stopwords removed."""
    return [tok for tok in tokens if tok not in STOPWORDS]


def preprocess(text: str) -> str:
    """
    Full pipeline: lowercase → tokenise → remove stopwords →
    rejoin as a single string for TF-IDF vectorisation.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    tokens  = tokenize(text)
    tokens  = remove_stopwords(tokens)
    return " ".join(tokens)


# ─────────────────────────────────────────────────────────────────────────────
# BMI Calculator
# ─────────────────────────────────────────────────────────────────────────────
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """
    Calculate Body Mass Index.

    Parameters
    ----------
    weight_kg : float — body weight in kilograms
    height_cm : float — height in centimetres

    Returns
    -------
    dict: bmi (float), category (str), advice (str)
    """
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive numbers.")

    height_m = height_cm / 100.0
    bmi      = round(weight_kg / (height_m ** 2), 2)

    if bmi < 18.5:
        category = "Underweight"
        advice   = (
            "You are below a healthy weight range. Focus on a calorie surplus "
            "with nutrient-dense foods and strength training to gain lean mass."
        )
    elif bmi < 25.0:
        category = "Normal weight"
        advice   = (
            "You are in the healthy BMI range. Maintain a balanced diet and "
            "regular exercise to stay here."
        )
    elif bmi < 30.0:
        category = "Overweight"
        advice   = (
            "You are slightly above the healthy range. A moderate calorie "
            "deficit with cardio and strength training can help."
        )
    else:
        category = "Obese"
        advice   = (
            "Your BMI indicates obesity. Consider consulting a healthcare "
            "professional and beginning with a structured diet and low-impact exercise."
        )

    return {"bmi": bmi, "category": category, "advice": advice}


def bmi_cli() -> None:
    """Interactive CLI for the BMI calculator with error handling."""
    print("\n  ─── BMI Calculator ─────────────────────────────────")
    try:
        weight = float(input("    Weight (kg) : "))
        height = float(input("    Height (cm) : "))
        r = calculate_bmi(weight, height)
        print(f"\n    BMI      : {r['bmi']}")
        print(f"    Category : {r['category']}")
        print(f"    Advice   : {r['advice']}")
    except ValueError as e:
        print(f"    ⚠  {e}")
    print("  ────────────────────────────────────────────────────\n")


# ─────────────────────────────────────────────────────────────────────────────
# Protein Requirement Calculator
# ─────────────────────────────────────────────────────────────────────────────
_PROTEIN_FACTORS = {
    "sedentary":          0.8,
    "lightly_active":     1.2,
    "moderately_active":  1.6,
    "very_active":        2.0,
    "athlete":            2.2,
}


def calculate_protein(weight_kg: float, activity_level: str) -> dict:
    """
    Estimate daily protein requirement in grams.

    Parameters
    ----------
    weight_kg      : float — body weight in kilograms
    activity_level : str  — sedentary | lightly_active | moderately_active |
                            very_active | athlete
    Returns
    -------
    dict: protein_g (float), factor (float), activity_level (str)
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be a positive number.")

    level = activity_level.lower().replace(" ", "_")
    if level not in _PROTEIN_FACTORS:
        raise ValueError(
            f"Unknown activity level '{activity_level}'. "
            f"Choose from: {', '.join(_PROTEIN_FACTORS)}"
        )

    factor    = _PROTEIN_FACTORS[level]
    protein_g = round(weight_kg * factor, 1)
    return {"protein_g": protein_g, "factor": factor, "activity_level": level}


def protein_cli() -> None:
    """Interactive CLI for the protein calculator."""
    levels = list(_PROTEIN_FACTORS.keys())
    print("\n  ─── Protein Requirement Calculator ─────────────────")
    print("    Activity levels:")
    for i, lvl in enumerate(levels, 1):
        print(f"      {i}. {lvl.replace('_', ' ').title()}")
    try:
        weight = float(input("\n    Weight (kg) : "))
        idx    = int(input(f"    Activity level (1–{len(levels)}) : ")) - 1
        if not 0 <= idx < len(levels):
            raise ValueError("Choice out of range.")
        level  = levels[idx]
        r      = calculate_protein(weight, level)
        print(
            f"\n    Recommended daily protein : {r['protein_g']} g"
            f"  ({r['factor']} g/kg × {weight} kg)"
        )
    except (ValueError, IndexError) as e:
        print(f"    ⚠  Invalid input — {e}")
    print("  ────────────────────────────────────────────────────\n")


# ─────────────────────────────────────────────────────────────────────────────
# Calorie (TDEE) Calculator — Harris-Benedict Equation
# ─────────────────────────────────────────────────────────────────────────────
_ACTIVITY_MULTIPLIERS = {
    "sedentary":          1.2,
    "lightly_active":     1.375,
    "moderately_active":  1.55,
    "very_active":        1.725,
    "extra_active":       1.9,
}


def calculate_calories(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str = "maintain",
) -> dict:
    """
    Estimate daily calorie requirement using Harris-Benedict.

    Parameters
    ----------
    weight_kg, height_cm, age : standard anthropometrics
    gender         : 'male' or 'female'
    activity_level : sedentary | lightly_active | moderately_active |
                     very_active | extra_active
    goal           : 'maintain' | 'lose' | 'gain'

    Returns
    -------
    dict: bmr, tdee, target_calories, goal
    """
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        raise ValueError("Weight, height, and age must be positive numbers.")

    g = gender.lower()
    if g == "male":
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    elif g == "female":
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'.")

    lvl = activity_level.lower().replace(" ", "_")
    if lvl not in _ACTIVITY_MULTIPLIERS:
        raise ValueError(
            f"Unknown activity level. Choose from: "
            f"{', '.join(_ACTIVITY_MULTIPLIERS)}"
        )

    tdee = round(bmr * _ACTIVITY_MULTIPLIERS[lvl], 0)

    if goal == "lose":
        target = tdee - 500
    elif goal == "gain":
        target = tdee + 300
    else:
        target = tdee

    return {
        "bmr":             round(bmr, 0),
        "tdee":            tdee,
        "target_calories": round(target, 0),
        "goal":            goal,
    }


def calorie_cli() -> None:
    """Interactive CLI for the calorie calculator."""
    levels = list(_ACTIVITY_MULTIPLIERS.keys())
    print("\n  ─── Calorie Requirement Calculator ─────────────────")
    try:
        weight = float(input("    Weight (kg)          : "))
        height = float(input("    Height (cm)          : "))
        age    = int(input("    Age                  : "))
        gender = input("    Gender (male/female) : ").strip()
        print("    Activity levels:")
        for i, lvl in enumerate(levels, 1):
            print(f"      {i}. {lvl.replace('_', ' ').title()}")
        idx    = int(input(f"    Choose (1–{len(levels)})        : ")) - 1
        if not 0 <= idx < len(levels):
            raise ValueError("Choice out of range.")
        level  = levels[idx]
        goal   = input("    Goal (maintain/lose/gain): ").strip().lower()
        r      = calculate_calories(weight, height, age, gender, level, goal)
        print(f"\n    BMR                : {r['bmr']:.0f} kcal/day")
        print(f"    TDEE               : {r['tdee']:.0f} kcal/day")
        print(f"    Target ({goal:8s}) : {r['target_calories']:.0f} kcal/day")
    except (ValueError, IndexError) as e:
        print(f"    ⚠  Invalid input — {e}")
    print("  ────────────────────────────────────────────────────\n")
