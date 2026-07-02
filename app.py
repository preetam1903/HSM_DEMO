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

/* Main Background */

.stApp{
    background:#f7f9fc;
}

/* Headers */

h1,h2,h3{
    color:#1f2937;
}

/* KPI Cards */

div[data-testid="metric-container"]{
    background:white;
    border-radius:12px;
    padding:18px;
    border:2px solid black;
    box-shadow:0 2px 8px rgba(0,0,0,0.08);
}

/* Buttons */

.stButton>button{

    background:#2563eb;

    border:2px solid black;

    color:white;

/* Running Agent */

.runningAgent{

    background:white;

    border:2px solid black;

    padding:16px;

    border-radius:10px;

    margin-bottom:10px;

}

/* Completed Agent */

.successAgent{

    background:white;

    border:2px solid black;

    padding:16px;

    border-radius:10px;

    margin-bottom:10px;

}

/* Tables */

[data-testid="stDataFrame"]{

    background:white;

    border:2px solid black;

    border-radius:10px;

}

/* Text Input */

.stTextInput input{

    background:white;

    border:2px solid black;

}

details{

    border:2px solid black;

    border-radius:8px;

    background:white;

    padding:6px;

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

#######################



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

    # ---------------------------------------------
# Investigation Questions
# ---------------------------------------------

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

# ---------------------------------------------
# Simple Analysis Questions
# ---------------------------------------------

    else:

        plan["intent"] = "Analysis"

        plan["agents"] = [

            "Trend Agent"

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

    if status == "Running":

        css = "runningAgent"
        icon = "🟡"

    elif status == "Completed":

        css = "successAgent"
        icon = "✅"

    else:

        css = "runningAgent"
        icon = "⚪"

    st.markdown(
        f"""
        <div class="{css}">
            <h4 style="margin:0;">{icon} {agent_name}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

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
# Production Trend by Grade
# ---------------------------------------

    st.write("### Production Trend by Grade")

    grade_week = (

        df.groupby(["GRADE","WEEK_NO"])

        .agg(

            Production=("MAT_ID","count")

        )

        .reset_index()

    )

    pivot = (

        grade_week

        .pivot(

            index="GRADE",

            columns="WEEK_NO",

            values="Production"

        )

        .fillna(0)

    )

    weeks = sorted(df["WEEK_NO"].unique())

    if len(weeks) >= 2:

        first_week = weeks[0]

        last_week = weeks[-1]

        pivot["Change %"] = (

            (
                pivot[last_week] -
                pivot[first_week]
            )

            / pivot[first_week].replace(0,1)

        ) * 100

    else:

        pivot["Change %"] = 0

    pivot = (

        pivot

        .sort_values(

            "Change %"

        )

    )

    st.dataframe(

        pivot.round(1),

        use_container_width=True

    )

    worst_grade = pivot.index[0]

    worst_change = pivot.iloc[0]["Change %"]

    st.error(f"""

    Largest production reduction detected

    **Grade : {worst_grade}**

    **Reduction : {abs(worst_change):.1f}%**

    This dimension has been identified as the
    largest contributor to the production decline.

    In Version 1, the Correlation Agent uses this
    information together with Inventory, Events and
    Dwell evidence to determine the most likely
    business reason.

    **Future Enhancement (Version 2):**
    Instead of analysing predefined dimensions such
    as Grade, the Metadata Agent will automatically
    identify the most relevant business dimension
    (Customer, Route, Width, Thickness, Order,
    Production Unit, etc.) and pass it to the
    Correlation Agent for investigation.

    """)

    

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

        "finding": finding,
        "worst_grade": worst_grade,

        "worst_grade_change": worst_change

    }

# ==========================================================
# EVENT AGENT
# ==========================================================
# ==========================================================
# EVENT AGENT
# ==========================================================

def event_agent(events_df, plan):

    st.subheader("🛠️ Event Agent")

    status = st.empty()
    status.info("Searching for relevant manufacturing events...")

    df = events_df.copy()

    df["DATE"] = pd.to_datetime(df["DATE"])
    df["WEEK_NO"] = df["DATE"].dt.isocalendar().week.astype(int)

    # ----------------------------------------
    # Filter Investigation Weeks
    # ----------------------------------------

    if len(plan["weeks"]) > 0:

        df = df[
            df["WEEK_NO"].isin(plan["weeks"])
        ]

    # ----------------------------------------
    # Keep only High / Critical
    # ----------------------------------------

    df = df[
        df["SEVERITY"].isin(
            ["High", "Critical"]
        )
    ]

    status.success("Relevant events identified")

    st.write("### Generated Pandas Query")

    st.code("""
events_df["WEEK_NO"]=pd.to_datetime(events_df["DATE"]).dt.isocalendar().week

events=events_df[
    (events_df["WEEK_NO"].isin(selected_weeks))
    &
    (events_df["SEVERITY"].isin(["High","Critical"]))
]
""")

    st.write("### Relevant Manufacturing Events")

    st.dataframe(
        df[
            [
                "DATE",
                "AREA",
                "EQUIPMENT",
                "EVENT_TYPE",
                "SEVERITY",
                "EST_LOST_COILS",
                "ROOT_CAUSE"
            ]
        ],
        use_container_width=True
    )

    total_loss = df["EST_LOST_COILS"].sum()

    st.metric(
        "Estimated Lost Coils",
        int(total_loss)
    )

    st.success(
        f"""
{len(df)} High/Critical events were found during the
selected investigation period.

Estimated Production Loss :

**{int(total_loss)} coils**
"""
    )

    return {

        "events": df,

        "lost_coils": total_loss,

        "count": len(df)
    }

# ==========================================================
# INVENTORY AGENT
# ==========================================================

# ==========================================================
# INVENTORY AGENT
# ==========================================================

def inventory_agent(inventory_df, coil_df, plan):

    st.subheader("📦 Inventory Agent")

    status = st.empty()
    status.info("Analysing inventory and blocked coils...")

    inv = inventory_df.copy()
    coils = coil_df.copy()

    inv["DATE"] = pd.to_datetime(inv["DATE"])
    coils["PROD_DATE"] = pd.to_datetime(coils["PROD_DATE"])

    inv["WEEK_NO"] = inv["DATE"].dt.isocalendar().week.astype(int)
    coils["WEEK_NO"] = coils["PROD_DATE"].dt.isocalendar().week.astype(int)

    # --------------------------------------------------
    # Investigation Weeks
    # --------------------------------------------------

    if len(plan["weeks"]) > 0:

        inv = inv[
            inv["WEEK_NO"].isin(plan["weeks"])
        ]

        coils = coils[
            coils["WEEK_NO"].isin(plan["weeks"])
        ]

    status.success("Relevant inventory identified")

    # --------------------------------------------------
    # Inventory Trend
    # --------------------------------------------------

    st.write("### Inventory Trend")

    inventory = (

        inv.groupby(
            ["WEEK_NO","PROCESS"]
        )

        .agg(

            Total_Coils=("TOTAL_COILS","sum"),

            Active_Coils=("ACTIVE_COILS","sum"),

            HighPriority=("HIGH_PRIORITY_COILS","sum"),

            Avg_Dwell=("AVG_DWELL_DAYS","mean")

        )

        .reset_index()

    )

    st.dataframe(
        inventory,
        use_container_width=True
    )

    # --------------------------------------------------
    # High Priority Trend
    # --------------------------------------------------

    st.write("### High Priority Coils")

    hp = (

        inventory.groupby("WEEK_NO")

        .agg(
            HighPriority=("HighPriority","sum")
        )

        .reset_index()

    )

    st.dataframe(
        hp,
        use_container_width=True
    )

    st.line_chart(

        hp.set_index("WEEK_NO")["HighPriority"]

    )

    # --------------------------------------------------
    # Blocked Coils
    # --------------------------------------------------

    blocked = coils[

        (coils["COIL_STATUS"]=="ACTIVE")

        &

        (coils["DWELL_DAYS"]>5)

    ]

    blocked_summary = (

        blocked.groupby("NEXT_INSTALLATION")

        .agg(

            Blocked_Coils=("MAT_ID","count"),

            Average_Dwell=("DWELL_DAYS","mean"),

            Maximum_Dwell=("DWELL_DAYS","max")

        )

        .reset_index()

    )

    st.write("### Blocked / Waiting Coils")

    st.dataframe(

        blocked_summary,

        use_container_width=True

    )

    with st.expander("View Blocked Coils"):

        st.dataframe(

            blocked[

                [

                    "MAT_ID",

                    "GRADE",

                    "NEXT_INSTALLATION",

                    "DWELL_DAYS",

                    "COIL_STATUS"

                ]

            ],

            use_container_width=True

        )

    # --------------------------------------------------
    # Highest Inventory
    # --------------------------------------------------

    latest = inventory[

        inventory["WEEK_NO"]==inventory["WEEK_NO"].max()

    ]

    highest = latest.loc[

        latest["Total_Coils"].idxmax()

    ]

    st.success(f"""

Highest Inventory Process

**{highest['PROCESS']}**

Inventory : **{int(highest['Total_Coils'])} coils**

High Priority : **{int(highest['HighPriority'])} coils**

Blocked Coils : **{len(blocked)}**

Possible downstream congestion before

**{highest['PROCESS']}**

""")

    return {

        "inventory":inventory,

        "highest_process":highest["PROCESS"],

        "highest_inventory":int(highest["Total_Coils"]),

        "blocked":blocked,

        "blocked_count":len(blocked),

        "high_priority":hp

    }

# ==========================================================
# DWELL AGENT
# ==========================================================

def dwell_agent(coil_df,plan):

    st.subheader("⏳ Dwell Agent")

    status = st.empty()

    status.info("Reading dwell time information...")

    df = coil_df.copy()

    df["WEEK_NO"] = (
        pd.to_datetime(df["PROD_DATE"])
        .dt.isocalendar()
        .week
        .astype(int)
    )

    if len(plan["weeks"]) > 0:

        df = df[
            df["WEEK_NO"].isin(plan["weeks"])
        ]

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
# CORRELATION AGENT
# ==========================================================

def correlation_agent(
    trend_result,
    event_result,
    inventory_result,
    dwell_result
):

    st.subheader("🔗 Correlation Agent")

    st.info("Correlating findings from all investigation agents...")

    production_change = trend_result["overall_change"]

    event_count = event_result["count"]

    lost_coils = event_result["lost_coils"]

    highest_process = inventory_result["highest_process"]

    highest_inventory = inventory_result["highest_inventory"]

    blocked_coils = len(dwell_result)

    confidence = 70

    reasons = []

    # ---------------------------------------------------
    # Trend
    # ---------------------------------------------------

    if production_change < 0:

        confidence += 5

        reasons.append(
            f"Production reduced by {abs(production_change):.2f}%."
        )

    # ---------------------------------------------------
    # Events
    # ---------------------------------------------------

    if event_count > 0:

        confidence += 5

        reasons.append(
            f"{event_count} High/Critical manufacturing events were detected resulting in an estimated loss of {int(lost_coils)} coils."
        )

    # ---------------------------------------------------
    # Inventory
    # ---------------------------------------------------

    confidence += 5

    reasons.append(
        f"Highest inventory accumulated before {highest_process} ({highest_inventory} coils)."
    )

    # ---------------------------------------------------
    # Blocked Coils
    # ---------------------------------------------------

    if blocked_coils > 0:

        confidence += 5

        reasons.append(
            f"{blocked_coils} coils exceeded the dwell threshold and remained active."
        )

    confidence = min(confidence,95)

    st.write("### Cross-Agent Evidence")

    for r in reasons:

        st.success(r)

    st.write("### AI Correlation")

    st.markdown("""
text
Maintenance / Breakdown
          │
          ▼
Inventory Build-up
          │
          ▼
Higher Dwell Time
          │
          ▼
Production Reduction
""")
    conclusion = f"""
## Executive Correlation Summary

The investigation indicates that the production reduction is not the result of a single event but a combination of operational factors.

### Cross-Agent Evidence

• Production changed by **{production_change:.2f}%**

• **{event_count}** High/Critical manufacturing events occurred during the investigation period.

• Highest inventory accumulated before **{highest_process}**, indicating downstream congestion.

• **{blocked_coils}** active coils exceeded the dwell threshold, suggesting delayed material movement.

### Executive Assessment

The combined evidence suggests that manufacturing disruptions resulted in downstream inventory build-up and increased waiting time, ultimately reducing production throughput.

### Future Enhancement

In the next version, the Correlation Agent will automatically identify the most affected business dimension (Grade, Route, Customer, Order, Width, Thickness, Production Unit, etc.) and correlate it with inventory, events and process bottlenecks to determine the most probable root cause automatically.
"""

    st.success(conclusion)

    return {

        "confidence": confidence,

        "summary": conclusion,

        "reasons": reasons

    }

# ==========================================================
# EXECUTIVE SUMMARY AGENT
# ==========================================================

def executive_summary_agent(

    plan,

    trend_result,

    event_result,

    inventory_result,

    correlation_result

):

    st.subheader("👔 Executive Summary")

    st.success("Executive investigation completed")

    st.write("## Executive Question")

    st.info(plan["question"])

    st.write("## Investigation Result")

    production_change = trend_result["overall_change"]

    if production_change < 0:

        answer = f"""
Production reduced by **{abs(production_change):.2f}%**
during the investigation period.
"""

    else:

        answer = f"""
Production increased by **{production_change:.2f}%**
during the investigation period.
"""

    st.success(answer)

    st.write("## Key Findings")

    c1,c2 = st.columns(2)

    with c1:

        st.metric(
            "Critical Events",
            event_result["count"]
        )

        st.metric(
            "Estimated Lost Coils",
            int(event_result["lost_coils"])
        )

    with c2:

        st.metric(
            "Blocked Coils",
            inventory_result["blocked_count"]
        )

        st.metric(
            "Highest Inventory",
            inventory_result["highest_process"]
        )

    st.write("## AI Investigation Summary")

    st.info(correlation_result["summary"])

    st.write("## Business Recommendation")

    recommendations=[]

    if event_result["count"]>0:

        recommendations.append(
            "• Review maintenance and breakdown history."
        )

    if inventory_result["blocked_count"]>0:

        recommendations.append(
            "• Clear blocked coils before downstream processing."
        )

    recommendations.append(
        f"• Reduce inventory before {inventory_result['highest_process']}."
    )

    recommendations.append(
        "• Review production sequencing for high priority coils."
    )

    recommendations.append(
        "• Continue monitoring dwell time daily."
    )

    for r in recommendations:

        st.write(r)

    st.write("## Confidence")

    st.progress(
        correlation_result["confidence"]/100
    )

    st.success(
        f"""
Overall Investigation Confidence

**{correlation_result['confidence']}%**
"""
    )

    

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

    #st.subheader("🧠 Investigation Planner")

    #st.write(f"**Intent :** {plan['intent']}")
    #st.write(f"**Primary KPI :** {plan['primary_kpi']}")

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
                trend_result = trend_agent(coil_df, plan)

            elif agent == "Event Agent":
                event_result = event_agent(events_df,plan)

            elif agent == "Inventory Agent":
                inventory_result = inventory_agent(inventory_df,coil_df,plan)

            elif agent == "Dwell Agent":

                dwell_result = dwell_agent(coil_df,plan)

            elif agent == "Correlation Agent":

                correlation_result = correlation_agent(

                    trend_result,

                    event_result,

                    inventory_result,

                    dwell_result

                )

            elif agent == "Executive Summary Agent":

                executive_summary_agent(

                    plan,

                    trend_result,

                    event_result,

                    inventory_result,

                    correlation_result

                )

            
                

            show_agent(f"{agent} Completed", "Completed")


st.divider()

###############
# ==========================================================
# DATASETS
# ==========================================================

st.divider()

st.header("📚 Manufacturing Data Repository")

# ---------------------------------------------------------

with st.expander("COIL_OPERATION_FACT.xlsx", expanded=False):

    st.markdown("""
### Purpose
Primary manufacturing dataset.

### Grain
One row = One Coil

### Used By
Trend Agent, Inventory Agent, Dwell Agent

### Key Information
- Coil ID
- Production Date
- Grade
- Width
- Thickness
- Weight
- Route
- Current Status
- Next Installation
- Dwell Days
""")

    st.dataframe(
        coil_df.head(20),
        use_container_width=True
    )

# ---------------------------------------------------------

with st.expander("INVENTORY_SNAPSHOT.xlsx"):

    st.markdown("""
### Purpose
Inventory snapshot.

### Grain
One row = One Process per Day

### Used By
Inventory Agent
Correlation Agent
""")

    st.dataframe(
        inventory_df.head(20),
        use_container_width=True
    )

# ---------------------------------------------------------

with st.expander("MANUFACTURING_EVENTS.xlsx"):

    st.markdown("""
### Purpose
Manufacturing Events

### Grain
One row = One Event

### Used By
Event Agent
Correlation Agent
""")

    st.dataframe(
        events_df.head(20),
        use_container_width=True
    )

# ---------------------------------------------------------

with st.expander("KPI_METADATA.xlsx"):

    st.markdown("""
### Purpose
Business KPI definitions

### Grain
One row = One KPI

### Used By
Future Metadata Driven Copilot
""")

    st.dataframe(
        kpi_df,
        use_container_width=True
    )

# ---------------------------------------------------------

with st.expander("KPI_RELATIONSHIPS.xlsx"):

    st.markdown("""
### Purpose
Relationship between KPIs

### Grain
One row = One KPI Relationship

### Used By
Correlation Agent
""")

    st.dataframe(
        relationship_df,
        use_container_width=True
    )

# ---------------------------------------------------------

with st.expander("INVESTIGATION_PLAYBOOK.xlsx"):

    st.markdown("""
### Purpose
Executive Investigation Rules

### Grain
One row = One Investigation Scenario

### Used By
Planner Agent
""")

    st.dataframe(
        playbook_df,
        use_container_width=True
    )
