
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# BANKING RISK INTELLIGENCE | EXECUTIVE DASHBOARD
# =========================================================

st.set_page_config(
    page_title="Banking Risk Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- PREMIUM COLOR PALETTE ----------------

BG = "#101923"
PANEL = "#1B2733"
CARD = "#222F3C"
GOLD = "#C8B68A"
SAGE = "#A5B9A8"
IVORY = "#F0EEE8"
MUTED = "#A5AFBA"
BORDER = "#354352"
GRID = "#2C3946"
SILVER = "#C5CDD5"

# ---------------- GLOBAL CSS ----------------

st.markdown(f"""
<style>
.stApp {{
    background-color: {BG};
    color: {IVORY};
}}

[data-testid="stHeader"] {{
    background: transparent;
}}

[data-testid="stSidebar"] {{
    background-color: {PANEL};
    border-right: 1px solid {BORDER};
}}

[data-testid="stSidebar"] * {{
    color: {IVORY};
}}

h1, h2, h3, h4 {{
    color: {IVORY} !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px;
}}

p, label {{
    color: {IVORY};
}}

[data-testid="stMetric"] {{
    background: linear-gradient(145deg, {CARD}, {PANEL});
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px;
    min-height: 125px;
}}

[data-testid="stMetricLabel"] p {{
    color: {MUTED} !important;
    font-size: 0.88rem !important;
}}

[data-testid="stMetricValue"] {{
    color: {GOLD} !important;
    font-weight: 650 !important;
}}

div[data-testid="stPlotlyChart"] {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 8px;
}}

.stButton > button,
.stDownloadButton > button {{
    background-color: {GOLD};
    color: {BG};
    border: 1px solid {GOLD};
    border-radius: 8px;
    font-weight: 600;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background-color: {IVORY};
    color: {BG};
    border-color: {IVORY};
}}

hr {{
    border-color: {BORDER};
}}

[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

div[data-testid="stAlert"] {{
    border-radius: 10px;
}}

#MainMenu, footer {{
    visibility: hidden;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    data = pd.read_csv("cleaned_credit_risk_dataset.csv")

    required_columns = [
        "loan_status",
        "loan_grade",
        "loan_intent",
        "person_home_ownership",
        "person_income",
        "loan_amnt",
        "loan_int_rate",
        "person_age",
        "person_emp_length",
        "loan_percent_income",
        "cb_person_cred_hist_length"
    ]

    missing = [col for col in required_columns if col not in data.columns]

    if missing:
        raise ValueError(
            "Dataset is missing these columns: " + ", ".join(missing)
        )

    data = data.dropna(subset=["loan_status"]).copy()
    data["loan_status"] = pd.to_numeric(
        data["loan_status"], errors="coerce"
    )
    data = data.dropna(subset=["loan_status"])

    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Dataset not found. Place cleaned_credit_risk_dataset.csv "
        "in the same folder as dashboard.py."
    )
    st.stop()
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()

# ---------------- EXECUTIVE HEADER ----------------

st.markdown(f"""
<div style="
    display:flex;
    align-items:center;
    gap:18px;
    padding:10px 0 22px 0;
    border-bottom:1px solid {BORDER};
    margin-bottom:22px;
">
    <div style="
        width:62px;
        height:62px;
        min-width:62px;
        display:flex;
        align-items:center;
        justify-content:center;
        background:{PANEL};
        border:1px solid {GOLD};
        border-radius:12px;
    ">
        <svg width="38" height="38" viewBox="0 0 48 48"
             fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 17 L24 6 L43 17 Z"
                  stroke="{GOLD}" stroke-width="1.8"
                  stroke-linejoin="round"/>
            <path d="M8 21 H40 M8 39 H40 M5 43 H43"
                  stroke="{IVORY}" stroke-width="1.8"
                  stroke-linecap="round"/>
            <path d="M12 22 V38 M20 22 V38 M28 22 V38 M36 22 V38"
                  stroke="{SAGE}" stroke-width="2.2"
                  stroke-linecap="round"/>
        </svg>
    </div>
    <div>
        <div style="
            color:{IVORY};
            font-size:28px;
            font-weight:650;
            letter-spacing:0.2px;
        ">Banking Risk Intelligence</div>
        <div style="
            color:{MUTED};
            font-size:11px;
            letter-spacing:2px;
            margin-top:7px;
        ">CREDIT RISK  /  PORTFOLIO ANALYTICS</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "Monitor loan portfolio patterns, observed repayment outcomes, "
    "and credit exposure through an interactive analytical workspace."
)

# ---------------- SIDEBAR ----------------

st.sidebar.markdown(
    f"<h2 style='color:{GOLD};'>Analysis Controls</h2>",
    unsafe_allow_html=True
)
st.sidebar.caption("Adjust filters to explore the portfolio.")

grades = sorted(df["loan_grade"].dropna().unique().tolist())
purposes = sorted(df["loan_intent"].dropna().unique().tolist())
home_types = sorted(
    df["person_home_ownership"].dropna().unique().tolist()
)

selected_grades = st.sidebar.multiselect(
    "Loan Grade",
    options=grades,
    default=grades
)

selected_purposes = st.sidebar.multiselect(
    "Loan Purpose",
    options=purposes,
    default=purposes
)

selected_home = st.sidebar.multiselect(
    "Home Ownership",
    options=home_types,
    default=home_types
)

income_min = int(df["person_income"].min())
income_max = int(df["person_income"].max())

if income_min < income_max:
    income_range = st.sidebar.slider(
        "Annual Income ($)",
        min_value=income_min,
        max_value=income_max,
        value=(income_min, income_max),
        step=max(1, (income_max - income_min) // 100)
    )
else:
    income_range = (income_min, income_max)

# ---------------- FILTER RECORDS ----------------

filtered = df[
    df["loan_grade"].isin(selected_grades)
    & df["loan_intent"].isin(selected_purposes)
    & df["person_home_ownership"].isin(selected_home)
    & df["person_income"].between(
        income_range[0], income_range[1]
    )
].copy()

if filtered.empty:
    st.warning("No records match these filters. Adjust your selections.")
    st.stop()

# ---------------- KEY PERFORMANCE INDICATORS ----------------

total_loans = len(filtered)
average_loan = filtered["loan_amnt"].mean()
average_interest = filtered["loan_int_rate"].mean()
status_one_rate = filtered["loan_status"].mean() * 100

k1, k2, k3, k4 = st.columns(4)

k1.metric("LOANS ANALYZED", f"{total_loans:,}")
k2.metric("STATUS 1 RATE", f"{status_one_rate:.2f}%")
k3.metric("AVERAGE LOAN", f"${average_loan:,.0f}")
k4.metric("AVERAGE INTEREST", f"{average_interest:.2f}%")

st.caption(
    "Status 1 Rate is the share of records coded 1. Confirm the dataset "
    "documentation before interpreting this as a default rate."
)

st.divider()

# ---------------- PLOTLY CHART THEME ----------------

def style_chart(fig, height=370):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(
            family="Arial",
            color=IVORY,
            size=12
        ),
        title_font=dict(
            color=IVORY,
            size=16
        ),
        margin=dict(l=25, r=25, t=55, b=35),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=IVORY)
        ),
        xaxis=dict(
            gridcolor=GRID,
            zerolinecolor=GRID,
            linecolor=BORDER
        ),
        yaxis=dict(
            gridcolor=GRID,
            zerolinecolor=GRID,
            linecolor=BORDER
        )
    )
    return fig

# ---------------- CHART 1: LOAN GRADE ----------------

left, right = st.columns(2)

with left:
    st.subheader("Portfolio by Loan Grade")

    grade_counts = (
        filtered.groupby("loan_grade")
        .size()
        .reset_index(name="Loan Count")
        .sort_values("loan_grade")
    )

    fig_grade = px.bar(
        grade_counts,
        x="loan_grade",
        y="Loan Count",
        text="Loan Count",
        color_discrete_sequence=[GOLD],
        labels={
            "loan_grade": "Loan Grade",
            "Loan Count": "Number of Loans"
        }
    )

    fig_grade.update_traces(
        textposition="outside",
        textfont=dict(color=IVORY),
        cliponaxis=False
    )

    fig_grade = style_chart(fig_grade)
    st.plotly_chart(fig_grade, use_container_width=True)

# ---------------- CHART 2: STATUS 1 RATE BY PURPOSE ----------------

with right:
    st.subheader("Observed Status 1 Rate by Purpose")

    purpose_rates = (
        filtered.groupby("loan_intent")
        .agg(
            status_rate=("loan_status", "mean"),
            loan_count=("loan_status", "size")
        )
        .reset_index()
    )

    purpose_rates["Status 1 Rate (%)"] = (
        purpose_rates["status_rate"] * 100
    ).round(2)

    fig_purpose = px.bar(
        purpose_rates,
        x="loan_intent",
        y="Status 1 Rate (%)",
        text="Status 1 Rate (%)",
        hover_data={"loan_count": True},
        color_discrete_sequence=[SAGE],
        labels={
            "loan_intent": "Loan Purpose",
            "loan_count": "Loan Count"
        }
    )

    fig_purpose.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        textfont=dict(color=IVORY),
        cliponaxis=False
    )

    fig_purpose = style_chart(fig_purpose)
    fig_purpose.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig_purpose, use_container_width=True)

# ---------------- CHART 3: LOAN AMOUNTS ----------------

left, right = st.columns(2)

with left:
    st.subheader("Loan Amount Distribution")

    fig_amount = px.histogram(
        filtered,
        x="loan_amnt",
        nbins=30,
        color_discrete_sequence=[SILVER],
        labels={
            "loan_amnt": "Loan Amount ($)",
            "count": "Number of Loans"
        }
    )

    fig_amount = style_chart(fig_amount)
    st.plotly_chart(fig_amount, use_container_width=True)

# ---------------- CHART 4: INTEREST BY GRADE ----------------

with right:
    st.subheader("Interest Rate by Loan Grade")

    fig_interest = px.box(
        filtered,
        x="loan_grade",
        y="loan_int_rate",
        color_discrete_sequence=[GOLD],
        points=False,
        labels={
            "loan_grade": "Loan Grade",
            "loan_int_rate": "Interest Rate (%)"
        }
    )

    fig_interest = style_chart(fig_interest)
    st.plotly_chart(fig_interest, use_container_width=True)

# ---------------- CHART 5: HOME OWNERSHIP ----------------

st.subheader("Portfolio Distribution by Home Ownership")

home_counts = (
    filtered.groupby("person_home_ownership")
    .size()
    .reset_index(name="Loan Count")
    .sort_values("Loan Count", ascending=False)
)

fig_home = px.bar(
    home_counts,
    x="person_home_ownership",
    y="Loan Count",
    text="Loan Count",
    color_discrete_sequence=[SAGE],
    labels={
        "person_home_ownership": "Home Ownership",
        "Loan Count": "Number of Loans"
    }
)

fig_home.update_traces(
    textposition="outside",
    textfont=dict(color=IVORY),
    cliponaxis=False
)

fig_home = style_chart(fig_home, height=330)
st.plotly_chart(fig_home, use_container_width=True)

# ---------------- INSIGHTS ----------------

st.divider()
st.markdown("## Portfolio Insights")

grade_rates = (
    filtered.groupby("loan_grade")["loan_status"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

purpose_summary = (
    filtered.groupby("loan_intent")["loan_status"]
    .agg(["mean", "count"])
)

insight1, insight2 = st.columns(2)

with insight1:
    st.markdown("### Grade Overview")

    if not grade_rates.empty:
        top_grade = grade_rates.index[0]
        top_rate = grade_rates.iloc[0]

        st.markdown(
            f"Highest observed Status 1 rate among grades: "
            f"**{top_grade} — {top_rate:.2f}%**."
        )
    else:
        st.write("No grade data available.")

with insight2:
    st.markdown("### Purpose Overview")

    if not purpose_summary.empty:
        top_purpose = purpose_summary["mean"].idxmax()
        top_rate = purpose_summary.loc[top_purpose, "mean"] * 100
        top_count = int(purpose_summary.loc[top_purpose, "count"])

        st.markdown(
            f"Highest observed Status 1 rate by purpose: "
            f"**{top_purpose.replace('_', ' ').title()} — "
            f"{top_rate:.2f}%** across {top_count:,} records."
        )
    else:
        st.write("No purpose data available.")

st.info(
    "These are descriptive patterns, not proof of causation or a validated "
    "prediction model. Lending decisions should consider verified repayment "
    "capacity, relevant financial evidence, fairness testing, and human review."
)

# ---------------- DATA TABLE ----------------

with st.expander("Explore Filtered Loan Records"):
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

# ---------------- DOWNLOAD ----------------

st.download_button(
    label="Download Filtered Loan Records",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_loan_risk_data.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------

st.markdown(f"""
<div style="
    border-top:1px solid {BORDER};
    padding-top:16px;
    margin-top:25px;
    color:{MUTED};
    font-size:11px;
    letter-spacing:1px;
    text-align:center;
">
    BANKING RISK INTELLIGENCE &nbsp; | &nbsp; CREDIT PORTFOLIO ANALYTICS
</div>
""", unsafe_allow_html=True)
