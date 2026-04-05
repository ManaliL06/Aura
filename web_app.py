"""
web_app.py
----------
Flask web server for the Fitness AI Chatbot.

Serves the chat UI at http://localhost:5000
API endpoints:
  POST /api/chat     — chatbot inference
  POST /api/bmi      — BMI calculator
  POST /api/protein  — protein requirement calculator
  POST /api/calorie  — calorie (TDEE) calculator

Run:
    python web_app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template  # type: ignore[import]
from src.chatbot import chatbot                              # type: ignore[import]
from src.utils import (                                     # type: ignore[import]
    calculate_bmi,
    calculate_protein,
    calculate_calories,
)

app = Flask(__name__)

# Pre-load model at startup
chatbot.load()

# ─────────────────────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html",
                           dataset_size=chatbot.dataset_size,
                           categories=chatbot.categories)


# ─────────────────────────────────────────────────────────────────────────────
# API — Chat
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    data  = request.get_json(force=True)
    query = str(data.get("message", "")).strip()
    if not query:
        return jsonify({"error": "Empty message"}), 400

    result = chatbot.predict(query)
    return jsonify(result)


# ─────────────────────────────────────────────────────────────────────────────
# API — Calculators
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/bmi", methods=["POST"])
def bmi():
    d = request.get_json(force=True)
    try:
        result = calculate_bmi(float(d["weight_kg"]), float(d["height_cm"]))
        return jsonify(result)
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/protein", methods=["POST"])
def protein():
    d = request.get_json(force=True)
    try:
        result = calculate_protein(float(d["weight_kg"]), str(d["activity_level"]))
        return jsonify(result)
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/calorie", methods=["POST"])
def calorie():
    d = request.get_json(force=True)
    try:
        result = calculate_calories(
            float(d["weight_kg"]),
            float(d["height_cm"]),
            int(d["age"]),
            str(d["gender"]),
            str(d["activity_level"]),
            str(d.get("goal", "maintain")),
        )
        return jsonify(result)
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n  FitBot AI — starting on http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
