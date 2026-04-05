"""
streamlit_app.py
----------------
Premium Streamlit web UI for the Fitness AI Chatbot.

Run with:
    streamlit run streamlit_app.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st  # type: ignore[import]
from src.chatbot import chatbot  # type: ignore[import]
from src.utils import calculate_bmi, calculate_protein, calculate_calories  # type: ignore[import]

# ─────────────────────────────────────────────────────────────────────────────
# Page config — must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FitBot AI — Fitness Chatbot",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — premium dark fitness theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit default branding */
#MainMenu, footer, header { visibility: hidden; }

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0d0f1a 0%, #111827 50%, #0d1117 100%);
    min-height: 100vh;
}

/* ── HEADER ── */
.fitbot-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f2044 50%, #1a1040 100%);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.fitbot-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #a78bfa, #f687b3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.fitbot-subtitle {
    color: #94a3b8;
    font-size: 0.9rem;
    margin: 4px 0 0 0;
}

/* ── CHAT MESSAGES ── */
.user-msg {
    background: linear-gradient(135deg, #1e40af, #1e3a8a);
    color: #e2e8f0;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0 8px 20%;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
    font-size: 0.95rem;
    line-height: 1.5;
    border: 1px solid rgba(99, 149, 237, 0.2);
}
.bot-msg {
    background: linear-gradient(135deg, #1a1f2e, #1e2435);
    color: #e2e8f0;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 20% 8px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    font-size: 0.95rem;
    line-height: 1.6;
    border: 1px solid rgba(255,255,255,0.06);
}
.bot-fallback {
    background: linear-gradient(135deg, #2d1b33, #1f1030);
    border: 1px solid rgba(167, 139, 250, 0.25);
    color: #c4b5fd;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 20% 8px 0;
    font-size: 0.9rem;
}
.msg-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
    opacity: 0.7;
}

/* ── METADATA BADGES ── */
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.badge-cat  { background: rgba(99,179,237,0.15); color: #63b3ed; border: 1px solid rgba(99,179,237,0.3); }
.badge-sim  { background: rgba(72,187,120,0.15); color: #68d391; border: 1px solid rgba(72,187,120,0.3); }
.badge-conf { background: rgba(246,173,85,0.15); color: #f6ad55; border: 1px solid rgba(246,173,85,0.3); }
.badge-src  { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }

.matched-q {
    margin-top: 8px;
    font-size: 0.75rem;
    color: #64748b;
    font-style: italic;
}

/* ── CHAT CONTAINER ── */
.chat-container {
    background: rgba(15, 20, 35, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    min-height: 400px;
    max-height: 560px;
    overflow-y: auto;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
}

/* ── INPUT ── */
.stTextInput > div > div > input {
    background: rgba(20, 28, 50, 0.9) !important;
    border: 1.5px solid rgba(99, 149, 237, 0.3) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(99, 149, 237, 0.7) !important;
    box-shadow: 0 0 0 3px rgba(99,149,237,0.1) !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(37,99,235,0.4) !important;
}

/* ── SIDEBAR ── */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1523 0%, #111827 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── SIDEBAR SECTION ── */
.sidebar-section {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}
.sidebar-section h4 {
    color: #94a3b8;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 12px 0;
    font-weight: 600;
}

/* ── RESULT CARD ── */
.result-card {
    background: linear-gradient(135deg, #0f1f3d, #111827);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 12px;
    padding: 16px;
    margin-top: 12px;
}
.result-card .metric-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 2px;
}
.result-card .metric-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #63b3ed;
}
.result-card .metric-sub {
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: 2px;
}

/* ── CHIP TOPICS ── */
.topic-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.topic-chip {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.72rem;
    color: #94a3b8;
}

/* Streamlit number/text inputs in sidebar */
.stNumberInput input, .stSelectbox select {
    background: rgba(20,28,50,0.9) !important;
    color: #e2e8f0 !important;
    border-color: rgba(99,149,237,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Load model once
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    chatbot.load()
    return chatbot

bot = load_model()

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "calc_result" not in st.session_state:
    st.session_state.calc_result = None

# ─────────────────────────────────────────────────────────────────────────────
# Category colours
# ─────────────────────────────────────────────────────────────────────────────
CAT_COLOURS = {
    "workout":           "#63b3ed",
    "diet":              "#68d391",
    "fat_loss":          "#f6ad55",
    "muscle_gain":       "#fc8181",
    "supplements":       "#b794f4",
    "injury_prevention": "#76e4f7",
    "rule_based":        "#f687b3",
    "unknown":           "#718096",
}

def cat_colour(c):
    return CAT_COLOURS.get(c, "#718096")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Calculators + Model info
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 20px'>
        <div style='font-size:2.4rem'>🏋️</div>
        <div style='font-size:1.1rem; font-weight:700; color:#e2e8f0'>FitBot AI</div>
        <div style='font-size:0.75rem; color:#64748b; margin-top:2px'>Offline · NLP · ML Powered</div>
    </div>""", unsafe_allow_html=True)

    # Model stats
    st.markdown(f"""
    <div class='sidebar-section'>
        <h4>Model Info</h4>
        <div style='display:flex; flex-direction:column; gap:6px'>
            <div style='display:flex; justify-content:space-between; font-size:0.82rem'>
                <span style='color:#64748b'>Dataset</span>
                <span style='color:#63b3ed; font-weight:600'>{bot.dataset_size} Q&A pairs</span>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:0.82rem'>
                <span style='color:#64748b'>Categories</span>
                <span style='color:#63b3ed; font-weight:600'>{len(bot.categories)}</span>
            </div>
            <div style='display:flex; justify-content:space-between; font-size:0.82rem'>
                <span style='color:#64748b'>Mode</span>
                <span style='color:#68d391; font-weight:600'>Offline ✓</span>
            </div>
        </div>
        <div class='topic-chips' style='margin-top:10px'>
            {''.join(f"<span class='topic-chip'>{c.replace('_',' ')}</span>" for c in bot.categories)}
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Calculator selector ──
    calc = st.selectbox(
        "🧮 Calculators",
        ["— Select —", "⚖️  BMI Calculator", "🥩  Protein Calculator", "🔥  Calorie Calculator"],
        key="calc_select"
    )

    if calc == "⚖️  BMI Calculator":
        with st.form("bmi_form"):
            st.markdown("<div class='sidebar-section'><h4>BMI Calculator</h4>", unsafe_allow_html=True)
            w = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
            h = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
            submitted = st.form_submit_button("Calculate BMI")
            st.markdown("</div>", unsafe_allow_html=True)
        if submitted:
            r = calculate_bmi(w, h)
            col1, col2 = st.columns(2)
            col1.metric("BMI", f"{r['bmi']:.1f}")
            col2.metric("Category", r["category"])
            st.info(r["advice"])

    elif calc == "🥩  Protein Calculator":
        levels = ["sedentary", "lightly_active", "moderately_active", "very_active", "athlete"]
        level_labels = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Athlete"]
        with st.form("prot_form"):
            st.markdown("<div class='sidebar-section'><h4>Protein Calculator</h4>", unsafe_allow_html=True)
            w  = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
            lv = st.selectbox("Activity Level", level_labels)
            submitted = st.form_submit_button("Calculate Protein")
            st.markdown("</div>", unsafe_allow_html=True)
        if submitted:
            level = levels[level_labels.index(lv)]
            r = calculate_protein(w, level)
            st.metric("Daily Protein", f"{r['protein_g']} g")
            st.caption(f"Factor: {r['factor']} g/kg × {w} kg")

    elif calc == "🔥  Calorie Calculator":
        act_levels = ["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"]
        act_labels  = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]
        with st.form("cal_form"):
            st.markdown("<div class='sidebar-section'><h4>Calorie Calculator</h4>", unsafe_allow_html=True)
            w   = st.number_input("Weight (kg)", 20.0, 300.0, 70.0, 0.5)
            h   = st.number_input("Height (cm)", 100.0, 250.0, 170.0, 0.5)
            age = st.number_input("Age", 10, 100, 25, 1)
            gen = st.radio("Gender", ["Male", "Female"], horizontal=True)
            lv  = st.selectbox("Activity Level", act_labels)
            goal = st.radio("Goal", ["maintain", "lose", "gain"], horizontal=True)
            submitted = st.form_submit_button("Calculate Calories")
            st.markdown("</div>", unsafe_allow_html=True)
        if submitted:
            level = act_levels[act_labels.index(lv)]
            r = calculate_calories(w, h, int(age), gen.lower(), level, goal)
            c1, c2, c3 = st.columns(3)
            c1.metric("BMR",    f"{r['bmr']:.0f} kcal")
            c2.metric("TDEE",   f"{r['tdee']:.0f} kcal")
            c3.metric("Target", f"{r['target_calories']:.0f} kcal")
            st.caption(f"Goal: **{goal}** | Activity: **{lv}**")

    # Clear chat
    st.markdown("---")
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN — Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='fitbot-header'>
    <div style='font-size:2.8rem'>🏋️</div>
    <div>
        <p class='fitbot-title'>Fitness AI Chatbot</p>
        <p class='fitbot-subtitle'>
            Hybrid NLP Engine &nbsp;·&nbsp; Intent Classification &nbsp;·&nbsp;
            Semantic Search &nbsp;·&nbsp; 100% Offline
        </p>
    </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN — Chat area
# ─────────────────────────────────────────────────────────────────────────────
chat_col, _ = st.columns([3, 0.01])

with chat_col:
    # Render message history
    chat_html = "<div class='chat-container'>"

    if not st.session_state.messages:
        chat_html += """
        <div style='text-align:center; padding: 60px 20px; color:#334155'>
            <div style='font-size:3rem; margin-bottom:12px'>💬</div>
            <div style='font-size:1rem; font-weight:600; color:#475569'>Ask me anything about fitness!</div>
            <div style='font-size:0.82rem; margin-top:8px; color:#334155'>
                Try: "How do I build muscle?" · "Best diet for fat loss?" · "How to prevent knee pain?"
            </div>
        </div>"""

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f"""
            <div>
                <div class='msg-label' style='text-align:right; color:#3b82f6'>You</div>
                <div class='user-msg'>{msg['content']}</div>
            </div>"""
        else:
            data = msg.get("data", {})
            is_fb = data.get("is_fallback", False)
            src   = data.get("source", "")
            cat   = data.get("category", "unknown")
            sim   = data.get("similarity", 0.0)
            iconf = data.get("intent_confidence", 0.0)
            mq    = data.get("matched_q", "")
            answer = msg["content"]

            colour = cat_colour(cat)

            if is_fb:
                chat_html += f"""
                <div>
                    <div class='msg-label' style='color:#a78bfa'>FitBot</div>
                    <div class='bot-fallback'>{answer}</div>
                </div>"""
            else:
                badges = f"""
                <div class='badge-row'>
                    <span class='badge badge-cat'>📂 {cat.replace('_',' ').title()}</span>
                    <span class='badge badge-sim'>📊 {sim:.1f}% match</span>
                    <span class='badge badge-conf'>🧠 {iconf:.1f}% confidence</span>
                    <span class='badge badge-src'>⚡ {src}</span>
                </div>"""
                matched = f"<div class='matched-q'>🔍 Matched: {mq[:80]}{'...' if len(str(mq)) > 80 else ''}</div>" if mq else ""

                chat_html += f"""
                <div>
                    <div class='msg-label' style='color:#a78bfa'>FitBot</div>
                    <div class='bot-msg'>
                        {answer}
                        {badges}
                        {matched}
                    </div>
                </div>"""

    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # ── Input row ──
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "message",
            placeholder="Ask a fitness question…",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_send:
        send = st.button("Send →", use_container_width=True)

    if (send or user_input) and user_input.strip():
        question = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Thinking…"):
            result = bot.predict(question)

        st.session_state.messages.append({
            "role":    "assistant",
            "content": result["answer"],
            "data":    result,
        })
        st.rerun()

    # ── Suggested questions ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.78rem; color:#475569; margin-bottom:8px; "
        "text-transform:uppercase; letter-spacing:0.08em; font-weight:600'>Try asking…</div>",
        unsafe_allow_html=True
    )
    suggestions = [
        "How do I build muscle as a beginner?",
        "Best foods for fat loss?",
        "How to prevent knee pain when squatting?",
        "Does creatine actually work?",
        "What should I eat after a workout?",
        "How many days a week should I train?",
    ]
    cols = st.columns(3)
    for i, sug in enumerate(suggestions):
        if cols[i % 3].button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": sug})
            result = bot.predict(sug)
            st.session_state.messages.append({
                "role":    "assistant",
                "content": result["answer"],
                "data":    result,
            })
            st.rerun()
