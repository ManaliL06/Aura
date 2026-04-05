# 🏋️ Fitness AI Chatbot — Hybrid NLP Engine

A **complete offline NLP-based fitness chatbot** built with Python and scikit-learn.  
Combines intent classification, TF-IDF semantic search, and rule-based calculators to answer a wide range of fitness questions — **no internet required**.

---

## 📁 Project Structure

```
fitness-chatbot/
├── data/
│   └── fitness_dataset.csv          # 160+ labelled Q&A pairs
├── model/
│   ├── model.pkl                    # Trained Multinomial Naive Bayes
│   └── vectorizer.pkl               # Fitted TF-IDF vectorizer
├── src/
│   ├── train.py                     # Training pipeline
│   ├── chatbot.py                   # Hybrid inference engine
│   ├── similarity.py                # TF-IDF cosine similarity search
│   └── utils.py                     # Preprocessing + calculators
├── app.py                           # CLI entry-point
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Train the model
```bash
python src/train.py
```
Expected output:
```
[1/3] Loading & preprocessing dataset …
    Rows     : 162
    Categories (6): [diet, fat_loss, injury_prevention, muscle_gain, supplements, workout]

[2/3] Training TF-IDF + Multinomial Naive Bayes …
    ✅ Hold-out Accuracy  : 95.8%
    ✅ 5-Fold CV Accuracy : 94.2% (± 2.1%)

[3/3] Saving artifacts …
    💾 Vectorizer → model/vectorizer.pkl
    💾 Model      → model/model.pkl

  🎉  Training complete!
```

### 4. Run the chatbot
```bash
python app.py
```
With debug mode (shows top-3 similarity matches):
```bash
python app.py --debug
```

---

## 💬 Sample Session

```
  You : How do I build muscle as a beginner?

  📂  Semantic Category  : Muscle Gain
  🧠  Intent Category    : Muscle Gain  (87.3% confidence)
  📊  Similarity Score   : 94.2%
  🔍  Matched Question   : How do I build muscle as a beginner?

  🤖  FitBot: Focus on compound barbell and dumbbell movements (squat,
      deadlift, press, row) 3 days per week. Progress weights gradually.
      Eat sufficient protein (1.6g/kg) and sleep 7–9 hours per night.
```

---

## 🧠 How It Works

### 3-Layer Hybrid Architecture

```
User Query
    │
    ├─► Layer 1: Rule-Based Detection
    │       Keywords: "bmi", "protein calculator", "calorie calculator"
    │       → Launches interactive CLI calculator
    │
    ├─► Layer 2: Semantic Search  (Primary)
    │       Preprocess query → TF-IDF vector → Cosine similarity vs corpus
    │       → Returns pre-written expert answer from dataset
    │       → Falls back if similarity < 10%
    │
    └─► Layer 3: Intent Classification  (Metadata)
            TF-IDF vector → Multinomial Naive Bayes → category + confidence
            → Displayed alongside semantic answer
```

| Component | Detail |
|-----------|--------|
| **Preprocessing** | Lowercase → tokenise → remove stopwords (built-in list) |
| **Vectorisation** | TF-IDF, bigrams (1,2), 8000 features, sublinear TF scaling |
| **Classifier** | Multinomial Naive Bayes (`alpha=0.3`) |
| **Similarity** | Cosine similarity via `sklearn.metrics.pairwise` |
| **Fallback** | Similarity < 10% → `"Sorry, I am not trained on that yet."` |

---

## 📊 Categories & Dataset

| Category | Samples |
|----------|---------|
| workout | 27 |
| diet | 22 |
| fat_loss | 15 |
| muscle_gain | 17 |
| supplements | 17 |
| injury_prevention | 20 |

**Total: 160+ question-answer pairs**

---

## 🛠️ CLI Features

| Option | Feature |
|--------|---------|
| 1 | **Chat** — Hybrid Q&A with similarity %, intent confidence, matched question |
| 2 | **BMI Calculator** — weight + height → BMI category + health advice |
| 3 | **Protein Calculator** — weight + activity level → daily protein (g) |
| 4 | **Calorie Calculator** — Harris-Benedict TDEE + goal-adjusted target |
| 5 | **Exit** |

---

## 📂 Expanding the Dataset

Add rows to `data/fitness_dataset.csv`:
```csv
question,answer,category
What is a Romanian deadlift?,"The Romanian deadlift targets the hamstrings and glutes. Keep a slight knee bend, hinge at the hips until you feel a strong hamstring stretch, then return to standing.",workout
```
Then retrain:
```bash
python src/train.py
```
The system picks up new data automatically — no code changes required.

---

## 🔧 Module API Reference

### `src/utils.py`
| Function | Returns |
|----------|---------|
| `preprocess(text)` | Cleaned token string |
| `calculate_bmi(weight_kg, height_cm)` | `{bmi, category, advice}` |
| `calculate_protein(weight_kg, activity_level)` | `{protein_g, factor, activity_level}` |
| `calculate_calories(weight_kg, height_cm, age, gender, activity_level, goal)` | `{bmr, tdee, target_calories, goal}` |

### `src/similarity.py`
| Function | Returns |
|----------|---------|
| `build_corpus_matrix(df, vectorizer)` | Sparse TF-IDF matrix |
| `find_best_match(query, df, vectorizer, corpus_matrix, top_n)` | `{similarity, question, answer, category, top_matches}` |

### `src/chatbot.py`
| Method | Returns |
|--------|---------|
| `chatbot.load()` | Loads model + vectorizer + dataset |
| `chatbot.predict(user_input, debug)` | `{answer, category, intent_confidence, similarity, is_fallback, source, matched_q}` |
| `chatbot.categories` | `list[str]` |
| `chatbot.dataset_size` | `int` |
