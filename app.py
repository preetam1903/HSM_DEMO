import streamlit as st
import pandas as pd
from openai import OpenAI
import time

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Production AI Copilot",
    page_icon="🏭",
    layout="wide"
)

# ==========================================================
# PREMIUM UI
# ==========================================================

st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#081120,#111827,#1e293b);
color:white;
}

h1{
color:#60a5fa;
font-weight:800;
}

div[data-testid="metric-container"]{
background:rgba(255,255,255,0.08);
border-radius:18px;
padding:18px;
border:1px solid rgba(255,255,255,.10);
box-shadow:0px 8px 18px rgba(0,0,0,.30);
}

.stButton>button{
background:#2563eb;
color:white;
border-radius:10px;
font-weight:bold;
border:none;
height:45px;
width:180px;
}

.agent{
padding:12px;
border-radius:10px;
background:#172554;
border-left:5px solid #3b82f6;
margin-bottom:8px;
}

.successAgent{
padding:12px;
border-radius:10px;
background:#14532d;
border-left:5px solid #22c55e;
margin-bottom:8px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# TITLE
# ==========================================================

st.title("🏭 Production AI Investigation Copilot")

st.caption(
    "Executive Investigation Platform for Manufacturing Operations"
)

# ==========================================================
# OPENAI
# ==========================================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data
def load_data():

    coil_df = pd.read_excel("COIL_OPERATION_FACT.xlsx")

    inventory_df = pd.read_excel("INVENTORY_SNAPSHOT.xlsx")

    events_df = pd.read_excel("MANUFACTURING_EVENTS.xlsx")

    kpi_df = pd.read_excel("KPI_METADATA.xlsx")

    relationship_df = pd.read_excel("KPI_RELATIONSHIPS.xlsx")

    playbook_df = pd.read_excel("INVESTIGATION_PLAYBOOK.xlsx")

    coil_df["PROD_DATE"] = pd.to_datetime(
        coil_df["PROD_DATE"]
    )

    return (
        coil_df,
        inventory_df,
        events_df,
        kpi_df,
        relationship_df,
        playbook_df
    )


(
coil_df,
inventory_df,
events_df,
kpi_df,
relationship_df,
playbook_df
)=load_data()

# ==========================================================
# KPI CARDS
# ==========================================================

st.subheader("Executive KPIs")

c1,c2,c3,c4=st.columns(4)

with c1:

    st.metric(
        "Total Coils",
        len(coil_df)
    )

with c2:

    st.metric(
        "Active Coils",
        len(
            coil_df[
                coil_df["COIL_STATUS"]=="ACTIVE"
            ]
        )
    )

with c3:

    st.metric(
        "Inventory",
        len(inventory_df)
    )

with c4:

    st.metric(
        "Manufacturing Events",
        len(events_df)
    )

st.divider()

# ==========================================================
# PLANNER AGENT
# ==========================================================

def planner_agent(question):

    q = question.lower()

    plan = {
        "intent": "query",
        "primary_kpi": "Unknown",
        "agents": []
    }

    # -----------------------------
    # Detect KPI
    # -----------------------------

    if "production" in q:
        plan["primary_kpi"] = "Production"

    elif "dwell" in q:
        plan["primary_kpi"] = "Dwell Time"

    elif "inventory" in q:
        plan["primary_kpi"] = "Inventory"

    elif "active" in q:
        plan["primary_kpi"] = "Active Coils"

    elif "maintenance" in q:
        plan["primary_kpi"] = "Maintenance"

    # -----------------------------
    # Investigation Detection
    # -----------------------------

    investigation_words = [

        "why",

        "reason",

        "investigate",

        "analysis",

        "analyse",

        "impact",

        "drop",

        "decline",

        "root cause",

        "correlation",

        "anomaly"

    ]

    if any(word in q for word in investigation_words):

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


# ==========================================================
# AGENT STATUS CARD
# ==========================================================



# ==========================================================
# AGENT STATUS CARD
# ==========================================================

def show_agent(agent_name, status="Waiting"):

    if status == "Waiting":
        color = "#1e3a8a"
        icon = "⚪"

    elif status == "Running":
        color = "#ca8a04"
        icon = "🟡"

    else:
        color = "#166534"
        icon = "✅"

    st.markdown(
        f"""
        <div style="
        background:{color};
        padding:14px;
        border-radius:10px;
        margin-bottom:8px;
        font-size:17px;
        font-weight:bold;
        color:white;">
        {icon} {agent_name}
        </div>
        """,
        unsafe_allow_html=True
    )
def trend_agent(coil_df):

    st.subheader("📈 Trend Agent")

    status = st.empty()

    status.info("Reading production data...")

    df = coil_df.copy()

    weekly = (
        df.groupby("WEEK_NO")
        .agg(
            Production=("COIL_ID","count"),
            Tonnage=("COIL_WEIGHT_TON","sum")
        )
        .reset_index()
    )

    status.success("Weekly production calculated")

    st.write("### Generated Pandas")

    st.code(
"""
weekly = (
    coil_df.groupby("WEEK_NO")
    .agg(
        Production=("COIL_ID","count"),
        Tonnage=("COIL_WEIGHT_TON","sum")
    )
    .reset_index()
)
"""
)

    st.write("### Evidence")

    st.dataframe(
        weekly,
        use_container_width=True
    )

    first = weekly.iloc[0]["Production"]

    last = weekly.iloc[-1]["Production"]

    change = (
        (last-first)
        /first
    )*100

    st.write("### Calculation")

    st.write(

        f"""
First Week Production : **{first} coils**

Last Week Production : **{last} coils**

Percentage Change :

(({last}-{first})/{first})×100

= **{change:.2f}%**
"""
    )

    if change<0:
        finding=f"""
Production reduced by **{abs(change):.2f}%**
over the last three weeks.
"""

    else:

        finding=f"""
Production increased by **{change:.2f}%**
over the last three weeks.
"""

    st.success(finding)

    return weekly

# ==========================================================
# ASK EXECUTIVE
# ==========================================================

st.subheader("🧠 Ask Executive")

question=st.text_input(

    "Ask anything about Production, Inventory, Dwell Time or Manufacturing"

)

if st.button("Investigate"):

    plan = planner_agent(question)

    st.divider()

    st.subheader("🧠 Investigation Planner")

    st.write(f"**Intent :** {plan['intent']}")
    st.write(f"**Primary KPI :** {plan['primary_kpi']}")

    st.write("### Investigation Progress")

    placeholder = st.empty()

    for agent in plan["agents"]:

        with placeholder.container():

            for completed in plan["agents"]:

                if completed == agent:

                    show_agent(completed, "Running")

# -------------------------
# Execute Trend Agent
# -------------------------

                    if completed == "Trend Agent":

                        trend_agent(coil_df)

                    break

                show_agent(completed, "Completed")

            time.sleep(1)

    with placeholder.container():

        for completed in plan["agents"]:

            show_agent(completed, "Completed")

    st.success("Investigation Planning Completed")


        

    
