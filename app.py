import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
#from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os

# -------------------
# PAGE CONFIG
# -------------------

st.set_page_config(
    page_title="Production AI",
    layout="wide"
)
# -------------------
# PREMIUM UI STYLING
# -------------------

st.markdown(
    """

    <style>

    .stApp {

        background:
        linear-gradient(
            135deg,
            #0b1120,
            #111827,
            #1e293b
        );

        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {

        background:
        linear-gradient(
            180deg,
            #111827,
            #0f172a
        );
    }

    h1 {

        color: #60a5fa !important;

        font-size: 48px !important;

        font-weight: 800 !important;
    }

    h2, h3 {

        color: #93c5fd !important;
    }

    p,
    label,
    .stMarkdown {

        color: #f8fafc !important;
    }

    div[data-testid="metric-container"] {

        background:
        rgba(255,255,255,0.08);

        border:
        1px solid rgba(255,255,255,0.12);

        padding: 20px;

        border-radius: 20px;

        backdrop-filter: blur(10px);

        box-shadow:
        0 8px 24px rgba(0,0,0,0.35);
    }

    .stButton button {

        background:
        linear-gradient(
            135deg,
            #2563eb,
            #1d4ed8
        );

        color: white !important;

        border-radius: 12px;

        border: none;

        padding: 10px 24px;

        font-weight: 700;
    }

    .stButton button:hover {

        background:
        linear-gradient(
            135deg,
            #3b82f6,
            #2563eb
        );
    }

    /* AI STATUS BANNER */

    .ai-banner {

        background:
        linear-gradient(
            135deg,
            rgba(37,99,235,0.25),
            rgba(6,182,212,0.20)
        );

        border:
        1px solid rgba(96,165,250,0.35);

        border-radius: 18px;

        padding: 18px;

        margin-bottom: 25px;

        box-shadow:
        0 0 24px rgba(59,130,246,0.25);

        animation:
        pulseGlow 3s infinite;
    }

    .ai-title {

        color: #f8fafc;

        font-size: 14px;

        font-weight: 600;
    }

    .ai-sub {

        color: #cbd5e1;

        margin-top: 6px;

        font-size: 10px;
        
    }

    @keyframes pulseGlow {

        0% {

            box-shadow:
            0 0 12px rgba(59,130,246,0.18);
        }

        50% {

            box-shadow:
            0 0 28px rgba(59,130,246,0.35);
        }

        100% {

            box-shadow:
            0 0 12px rgba(59,130,246,0.18);
        }
    }
    /* INSIGHT BANNER */

.insight-banner {

    background:
    linear-gradient(
        135deg,
        rgba(37,99,235,0.22),
        rgba(15,23,42,0.92)
    );

    border:
    1px solid rgba(96,165,250,0.35);

    border-radius: 18px;

    padding: 18px;

    margin-top: 20px;

    margin-bottom: 20px;

    color: #f8fafc;

    font-size: 16px;

    font-weight: 600;

    box-shadow:
    0 0 24px rgba(59,130,246,0.25);

    animation:
    insightGlow 2.5s infinite;
}

/* BLINKING GLOW */

@keyframes insightGlow {

    0% {

        box-shadow:
        0 0 10px rgba(59,130,246,0.15);
    }

    50% {

        box-shadow:
        0 0 28px rgba(59,130,246,0.40);
    }

    100% {

        box-shadow:
        0 0 10px rgba(59,130,246,0.15);
    }
}
    
    </style>
    """,

    unsafe_allow_html=True
)
st.title(
    "🏭 Production AI Copilot"
)

st.write(
    "KEY KPI'S"
)


# -------------------
# LOAD AI MODEL
# -------------------

@st.cache_data
def load_data():

    coil_df = pd.read_excel("COIL_OPERATION_FACT.xlsx")

    inventory_df = pd.read_excel("INVENTORY_SNAPSHOT.xlsx")

    events_df = pd.read_excel("MANUFACTURING_EVENTS.xlsx")

    kpi_df = pd.read_excel("KPI_METADATA.xlsx")

    relationship_df = pd.read_excel("KPI_RELATIONSHIPS.xlsx")

    coil_df["PROD_DATE"] = pd.to_datetime(coil_df["PROD_DATE"])

    return (
        coil_df,
        inventory_df,
        events_df,
        kpi_df,
        relationship_df
    )


coil_df, inventory_df, events_df, kpi_df, relationship_df = load_data()
# Temporary aliases
production_df = coil_df
master_df = coil_df
material_flow_df = pd.DataFrame()

#
# -------------------
# AI INSIGHT BANNER
# -------------------

# -------------------
# AI INSIGHT BANNER
# -------------------




# -------------------
# EXECUTIVE SUMMARY
# -------------------
# -------------------
# EXECUTIVE SUMMARY
# -------------------

def generate_executive_summary(result_df):

    try:

        total_rows = len(result_df)

        if "TONNAGE" in result_df.columns:

            total_tonnage = (
                result_df[
                    "TONNAGE"
                ]
                .sum()
            )

        else:

            total_tonnage = 0

        summary = f"""
🧠 Executive Summary

• Records analyzed: {total_rows}

• Total tonnage impacted: {total_tonnage:,.2f}

• AI Observation:
Operational trends appear stable with active monitoring enabled.
"""

        st.markdown(
            f"""
<div class="insight-banner">
{summary}
</div>
""",
            unsafe_allow_html=True
        )

    except:

        pass
# -------------------
# AI RECOMMENDATION ENGINE
# -------------------

def show_ai_recommendation(message):

    st.markdown(
        f"""
<div class="insight-banner">

🧠 AI Recommendation

<br><br>

{message}

</div>
""",
        unsafe_allow_html=True
    )

    

   

# ==========================================================
# PLANNER AGENT
# ==========================================================

def planner_agent(question: str):
    """
    Decide whether the question is a simple data query
    or a multi-agent investigation.
    """

    q = question.lower()

    plan = {
        "intent": "query",
        "primary_kpi": "Unknown",
        "agents": []
    }

    # -------------------------------
    # Investigation Keywords
    # -------------------------------
    investigation_words = [
        "why",
        "reason",
        "root cause",
        "investigate",
        "analysis",
        "analyse",
        "impact",
        "correlation",
        "anomaly",
        "drop",
        "reduce",
        "decline",
        "increase"
    ]

    # -------------------------------
    # Detect KPI
    # -------------------------------
    if "production" in q:
        plan["primary_kpi"] = "Production"

    elif "dwell" in q:
        plan["primary_kpi"] = "Dwell Time"

    elif "inventory" in q:
        plan["primary_kpi"] = "Inventory"

    elif "active" in q:
        plan["primary_kpi"] = "Active Coils"

    elif "yield" in q:
        plan["primary_kpi"] = "Yield"

    elif "speed" in q:
        plan["primary_kpi"] = "Rolling Speed"

    # -------------------------------
    # Intent
    # -------------------------------
    is_investigation = any(word in q for word in investigation_words)

    if is_investigation:

        plan["intent"] = "investigation"

        plan["agents"] = [
            "Planner Agent",
            "Trend Agent",
            "Event Agent",
            "Inventory Agent",
            "Dwell Agent",
            "Executive Summary Agent"
        ]

    else:

        plan["intent"] = "query"

        plan["agents"] = [
            "Data Query Agent"
        ]

    return plan


# QUESTION ENGINE
# -------------------



# -------------------
# USER INTERFACE
# -------------------

question = st.text_input(
    "Ask a question"
)

if st.button("Ask"):

    question = "Why has production reduced over the last 3 weeks?"

    plan = planner_agent(question)

    st.write(plan)
    

    
