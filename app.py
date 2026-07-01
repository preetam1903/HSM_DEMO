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
st.write("COIL_OPERATION_FACT Columns")
st.write(coil_df.columns.tolist())
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
# ==========================================================
# PLANNER AGENT
# ==========================================================

def planner_agent(question):

    q = question.lower()

    plan = {
        "question": question,
        "intent": "Query",
        "primary_kpi": "Unknown",
        "time_period": "Current",
        "weeks": [],
        "agents": []
    }

    # -----------------------------
    # KPI Detection
    # -----------------------------

    if "production" in q:
        plan["primary_kpi"] = "Production"

    elif "dwell" in q:
        plan["primary_kpi"] = "Dwell Time"

    elif "inventory" in q:
        plan["primary_kpi"] = "Inventory"

    elif "maintenance" in q:
        plan["primary_kpi"] = "Maintenance"

    elif "active" in q:
        plan["primary_kpi"] = "Active Coils"

    # -----------------------------
    # Time Detection
    # -----------------------------

    if "last 3 week" in q or "3 weeks" in q:

        plan["time_period"] = "Last 3 Weeks"

        latest_week = (
            pd.to_datetime(coil_df["PROD_DATE"])
            .dt.isocalendar()
            .week
            .max()
        )

        plan["weeks"] = [
            int(latest_week-2),
            int(latest_week-1),
            int(latest_week)
        ]

    # -----------------------------
    # Intent Detection
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

        plan["intent"] = "Investigation"

        plan["agents"] = [

            "Planner Agent",
            "Context Agent",
            "Trend Agent",
            "Event Agent",
            "Inventory Agent",
            "Dwell Agent",
            "Correlation Agent",
            "Executive Summary Agent"

        ]

    else:

        plan["agents"] = [

            "Data Query Agent"

        ]

    return plan

# ==========================================================
# PLANNER DISPLAY
# ==========================================================

def planner_display(plan):

    st.subheader("🧠 Planner Agent")

    st.success("Investigation planned successfully")

    st.write("### Question")
    st.info(plan["question"])

    c1, c2 = st.columns(2)

    with c1:

        st.write("**Intent**")
        st.success(plan["intent"])

        st.write("**Primary KPI**")
        st.info(plan["primary_kpi"])

    with c2:

        st.write("**Time Period**")
        st.success(plan["time_period"])

        st.write("**Weeks**")
        st.info(", ".join(map(str, plan["weeks"])))

    st.write("### Investigation Plan")

    for a in plan["agents"][1:]:

        st.write("➡️", a)

# ==========================================================
# CONTEXT AGENT
# ==========================================================

def context_agent(plan):

    st.subheader("📅 Context Agent")

    st.success("Question understood successfully")

    c1, c2 = st.columns(2)

    with c1:

        st.write("**Question**")
        st.info(plan["question"])

        st.write("**Intent**")
        st.success(plan["intent"])

        st.write("**Primary KPI**")
        st.info(plan["primary_kpi"])

    with c2:

        st.write("**Time Period**")
        st.success(plan["time_period"])

        st.write("**Weeks Selected**")
        st.info(", ".join(map(str, plan["weeks"])))

        st.write("**Plant**")
        st.success("HSM")

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
###########################

# ==========================================================
# TREND AGENT
# ==========================================================

def trend_agent(coil_df, plan):

    st.subheader("📈 Trend Agent")

    status = st.empty()
    status.info("Reading production data...")

    df = coil_df.copy()

    # ---------------------------------------
    # Create Week Number
    # ---------------------------------------

    df["WEEK_NO"] = (
        pd.to_datetime(df["PROD_DATE"])
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # ---------------------------------------
    # Filter Investigation Weeks
    # ---------------------------------------

    if len(plan["weeks"]) > 0:

        df = df[
            df["WEEK_NO"].isin(plan["weeks"])
        ]

    # ---------------------------------------
    # Weekly Aggregation
    # ---------------------------------------

    weekly = (
        df.groupby("WEEK_NO")
        .agg(
            Production=("MAT_ID","count"),
            Tonnage=("COIL_WEIGHT_TON","sum")
        )
        .reset_index()
        .sort_values("WEEK_NO")
    )

    status.success("Weekly production calculated")

    # ---------------------------------------
    # Generated Query
    # ---------------------------------------

    st.write("### Generated Pandas Query")

    st.code(
"""
df["WEEK_NO"] = pd.to_datetime(df["PROD_DATE"]).dt.isocalendar().week

weekly = (
    df[df["WEEK_NO"].isin(selected_weeks)]
      .groupby("WEEK_NO")
      .agg(
            Production=("MAT_ID","count"),
            Tonnage=("COIL_WEIGHT_TON","sum")
      )
      .reset_index()
)
"""
    )

    # ---------------------------------------
    # Evidence
    # ---------------------------------------

    st.write("### Weekly Production")

    st.dataframe(
        weekly,
        use_container_width=True
    )

    # ---------------------------------------
    # Week-on-Week Calculation
    # ---------------------------------------

    weekly["WoW_%"] = (
        weekly["Production"]
        .pct_change()*100
    )

    st.write("### Week-on-Week Trend")

    st.dataframe(
        weekly.round(2),
        use_container_width=True
    )

    # ---------------------------------------
    # Trend Chart
    # ---------------------------------------

    chart = (
        weekly
        .set_index("WEEK_NO")["Production"]
    )

    st.line_chart(chart)

    # ---------------------------------------
    # Overall Reduction
    # ---------------------------------------

    first = weekly.iloc[0]["Production"]
    last = weekly.iloc[-1]["Production"]

    overall = (
        (last-first)
        /first
    )*100

    st.metric(
        "Overall Production Change",
        f"{overall:.2f}%"
    )

    # ---------------------------------------
    # Finding
    # ---------------------------------------

    if overall < 0:

        finding = (
            f"""
Production reduced by **{abs(overall):.2f}%**

Week {int(weekly.iloc[0]['WEEK_NO'])}
↓

Week {int(weekly.iloc[-1]['WEEK_NO'])}

The reduction was continuous across the
selected investigation period.
"""
        )

    elif overall > 0:

        finding = (
            f"""
Production increased by **{overall:.2f}%**
during the investigation period.
"""
        )

    else:

        finding = (
            "Production remained stable."
        )

    st.success(finding)

    return {

        "weekly": weekly,

        "overall_change": overall,

        "finding": finding

    }

# ==========================================================
# EVENT AGENT
# ==========================================================

def event_agent(events_df):

    st.subheader("🛠️ Event Agent")

    status = st.empty()

    status.info("Reading manufacturing events...")

    df = events_df.copy()

    st.write("### Generated Pandas Query")

    st.code("""
events_df.sort_values("EVENT_DATE")
""")

    df["DATE"] = pd.to_datetime(df["DATE"])

    df = df.sort_values("DATE")

    st.write("### Manufacturing Events")

    st.dataframe(
        df,
        use_container_width=True
    )

    major_events = df[
        df["SEVERITY"].isin(
            [
                "High",
                "Critical"
            ]
        )
    ]

    status.success("Events analysed")

    st.write("### Evidence")

    st.dataframe(
        major_events,
        use_container_width=True
    )

    if len(major_events):

        finding = f"""
    Detected **{len(major_events)}** High/Critical manufacturing events.

    Estimated Lost Coils :

    **{major_events['EST_LOST_COILS'].sum()}**

    Primary Areas Impacted :

    {", ".join(major_events['AREA'].unique())}

    Potential production impact identified.
    """

    st.success(finding)

    return major_events

# ==========================================================
# INVENTORY AGENT
# ==========================================================

def inventory_agent(inventory_df):

    st.subheader("📦 Inventory Agent")

    status = st.empty()
    status.info("Reading inventory snapshot...")

    df = inventory_df.copy()

    df["DATE"] = pd.to_datetime(df["DATE"])

    st.write("### Generated Pandas Query")

    st.code("""
inventory_df.groupby("PROCESS").agg(
    Total_Coils=("TOTAL_COILS","sum"),
    Active_Coils=("ACTIVE_COILS","sum"),
    High_Priority=("HIGH_PRIORITY_COILS","sum"),
    Avg_Dwell=("AVG_DWELL_DAYS","mean")
)
""")

    inventory = (
        df.groupby("PROCESS")
        .agg(
            Total_Coils=("TOTAL_COILS", "sum"),
            Active_Coils=("ACTIVE_COILS", "sum"),
            High_Priority=("HIGH_PRIORITY_COILS", "sum"),
            Avg_Dwell=("AVG_DWELL_DAYS", "mean")
        )
        .reset_index()
        .sort_values("Total_Coils", ascending=False)
    )

    status.success("Inventory analysis completed")

    st.write("### Inventory Summary")

    st.dataframe(inventory, use_container_width=True)

    highest = inventory.iloc[0]

    st.success(f"""
Highest inventory is at **{highest['PROCESS']}**

• Total Coils: **{int(highest['Total_Coils'])}**

• Active Coils: **{int(highest['Active_Coils'])}**

• High Priority Coils: **{int(highest['High_Priority'])}**

• Average Dwell: **{highest['Avg_Dwell']:.2f} days**

This process should be investigated for possible congestion.
""")

    return inventory

# ==========================================================
# DWELL AGENT
# ==========================================================

def dwell_agent(coil_df):

    st.subheader("⏳ Dwell Agent")

    status = st.empty()

    status.info("Reading dwell time information...")

    df = coil_df.copy()

    st.write("### Generated Pandas Query")

    st.code("""
coil_df.groupby("NEXT_INSTALLATION")
       .agg(
            Average_Dwell=("DWELL_DAYS","mean"),
            Maximum_Dwell=("DWELL_DAYS","max"),
            Coil_Count=("MAT_ID","count")
       )
       .reset_index()
""")

    dwell = (
        df.groupby("NEXT_INSTALLATION")
        .agg(
            Average_Dwell=("DWELL_DAYS","mean"),
            Maximum_Dwell=("DWELL_DAYS","max"),
            Coil_Count=("MAT_ID","count")
        )
        .reset_index()
    )

    status.success("Dwell analysis completed")

    st.write("### Dwell Time by Next Installation")

    st.dataframe(
        dwell.round(2),
        use_container_width=True
    )

    # --------------------------
    # Daily Abnormal Dwell
    # --------------------------

    abnormal = df[df["DWELL_DAYS"] > 5]

    st.write("### Abnormal Dwell (>5 Days)")

    if len(abnormal):

        st.dataframe(
            abnormal[
                [
                    "MAT_ID",
                    "PROD_DATE",
                    "NEXT_INSTALLATION",
                    "DWELL_DAYS"
                ]
            ],
            use_container_width=True
        )

        finding = f"""
{len(abnormal)} coils exceeded the
5-day dwell threshold.

Although the weekly average may appear normal,
a small number of coils experienced significant
waiting time.

These abnormal dwell spikes can delay downstream
processing and reduce production.
"""

    else:

        finding = """
No abnormal dwell time detected.
"""

    st.success(finding)

    return abnormal


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

    for agent in plan["agents"]:

        st.markdown("---")

        agent_box = st.container()

        
        # -----------------------------
        # Execute Agent
        # -----------------------------

        with agent_box:

            show_agent(agent, "Running")
            if agent == "Planner Agent":

                planner_display(plan)

            elif agent == "Context Agent":

                context_agent(plan)

            elif agent == "Trend Agent":
                trend_agent(coil_df)

            elif agent == "Event Agent":
                event_agent(events_df)

            elif agent == "Inventory Agent":
                inventory_agent(inventory_df)

            elif agent == "Dwell Agent":
                dwell_agent(coil_df)

            
                

            show_agent(f"{agent} Completed", "Completed")
        

    
