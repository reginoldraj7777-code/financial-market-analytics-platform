from __future__ import annotations

import html
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dashboard_utils import (
    data_quality_checks,
    entity_period_summary,
    event_investigation_brief,
    event_severity_frame,
    file_sha256,
    latest_file_timestamp,
    market_decision_brief,
    quality_score,
    risk_driver_breakdown,
    safe_readonly_sql,
    telemetry_incident_brief,
    telemetry_service_summary,
)
from src.gtm_demo import (
    deterministic_stakeholder_brief,
    latest_region_summary,
    save_synthetic_gtm_data,
)
from src.snowflake_adapter import (
    connection_readiness,
    run_readonly_query,
    safe_connection_summary,
    test_connection,
    upload_demo_dataframe,
)

st.set_page_config(
    page_title="Time-Series Analytics & AI Adoption Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
STOCK_PATH = OUTPUT_DIR / "processed_stock_metrics.csv"
FALLBACK_STOCK_PATH = OUTPUT_DIR / "processed_data.csv"
TELEMETRY_PATH = OUTPUT_DIR / "simulated_system_telemetry.csv"
STREAM_PATH = OUTPUT_DIR / "event_stream_log.csv"
DB_PATH = OUTPUT_DIR / "analytics_pipeline.db"
REPORT_PATH = OUTPUT_DIR / "automated_summary_report.md"
QUALITY_PATH = OUTPUT_DIR / "data_quality_report.md"
SQL_PATH = OUTPUT_DIR / "sql_analysis_queries.sql"
RUN_LOG_PATH = OUTPUT_DIR / "pipeline_run_log.json"
VERIFICATION_PATH = OUTPUT_DIR / "verification_summary.json"
AI_LOG_PATH = ROOT / "docs" / "ai_assistance_log.json"
AI_EVIDENCE_PATH = ROOT / "docs" / "AI_ASSISTED_DEVELOPMENT_EVIDENCE.md"
AI_PLAYBOOK_PATH = ROOT / "docs" / "AI_ADOPTION_PLAYBOOK.md"
GTM_PATH = OUTPUT_DIR / "synthetic_gtm_metrics.csv"
SNOWFLAKE_SCHEMA_PATH = ROOT / "sql" / "snowflake_gtm_schema.sql"
SNOWFLAKE_ANALYSIS_PATH = ROOT / "sql" / "snowflake_gtm_analysis.sql"
CURSOR_RULE_PATH = ROOT / ".cursor" / "rules" / "analytics-quality.mdc"
CURSOR_WORKFLOW_PATH = ROOT / "docs" / "CURSOR_WORKFLOW.md"

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F5F7FA"),
    margin=dict(l=20, r=20, t=55, b=20),
    hoverlabel=dict(bgcolor="#171B23"),
)

CSS = """
<style>
.block-container {padding-top: 1.85rem; padding-bottom: 1.8rem; max-width: 1500px;}
[data-testid="stSidebar"] {border-right: 1px solid rgba(255,255,255,.08);}
[data-testid="stAppDeployButton"] {display:none;}
#MainMenu {visibility:visible;}
footer {visibility:hidden;}
[data-testid="stMetric"] {background: linear-gradient(145deg, rgba(255,255,255,.045), rgba(255,255,255,.015)); border: 1px solid rgba(255,255,255,.10); padding: .75rem .8rem; border-radius: 13px;}
[data-testid="stMetricLabel"] {font-weight: 700;}
[data-testid="stMetricValue"] {font-size:1.62rem;}
button[data-baseweb="tab"] {font-size:.88rem; padding-left:.7rem; padding-right:.7rem;}
.platform-header {position:relative; z-index:2; overflow:visible; border:1px solid rgba(255,255,255,.10); border-radius:18px; padding:1.35rem 1.4rem 1.25rem; background:linear-gradient(135deg, rgba(238,0,0,.10), rgba(23,27,35,.78) 42%, rgba(41,181,232,.055)); box-shadow:0 14px 34px rgba(0,0,0,.20); margin-top:.15rem; margin-bottom:1rem;}
.header-main {display:flex; align-items:center; gap:1rem; overflow:visible;}
.header-icon {display:flex; align-items:center; justify-content:center; width:3.4rem; height:3.4rem; flex:0 0 3.4rem; border-radius:14px; background:linear-gradient(145deg, rgba(238,0,0,.20), rgba(41,181,232,.16)); border:1px solid rgba(255,255,255,.13); font-size:1.8rem;}
.header-kicker {display:inline-block; font-size:.72rem; letter-spacing:.13em; text-transform:uppercase; color:#FF7B7B; font-weight:800; margin:0 0 .32rem 0; padding-top:.04rem;}
.header-title {font-size:2.18rem; line-height:1.12; margin:0; letter-spacing:-.02em;}
.header-subtitle {font-size:1rem; color:#C7CDD8; margin:.42rem 0 0 0; line-height:1.45;}
.header-meta {display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.65rem; margin-top:1rem;}
.meta-card {border:1px solid rgba(255,255,255,.09); border-radius:11px; background:rgba(255,255,255,.028); padding:.62rem .75rem;}
.meta-label {display:block; color:#8E98A9; font-size:.68rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; margin-bottom:.14rem;}
.meta-value {font-size:.86rem; font-weight:700; color:#F3F5F8;}
.hero {border: 1px solid rgba(238,0,0,.42); border-radius: 18px; padding: 1.15rem 1.3rem; background: linear-gradient(135deg, rgba(238,0,0,.13), rgba(23,27,35,.55)); box-shadow: 0 12px 32px rgba(0,0,0,.18);}
.hero-blue {border: 1px solid rgba(41,181,232,.42); border-radius: 18px; padding: 1.15rem 1.3rem; background: linear-gradient(135deg, rgba(41,181,232,.13), rgba(23,27,35,.55));}
.hero-purple {border: 1px solid rgba(167,139,250,.42); border-radius: 18px; padding: 1.15rem 1.3rem; background: linear-gradient(135deg, rgba(167,139,250,.12), rgba(23,27,35,.55));}
.badge {display:inline-block; border:1px solid rgba(238,0,0,.65); color:#ff6b6b; border-radius:999px; padding:.18rem .58rem; margin-right:.35rem; font-size:.75rem; font-weight:800; letter-spacing:.02em;}
.badge-blue {display:inline-block; border:1px solid rgba(41,181,232,.65); color:#63d3ff; border-radius:999px; padding:.18rem .58rem; margin-right:.35rem; font-size:.75rem; font-weight:800;}
.badge-green {display:inline-block; border:1px solid rgba(34,197,94,.62); color:#57e389; border-radius:999px; padding:.18rem .58rem; margin-right:.35rem; font-size:.75rem; font-weight:800;}
.card {border:1px solid rgba(255,255,255,.10); border-radius:14px; padding:.9rem 1rem; background:rgba(255,255,255,.035); min-height:110px;}
.card-tight {border:1px solid rgba(255,255,255,.10); border-radius:14px; padding:.75rem .9rem; background:rgba(255,255,255,.032);}
.summary-card {border:1px solid rgba(255,255,255,.10); border-radius:14px; padding:.9rem 1rem; background:linear-gradient(145deg, rgba(255,255,255,.042), rgba(255,255,255,.018)); min-height:112px;}
.summary-label {display:block; color:#8E98A9; font-size:.72rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; margin-bottom:.35rem;}
.summary-text {font-size:.96rem; line-height:1.5; color:#E9EDF3;}
.step {border-top:3px solid #EE0000; border-radius:12px; padding:.78rem .85rem; background:rgba(255,255,255,.035); min-height:118px;}
.step-blue {border-top:3px solid #29B5E8; border-radius:12px; padding:.78rem .85rem; background:rgba(255,255,255,.035); min-height:118px;}
.muted {font-size:.9rem; color:#A9B1BF;}
.callout {border-left:4px solid #EE0000; padding:.78rem .95rem; background:rgba(238,0,0,.075); border-radius:8px;}
.callout-blue {border-left:4px solid #29B5E8; padding:.78rem .95rem; background:rgba(41,181,232,.075); border-radius:8px;}
.callout-green {border-left:4px solid #22C55E; padding:.78rem .95rem; background:rgba(34,197,94,.075); border-radius:8px;}
.callout-amber {border-left:4px solid #F59E0B; padding:.78rem .95rem; background:rgba(245,158,11,.075); border-radius:8px;}
.small {font-size:.85rem;}
.prompt-box {white-space:pre-wrap; overflow-wrap:anywhere; font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:.86rem; line-height:1.45; border:1px solid rgba(255,255,255,.10); border-radius:12px; padding:.85rem 1rem; background:rgba(255,255,255,.035);}
.ownership {border-left:3px solid #29B5E8; border-radius:10px; padding:.72rem .82rem; background:rgba(41,181,232,.055); min-height:105px;}
hr {border-color:rgba(255,255,255,.08);}
@media (max-width: 900px) {.header-meta {grid-template-columns:1fr;} .header-title {font-size:1.72rem;} .header-main {align-items:flex-start;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stock_file = STOCK_PATH if STOCK_PATH.exists() else FALLBACK_STOCK_PATH
    if not stock_file.exists():
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    stock = pd.read_csv(stock_file)
    stock["Date"] = pd.to_datetime(stock["Date"])
    for col in ["Return_Anomaly", "Volatility_Spike", "High_Volume_Event"]:
        if col in stock and stock[col].dtype != bool:
            stock[col] = stock[col].astype(str).str.lower().map({"true": True, "false": False, "1": True, "0": False}).fillna(False)

    telemetry = pd.read_csv(TELEMETRY_PATH) if TELEMETRY_PATH.exists() else pd.DataFrame()
    if not telemetry.empty:
        telemetry["Timestamp"] = pd.to_datetime(telemetry["Timestamp"])
        if telemetry["Telemetry_Anomaly"].dtype != bool:
            telemetry["Telemetry_Anomaly"] = telemetry["Telemetry_Anomaly"].astype(str).str.lower().map({"true": True, "false": False, "1": True, "0": False}).fillna(False)

    stream = pd.read_csv(STREAM_PATH) if STREAM_PATH.exists() else pd.DataFrame()
    return stock, telemetry, stream


@st.cache_data(show_spinner=False)
def load_gtm_data() -> pd.DataFrame:
    if not GTM_PATH.exists():
        save_synthetic_gtm_data(GTM_PATH)
    gtm = pd.read_csv(GTM_PATH)
    gtm["Week_Start"] = pd.to_datetime(gtm["Week_Start"])
    if "Requires_Review" in gtm and gtm["Requires_Review"].dtype != bool:
        gtm["Requires_Review"] = gtm["Requires_Review"].astype(str).str.lower().map({"true": True, "false": False, "1": True, "0": False}).fillna(False)
    return gtm


@st.cache_data(show_spinner=False)
def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def run_local_query(sql: str) -> pd.DataFrame:
    validated = safe_readonly_sql(sql)
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(validated, conn)


def pct(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:.{digits}f}%"


def eur_m(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"€{float(value) / 1_000_000:.{digits}f}M"


def format_mb(path: Path) -> str:
    if not path.exists():
        return "Missing"
    size = path.stat().st_size
    return f"{size / 1_048_576:.2f} MB" if size >= 1_048_576 else f"{size / 1024:.1f} KB"


def polish(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)")
    return fig


def render_step(number: int, title: str, desc: str, blue: bool = False) -> str:
    klass = "step-blue" if blue else "step"
    return f'<div class="{klass}"><b>{number}. {title}</b><br><span class="muted">{desc}</span></div>'


def render_checklist(items: list[str], style: str = "green") -> None:
    klass = {"green": "callout-green", "amber": "callout-amber", "blue": "callout-blue"}.get(style, "callout")
    content = "".join(f"<div>✅ {item}</div>" for item in items)
    st.markdown(f'<div class="{klass}">{content}</div>', unsafe_allow_html=True)


def render_prompt(text: str) -> None:
    st.markdown(f'<div class="prompt-box">{html.escape(text)}</div>', unsafe_allow_html=True)


def compact_trend_label(value: object) -> str:
    label = str(value).strip().lower()
    if "up" in label:
        return "Upward ↑"
    if "down" in label:
        return "Downward ↓"
    return "Neutral →"


stock_df, telemetry_df, stream_df = load_data()
gtm_df = load_gtm_data()
run_log = load_json(RUN_LOG_PATH)
verification = load_json(VERIFICATION_PATH)
ai_evidence = load_json(AI_LOG_PATH)

if stock_df.empty:
    st.error("Processed data was not found. Run the pipeline before opening the dashboard.")
    st.code("python src/main.py\npython -m streamlit run app.py", language="bash")
    st.stop()

# ---------- GLOBAL CONTROLS ----------
all_symbols = sorted(stock_df["Symbol"].unique())
default_symbol = all_symbols.index("TSLA") if "TSLA" in all_symbols else 0
selected_symbol = st.sidebar.selectbox("Primary entity", all_symbols, index=default_symbol)
min_date = stock_df["Date"].min().date()
max_date = stock_df["Date"].max().date()
selected_dates = st.sidebar.date_input("Analysis window", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    date_start, date_end = selected_dates
else:
    date_start, date_end = min_date, max_date
show_advanced = st.sidebar.toggle("Technical appendix", value=False)

window_df = stock_df[(stock_df["Date"].dt.date >= date_start) & (stock_df["Date"].dt.date <= date_end)].copy()
stock = window_df[window_df["Symbol"] == selected_symbol].sort_values("Date").copy()
if len(stock) < 2:
    st.warning("The selected date range is too small. Expand the analysis window.")
    st.stop()
latest = stock.dropna(subset=["Close"]).iloc[-1]
previous = stock.dropna(subset=["Close"]).iloc[-2]

st.sidebar.markdown("### Data scope")
st.sidebar.markdown("<span class='badge-green'>PUBLIC + SYNTHETIC</span>", unsafe_allow_html=True)
st.sidebar.caption("Public market data and synthetic GTM / operational data only. No company, customer, or confidential data.")
st.sidebar.markdown("### Technology")
st.sidebar.write("Python · SQL · Streamlit · Snowflake-ready architecture · Cursor rules · Human validation")

# ---------- HEADER ----------
st.markdown(
    """
    <div class="platform-header">
      <div class="header-main">
        <div class="header-icon">📊</div>
        <div>
          <div class="header-kicker">Analytics platform</div>
          <h1 class="header-title">Time-Series Analytics &amp; AI Adoption Platform</h1>
          <p class="header-subtitle">Validated analytics, explainable investigations, reusable SQL, and governed AI workflows.</p>
        </div>
      </div>
      <div class="header-meta">
        <div class="meta-card"><span class="meta-label">Data</span><span class="meta-value">Public market + synthetic GTM</span></div>
        <div class="meta-card"><span class="meta-label">AI control</span><span class="meta-value">Human-reviewed and auditable</span></div>
        <div class="meta-card"><span class="meta-label">Warehouse</span><span class="meta-value">Snowflake-ready · local execution</span></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

TABS = st.tabs(
    [
        "1 Overview",
        "2 Trends",
        "3 Investigation",
        "4 SQL & Snowflake",
        "5 Reliability",
        "6 Operations",
        "7 AI Evidence",
        "8 GTM Studio",
    ]
)

# =====================================================================
# 1. EXECUTIVE COMMAND CENTER
# =====================================================================
with TABS[0]:
    st.subheader("Executive overview")
    overview_left, overview_right = st.columns(2)
    overview_left.markdown(
        """
        <div class="summary-card">
          <span class="summary-label">Business need</span>
          <div class="summary-text">Multi-entity time-series data must be validated, compared, and prioritised before teams can act with confidence.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    overview_right.markdown(
        """
        <div class="summary-card">
          <span class="summary-label">Platform response</span>
          <div class="summary-text">The pipeline produces quality-checked metrics, explainable review flags, reusable SQL outputs, and stakeholder-ready summaries.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    checks_overview = data_quality_checks(stock_df)
    events_all = event_severity_frame(window_df)
    latest_artifact = latest_file_timestamp([STOCK_PATH, DB_PATH, REPORT_PATH, GTM_PATH])
    freshness = latest_artifact.strftime("%Y-%m-%d %H:%M") if latest_artifact is not None else "N/A"
    critical_count = int((events_all["Severity"] == "Critical").sum()) if not events_all.empty else 0

    st.write("")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Rows in scope", f"{len(window_df):,}")
    k2.metric("Entities", window_df["Symbol"].nunique())
    k3.metric("Quality gates", f"{int(checks_overview['Passed'].sum())}/{len(checks_overview)}")
    k4.metric("Selected entity", selected_symbol)
    k5.metric("Attention score", f"{latest['Risk_Score']:.1f}/100")
    k6.metric("Critical review flags", critical_count)
    st.caption(f"Heuristic attention score for prioritisation—not a prediction or recommendation. Latest local artifact: {freshness}.")

    brief = market_decision_brief(stock, selected_symbol)
    st.markdown("### Decision brief")
    b1, b2 = st.columns([1.25, 1])
    with b1:
        st.markdown(f'<div class="callout"><b>Headline</b><br>{brief["headline"]}</div>', unsafe_allow_html=True)
        st.markdown("**Verified evidence**")
        for item in brief["evidence"]:
            st.write(f"• {item}")
    with b2:
        st.markdown("**Analyst questions before action**")
        render_checklist(brief["questions"], style="amber")
        st.caption("The platform separates calculated observations from domain interpretation. It does not provide financial advice.")

    st.markdown("### Platform capabilities")
    own_cols = st.columns(4)
    ownership_items = [
        ("Pipeline", "Ingestion, validation, feature engineering, explainable flags, and offline reproducibility"),
        ("Data layer", "CSV / SQLite outputs, read-only SQL workspace, and Snowflake-ready schemas and queries"),
        ("Decision interface", "Interactive analysis, review queues, stakeholder briefs, and monitoring views"),
        ("AI adoption", "Evidence records, human validation gates, Cursor rules, and a synthetic GTM enablement scenario"),
    ]
    for col, (title, desc) in zip(own_cols, ownership_items):
        col.markdown(f'<div class="ownership"><b>{title}</b><br><span class="muted">{desc}</span></div>', unsafe_allow_html=True)

    st.markdown("### Governed architecture")
    architecture = [
        ("Ingest", "Public data with deterministic offline fallback"),
        ("Validate", "Schema, null, key, range, and reproducibility checks"),
        ("Engineer", "Returns, moving averages, volatility, drawdown, risk"),
        ("Detect", "Transparent thresholds and explainable review flags"),
        ("Store", "CSV, SQLite, and optional Snowflake-ready structures"),
        ("Explain", "Decision briefs, SQL reports, and interactive dashboards"),
        ("Govern", "AI evidence, Cursor rules, privacy boundaries, testing"),
    ]
    row1 = st.columns(4)
    row2 = st.columns(3)
    for idx, (title, desc) in enumerate(architecture, start=1):
        target = row1[idx - 1] if idx <= 4 else row2[idx - 5]
        target.markdown(render_step(idx, title, desc), unsafe_allow_html=True)

    st.markdown("### How the analytical pattern transfers to GTM Operations")
    mapping = pd.DataFrame(
        [
            ["Entity", "Stock symbol", "Region, account, product, segment, or sales team"],
            ["Time KPI", "Price / return / volatility", "Pipeline, bookings, win rate, conversion, or activity"],
            ["Review flag", "Return anomaly / volatility spike", "Unexpected KPI drop, surge, stall, or unusual activity"],
            ["Reusable data", "SQLite / CSV / Snowflake-ready", "Governed reporting tables and recurring analysis"],
            ["Stakeholder output", "Executive overview and event queue", "Regional decision brief and action-focused presentation"],
        ],
        columns=["Analytical concept", "Market-data example", "GTM equivalent"],
    )
    st.dataframe(mapping, hide_index=True, use_container_width=True)

    with st.expander(f"Inspect latest processed rows for {selected_symbol}"):
        columns = ["Date", "Symbol", "Close", "Daily_Return", "SMA_20", "SMA_50", "SMA_200", "Volatility_20", "Drawdown", "Trend_Signal", "Risk_Score", "Event_Label"]
        st.dataframe(stock[columns].tail(15), hide_index=True, use_container_width=True)

# =====================================================================
# 2. TREND & DRIVER ANALYSIS
# =====================================================================
with TABS[1]:
    st.subheader(f"Trend and driver analysis — {selected_symbol}")
    drivers = risk_driver_breakdown(stock)
    twenty_day_change = latest["Close"] / stock.iloc[max(0, len(stock) - 21)]["Close"] - 1
    t1, t2, t3, t4, t5 = st.columns(5)
    t1.metric("Latest close", f"{latest['Close']:.2f}", delta=f"{latest['Close'] - previous['Close']:+.2f}")
    t2.metric("20-session movement", pct(twenty_day_change))
    t3.metric("20-day volatility", pct(latest["Volatility_20"]))
    t4.metric("Current drawdown", pct(latest["Drawdown"]))
    t5.metric("Trend", compact_trend_label(latest["Trend_Signal"]))

    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(x=stock["Date"], y=stock["Close"], name="Close", mode="lines", line=dict(width=2.2, color="#F5F7FA")))
    price_fig.add_trace(go.Scatter(x=stock["Date"], y=stock["SMA_20"], name="SMA 20", mode="lines", line=dict(width=1.3, color="#29B5E8")))
    price_fig.add_trace(go.Scatter(x=stock["Date"], y=stock["SMA_50"], name="SMA 50", mode="lines", line=dict(width=1.3, color="#A78BFA")))
    price_fig.add_trace(go.Scatter(x=stock["Date"], y=stock["SMA_200"], name="SMA 200", mode="lines", line=dict(width=1.3, color="#F59E0B")))
    anomalies = stock[stock["Return_Anomaly"]]
    price_fig.add_trace(go.Scatter(x=anomalies["Date"], y=anomalies["Close"], name="Return anomaly", mode="markers", marker=dict(size=9, symbol="x", color="#EE0000")))
    price_fig.update_layout(title="Trend with moving averages and explainable anomaly markers", xaxis_title="Date", yaxis_title="Value", legend_title_text="Series")
    st.plotly_chart(polish(price_fig, 510), use_container_width=True)

    left, right = st.columns([1.35, 1])
    with left:
        comparison_mode = st.radio("Cross-entity comparison", ["Indexed performance", "Attention score", "Volatility"], horizontal=True)
        comparison = window_df.sort_values(["Symbol", "Date"]).copy()
        if comparison_mode == "Indexed performance":
            comparison["Indexed"] = comparison.groupby("Symbol")["Close"].transform(lambda s: 100 * s / s.iloc[0])
            comp_fig = px.line(comparison, x="Date", y="Indexed", color="Symbol", title="Comparable indexed performance (start = 100)")
            comp_fig.update_yaxes(title="Indexed value")
        elif comparison_mode == "Attention score":
            comp_fig = px.line(comparison, x="Date", y="Risk_Score", color="Symbol", title="Attention score comparison")
            comp_fig.update_yaxes(title="Attention score")
        else:
            comp_fig = px.line(comparison, x="Date", y="Volatility_20", color="Symbol", title="Rolling volatility comparison")
            comp_fig.update_yaxes(title="Volatility", tickformat=".1%")
        st.plotly_chart(polish(comp_fig, 430), use_container_width=True)
    with right:
        st.markdown("### Current attention-score components")
        driver_df = pd.DataFrame({"Driver": list(drivers), "Contribution": list(drivers.values())})
        driver_fig = px.bar(driver_df, x="Contribution", y="Driver", orientation="h", text="Contribution", title="Transparent 0–100 prioritisation components")
        driver_fig.update_traces(marker_color=["#29B5E8", "#A78BFA", "#EE0000"], texttemplate="%{text:.1f}")
        driver_fig.update_xaxes(range=[0, 50], title="Score contribution")
        st.plotly_chart(polish(driver_fig, 360), use_container_width=True)
        st.caption("Heuristic attention score = 50% volatility rank + 30% drawdown severity + 20% return-anomaly intensity. It prioritises review; it is not a forecast.")

    st.markdown("### Entity benchmark")
    benchmark = entity_period_summary(window_df)
    display_benchmark = benchmark[["Symbol", "Total_Return", "Volatility_20", "Drawdown", "Risk_Score", "Review_Events"]].copy()
    display_benchmark = display_benchmark.rename(columns={"Total_Return": "Period return", "Volatility_20": "20-day volatility", "Drawdown": "Drawdown", "Risk_Score": "Attention score", "Review_Events": "Review flags"})
    for col in ["Period return", "20-day volatility", "Drawdown"]:
        display_benchmark[col] = display_benchmark[col].map(lambda x: "N/A" if pd.isna(x) else f"{x:+.1%}")
    display_benchmark["Attention score"] = display_benchmark["Attention score"].round(1)
    st.dataframe(
        display_benchmark,
        hide_index=True,
        use_container_width=True,
        column_config={"Attention score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")},
    )

    if show_advanced:
        correlation = window_df.pivot_table(index="Date", columns="Symbol", values="Daily_Return").corr()
        corr_fig = px.imshow(correlation, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r", title="Return correlation across entities")
        st.plotly_chart(polish(corr_fig, 420), use_container_width=True)

# =====================================================================
# 3. EVENTS & INVESTIGATION
# =====================================================================
with TABS[2]:
    st.subheader("Explainable review flags and investigation workflow")
    events = event_severity_frame(window_df)
    multi_rule_count = int((events.get("Event_Count", pd.Series(dtype=float)) >= 2).sum()) if not events.empty else 0
    latest_flag_date = pd.to_datetime(events["Date"]).max().date() if not events.empty else "N/A"
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Review flags", f"{len(events):,}")
    s2.metric("Critical flags", int((events["Severity"] == "Critical").sum()) if not events.empty else 0)
    s3.metric("Multi-rule flags", multi_rule_count)
    s4.metric("Entities affected", events["Symbol"].nunique() if not events.empty else 0)
    s5.metric("Latest flag", str(latest_flag_date))

    f1, f2, f3 = st.columns([1, 1, 1.2])
    severity_options = ["Critical", "High", "Medium", "Low"]
    selected_severities = f1.multiselect("Severity", severity_options, default=severity_options)
    selected_symbols_events = f2.multiselect("Entities", all_symbols, default=[selected_symbol])
    max_queue = f3.slider("Queue size", 5, 30, 12)
    selected_events = events[events["Severity"].isin(selected_severities) & events["Symbol"].isin(selected_symbols_events)].copy()

    st.markdown(
        """
        <div class="callout-blue"><b>Design principle:</b> the platform flags observations for analyst review. It does not claim causality. Every alert shows the triggered rule, supporting metrics, and follow-up questions.</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.2, 1])
    with left:
        event_counts = (
            events.groupby(["Symbol", "Severity"], observed=False).size().reset_index(name="Events") if not events.empty else pd.DataFrame(columns=["Symbol", "Severity", "Events"])
        )
        event_bar = px.bar(event_counts, x="Symbol", y="Events", color="Severity", barmode="stack", category_orders={"Severity": ["Critical", "High", "Medium", "Low"]}, title="Investigation queue by entity and severity", color_discrete_map={"Critical": "#EE0000", "High": "#F97316", "Medium": "#F59E0B", "Low": "#29B5E8"})
        st.plotly_chart(polish(event_bar, 410), use_container_width=True)
    with right:
        rules = pd.DataFrame(
            [
                ["Return anomaly", "|rolling 60-day return z-score| ≥ 2.5", "Unusual movement relative to recent history"],
                ["Volatility spike", "20-day volatility ≥ entity 90th percentile", "Sustained variability requiring review"],
                ["High-volume event", "Volume ≥ entity 90th percentile", "Unusual activity supporting context"],
                ["Priority", "Attention score + multi-rule uplift", "Orders the analyst queue, not a final decision"],
            ],
            columns=["Rule", "Transparent condition", "Interpretation"],
        )
        st.markdown("### Rule catalogue")
        st.dataframe(rules, hide_index=True, use_container_width=True)

    st.markdown("### Prioritised investigation queue")
    queue_columns = ["Date", "Symbol", "Severity", "Investigation_Priority", "Daily_Return", "Volatility_20", "Return_ZScore", "Risk_Score", "Event_Label"]
    queue_display = selected_events[queue_columns].head(max_queue).copy()
    queue_display["Daily_Return"] = queue_display["Daily_Return"].map(lambda value: f"{value:+.2%}")
    queue_display["Volatility_20"] = queue_display["Volatility_20"].map(lambda value: f"{value:.2%}")
    st.dataframe(
        queue_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Investigation_Priority": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f"),
            "Risk_Score": st.column_config.ProgressColumn("Attention score", min_value=0, max_value=100, format="%.1f"),
        },
    )

    if not selected_events.empty:
        event_labels = selected_events.head(max_queue).apply(lambda row: f"{pd.to_datetime(row['Date']).date()} · {row['Symbol']} · {row['Severity']} · {row['Event_Label']} · priority {row['Investigation_Priority']:.1f}", axis=1).tolist()
        chosen_label = st.selectbox("Open an event for explainable review", event_labels)
        chosen_row = selected_events.head(max_queue).iloc[event_labels.index(chosen_label)]
        investigation = event_investigation_brief(chosen_row)
        i1, i2 = st.columns(2)
        with i1:
            st.markdown(f'<div class="callout"><b>{investigation["headline"]}</b></div>', unsafe_allow_html=True)
            st.markdown("**Observed facts**")
            for point in investigation["observed"]:
                st.write(f"• {point}")
        with i2:
            st.markdown("**Questions for the analyst / stakeholder**")
            render_checklist(investigation["questions"], style="amber")

    st.markdown("### Triage outcome framework")
    outcome = pd.DataFrame(
        [
            ["Close", "Data and context confirm no material issue", "Document rationale and retain evidence"],
            ["Monitor", "Signal is real but impact is uncertain", "Set owner, threshold, and review date"],
            ["Investigate", "Multiple metrics support a material change", "Validate scope, segment, timing, and likely drivers"],
            ["Escalate", "High severity, repeated pattern, or business-critical uncertainty", "Engage the appropriate business/domain owner"],
        ],
        columns=["Outcome", "When to use", "Required action"],
    )
    st.dataframe(outcome, hide_index=True, use_container_width=True)

# =====================================================================
# 4. SQL, DATA MODEL & SNOWFLAKE
# =====================================================================
with TABS[3]:
    st.subheader("Reusable SQL layer and Snowflake-ready design")
    local_tab, snow_tab, lineage_tab = st.tabs(["Local SQL workspace", "Snowflake-ready architecture", "Data lineage & exports"])

    with local_tab:
        st.markdown("#### Read-only SQLite analysis workspace")
        templates = {
            "Latest KPI snapshot": """WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Symbol ORDER BY Date DESC) AS rn
    FROM stock_metrics
)
SELECT Symbol, Date, ROUND(Close, 2) AS Close,
       ROUND(Daily_Return, 4) AS Daily_Return,
       ROUND(Volatility_20, 4) AS Volatility_20,
       ROUND(Risk_Score, 1) AS Risk_Score,
       Trend_Signal, Long_Term_Trend
FROM ranked
WHERE rn = 1
ORDER BY Risk_Score DESC;""",
            "Event summary": """SELECT Symbol,
       COUNT(*) AS Rows_Processed,
       SUM(CASE WHEN Return_Anomaly = 1 THEN 1 ELSE 0 END) AS Return_Anomalies,
       SUM(CASE WHEN Volatility_Spike = 1 THEN 1 ELSE 0 END) AS Volatility_Spikes,
       SUM(CASE WHEN High_Volume_Event = 1 THEN 1 ELSE 0 END) AS High_Volume_Events,
       ROUND(AVG(Risk_Score), 1) AS Avg_Risk_Score
FROM stock_metrics
GROUP BY Symbol
ORDER BY Avg_Risk_Score DESC;""",
            "Synthetic GTM latest regional view": """WITH latest_week AS (
    SELECT MAX(Week_Start) AS Week_Start FROM gtm_metrics_synthetic
)
SELECT Region,
       ROUND(SUM(Pipeline_Value_EUR), 2) AS Pipeline_Value_EUR,
       ROUND(SUM(Bookings_EUR), 2) AS Bookings_EUR,
       ROUND(AVG(Win_Rate), 4) AS Win_Rate,
       SUM(CASE WHEN Requires_Review = 1 THEN 1 ELSE 0 END) AS Review_Items
FROM gtm_metrics_synthetic
WHERE Week_Start = (SELECT Week_Start FROM latest_week)
GROUP BY Region
ORDER BY Pipeline_Value_EUR DESC;""",
            "Operational service health": """SELECT Service, Software_Version,
       COUNT(*) AS Rows_Analyzed,
       ROUND(AVG(Signal_Latency_ms), 2) AS Avg_Latency_ms,
       ROUND(AVG(Packet_Loss_Rate), 4) AS Avg_Packet_Loss,
       SUM(Reconnect_Count) AS Reconnects,
       SUM(CASE WHEN Telemetry_Anomaly = 1 THEN 1 ELSE 0 END) AS Anomalies
FROM telemetry_metrics_simulated
GROUP BY Service, Software_Version
ORDER BY Anomalies DESC, Avg_Latency_ms DESC;""",
        }
        chosen_template = st.selectbox("Query template", list(templates), index=2)
        query = st.text_area("SQL (read-only guard enabled)", templates[chosen_template], height=260)
        q1, q2 = st.columns([1, 3])
        run_clicked = q1.button("Run query", use_container_width=True)
        q2.caption("Only one SELECT, WITH, or PRAGMA statement is accepted. Write/DDL tokens are blocked before database access.")
        if run_clicked:
            try:
                result = run_local_query(query)
                st.success(f"Query completed: {len(result):,} rows returned.")
                st.dataframe(result, hide_index=True, use_container_width=True)
                st.download_button("Download query result (CSV)", result.to_csv(index=False).encode("utf-8"), file_name="query_result.csv", mime="text/csv")
            except Exception as exc:
                st.error(f"Query blocked or failed: {exc}")

        if DB_PATH.exists():
            schema_query = "SELECT name AS table_name FROM sqlite_master WHERE type='table' ORDER BY name;"
            tables_df = run_local_query(schema_query)
            st.markdown("#### Available local analytical tables")
            st.dataframe(tables_df, hide_index=True, use_container_width=True)

    with snow_tab:
        readiness = connection_readiness()
        sf1, sf2, sf3, sf4 = st.columns(4)
        sf1.metric("Connector layer", "Implemented")
        sf2.metric("Credential handling", "Environment-only")
        sf3.metric("Default mode", "Local execution")
        sf4.metric("Write actions", "Disabled")
        st.caption("Snowflake-native schema and analytical SQL assets are included with environment-based credential handling. Live connectivity remains optional.")

        left, right = st.columns([1, 1.45])
        with left:
            st.markdown(
                """
                <div class="callout-blue"><b>Operating model</b><br>
                Validated local/synthetic data → governed Snowflake table/view → read-only analytical SQL → dashboard or stakeholder export.<br><br>
                Credentials are accepted only through environment variables. Live writes require explicit user confirmation.</div>
                """,
                unsafe_allow_html=True,
            )
            render_checklist(
                [
                    "Snowflake-native schema and governed view included",
                    "Regional analytical SQL uses reviewed windows and filters",
                    "Credentials are never stored in the repository",
                    "Interactive queries are read-only by default",
                ],
                style="blue",
            )
            with st.expander("Optional live-connection details", expanded=show_advanced):
                st.dataframe(pd.DataFrame(list(safe_connection_summary().items()), columns=["Setting", "Status"]), hide_index=True, use_container_width=True)
                if readiness.missing_fields:
                    st.caption("Configuration fields not supplied in local mode: " + ", ".join(readiness.missing_fields))
                if not readiness.connector_installed:
                    st.code("python -m pip install -r requirements-snowflake.txt", language="bash")
                if st.button("Test live Snowflake connection", disabled=not readiness.live_ready, use_container_width=True):
                    try:
                        st.dataframe(test_connection(), hide_index=True, use_container_width=True)
                        st.success("Live Snowflake connection verified.")
                    except Exception as exc:
                        st.error(f"Connection test failed: {exc}")
        with right:
            sql_tabs = st.tabs(["Schema / governed view", "Regional analytical query", "Optional read-only runner"])
            with sql_tabs[0]:
                st.code(SNOWFLAKE_SCHEMA_PATH.read_text(encoding="utf-8"), language="sql")
            with sql_tabs[1]:
                st.code(SNOWFLAKE_ANALYSIS_PATH.read_text(encoding="utf-8"), language="sql")
            with sql_tabs[2]:
                sf_query = st.text_area(
                    "Snowflake SELECT/WITH query",
                    """SELECT REGION,
       ROUND(SUM(PIPELINE_VALUE_EUR), 2) AS PIPELINE_VALUE_EUR,
       ROUND(AVG(WIN_RATE), 4) AS WIN_RATE,
       COUNT_IF(REQUIRES_REVIEW) AS REVIEW_ITEMS
FROM GTM_METRICS_DEMO
GROUP BY REGION
ORDER BY PIPELINE_VALUE_EUR DESC;""",
                    height=190,
                    key="snowflake_readonly_query",
                )
                if st.button("Run Snowflake read-only query", disabled=not readiness.live_ready):
                    try:
                        st.dataframe(run_readonly_query(sf_query), hide_index=True, use_container_width=True)
                    except Exception as exc:
                        st.error(f"Query failed: {exc}")

    with lineage_tab:
        st.markdown("#### Data lineage")
        lineage_steps = [
            ("Source", "Public market data or deterministic offline fallback"),
            ("Raw validation", "Type conversion, required fields, date/entity keys"),
            ("Feature layer", "Returns, rolling metrics, trend, drawdown, risk"),
            ("Decision layer", "Event labels, priority queue, stakeholder summaries"),
            ("Storage layer", "CSV + SQLite + optional Snowflake table/view"),
            ("Consumption", "Streamlit, SQL exports, reports, onboarding assets"),
        ]
        cols = st.columns(3)
        for idx, (title, desc) in enumerate(lineage_steps, start=1):
            cols[(idx - 1) % 3].markdown(render_step(idx, title, desc, blue=True), unsafe_allow_html=True)

        st.markdown("#### Generated artifacts")
        artifacts = [
            STOCK_PATH,
            TELEMETRY_PATH,
            GTM_PATH,
            DB_PATH,
            REPORT_PATH,
            QUALITY_PATH,
            SQL_PATH,
            RUN_LOG_PATH,
        ]
        artifact_rows = []
        for path in artifacts:
            artifact_rows.append(
                {
                    "Artifact": path.name,
                    "Status": "Ready" if path.exists() else "Missing",
                    "Size": format_mb(path),
                    "SHA-256 prefix": file_sha256(path)[:12] if path.exists() else "N/A",
                    "Purpose": {
                        STOCK_PATH.name: "Validated analytical fact table",
                        TELEMETRY_PATH.name: "Synthetic operational extension",
                        GTM_PATH.name: "Synthetic EMEA GTM decision-support dataset",
                        DB_PATH.name: "Reusable local analytical database",
                        REPORT_PATH.name: "Automated stakeholder report",
                        QUALITY_PATH.name: "Data quality evidence",
                        SQL_PATH.name: "Reusable SQL analysis examples",
                        RUN_LOG_PATH.name: "Pipeline execution metadata",
                    }.get(path.name, "Project artifact"),
                }
            )
        st.dataframe(pd.DataFrame(artifact_rows), hide_index=True, use_container_width=True)
        downloads = st.columns(3)
        if STOCK_PATH.exists():
            downloads[0].download_button("Download processed metrics", STOCK_PATH.read_bytes(), STOCK_PATH.name, "text/csv", use_container_width=True)
        if GTM_PATH.exists():
            downloads[1].download_button("Download synthetic GTM data", GTM_PATH.read_bytes(), GTM_PATH.name, "text/csv", use_container_width=True)
        if REPORT_PATH.exists():
            downloads[2].download_button("Download automated report", REPORT_PATH.read_bytes(), REPORT_PATH.name, "text/markdown", use_container_width=True)

# =====================================================================
# 5. RELIABILITY & GOVERNANCE
# =====================================================================
with TABS[4]:
    st.subheader("Reliability, quality gates, and reproducibility")
    checks = data_quality_checks(stock_df)
    q_score = quality_score(stock_df)
    v_status = verification.get("status", "Not recorded")
    test_count = verification.get("tests_passed", "N/A")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Implemented quality gates", f"{int(checks['Passed'].sum())}/{len(checks)}")
    r2.metric("Weighted gate score", f"{q_score:.0f}/100")
    r3.metric("Processing batches", len(stream_df) if not stream_df.empty else 0)
    r4.metric("Automated checks", str(test_count))
    r5.metric("Preflight status", str(v_status))
    st.caption("These results cover the implemented deterministic validation checks; they are not a production SLA or complete data-quality framework.")

    st.markdown("### Data quality control panel")
    checks_display = checks.copy()
    checks_display["Status"] = checks_display["Passed"].map({True: "✅ Passed", False: "❌ Failed"})
    st.dataframe(checks_display[["Check", "Status", "Detail"]], hide_index=True, use_container_width=True)

    p1, p2 = st.columns([1.25, 1])
    with p1:
        if not stream_df.empty:
            batch_fig = px.line(
                stream_df,
                x="Batch_Number",
                y=["Return_Anomalies", "Volatility_Spikes", "High_Volume_Events"],
                markers=True,
                title="Event counts by simulated processing batch",
            )
            batch_fig.update_yaxes(title="Events")
            st.plotly_chart(polish(batch_fig, 410), use_container_width=True)
            st.dataframe(stream_df.tail(8), hide_index=True, use_container_width=True)
    with p2:
        st.markdown("### Reproducibility controls")
        render_checklist(
            [
                "Deterministic offline fallback when public API access fails",
                "Explicit Python dependencies including optional report dependencies",
                "Version-controlled SQL, Cursor rules, tests, and documentation",
                "Read-only guards for interactive SQL runners",
                "Synthetic data labels and no embedded credentials",
                "Full-pipeline rerun after accepted AI-assisted changes",
            ],
            style="green",
        )
        st.markdown("### Latest run metadata")
        if run_log:
            metadata = {
                "Generated at": run_log.get("generated_at", "N/A"),
                "Stock rows": run_log.get("stock_rows", "N/A"),
                "Symbols": ", ".join(run_log.get("symbols", [])),
                "Telemetry rows": run_log.get("telemetry_rows_simulated", "N/A"),
                "GTM rows": run_log.get("synthetic_gtm_rows", len(gtm_df)),
            }
            st.dataframe(pd.DataFrame(list(metadata.items()), columns=["Field", "Value"]), hide_index=True, use_container_width=True)
        else:
            st.info("Run metadata is not available. Rerun the pipeline.")

    st.markdown("### Verification evidence")
    if verification:
        st.json(verification, expanded=False)
    else:
        st.info("Run the preflight script to generate outputs/verification_summary.json.")

    with st.expander("Inspect generated data-quality report"):
        if QUALITY_PATH.exists():
            st.markdown(QUALITY_PATH.read_text(encoding="utf-8"))
        else:
            st.info("Run the pipeline to generate the report.")

# =====================================================================
# 6. OPERATIONAL MONITORING
# =====================================================================
with TABS[5]:
    st.subheader("Synthetic operational monitoring")
    st.markdown(
        """
        <div class="hero-blue">
        <span class="badge-blue">SYNTHETIC OPERATIONAL DATA</span>
        <span class="badge-blue">TRANSFERABLE PIPELINE</span><br><br>
        <b>Purpose:</b> prove that the architecture is not tied to stock prices. The same entity-time-KPI-alert pattern can monitor services, business activities, sales motions, or other operational processes.<br><br>
        <b>Boundary:</b> the telemetry records are generated locally and do not represent Red Hat systems or production infrastructure.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if telemetry_df.empty:
        st.info("Run the pipeline to generate the synthetic operational dataset.")
    else:
        services = sorted(telemetry_df["Service"].unique())
        versions = sorted(telemetry_df["Software_Version"].unique())
        f1, f2 = st.columns(2)
        selected_services = f1.multiselect("Services", services, default=services)
        selected_versions = f2.multiselect("Software versions", versions, default=versions)
        tele_scope = telemetry_df[telemetry_df["Service"].isin(selected_services) & telemetry_df["Software_Version"].isin(selected_versions)].copy()

        o1, o2, o3, o4, o5 = st.columns(5)
        o1.metric("Observations", f"{len(tele_scope):,}")
        o2.metric("Services", tele_scope["Service"].nunique())
        o3.metric("Devices", tele_scope["Device_ID"].nunique())
        o4.metric("Flagged incidents", int(tele_scope["Telemetry_Anomaly"].sum()))
        o5.metric("P95 latency", f"{tele_scope['Signal_Latency_ms'].quantile(.95):.1f} ms")

        risk_fig = px.line(
            tele_scope.sort_values("Timestamp"),
            x="Timestamp",
            y="Telemetry_Risk_Score",
            color="Service",
            title="Operational attention score over time",
        )
        risk_fig.add_hline(y=90, line_dash="dash", line_color="#EE0000", annotation_text="Synthetic review threshold")
        st.plotly_chart(polish(risk_fig, 470), use_container_width=True)

        service_summary = telemetry_service_summary(tele_scope)
        left, right = st.columns([1.3, 1])
        with left:
            st.markdown("### Service / version health matrix")
            st.dataframe(
                service_summary,
                hide_index=True,
                use_container_width=True,
                column_config={"Avg_Risk": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")},
            )
        with right:
            heat = service_summary.pivot(index="Service", columns="Software_Version", values="Avg_Risk")
            heat_fig = px.imshow(heat, text_auto=".1f", zmin=0, zmax=100, color_continuous_scale="YlOrRd", title="Average attention score by service and version")
            st.plotly_chart(polish(heat_fig, 390), use_container_width=True)

        st.markdown("### Incident review queue")
        incidents = tele_scope[tele_scope["Telemetry_Anomaly"]].sort_values(["Timestamp", "Telemetry_Risk_Score"], ascending=[False, False]).head(30)
        st.dataframe(
            incidents[["Timestamp", "Service", "Software_Version", "Device_ID", "Signal_Latency_ms", "Packet_Loss_Rate", "Reconnect_Count", "Telemetry_Risk_Score"]],
            hide_index=True,
            use_container_width=True,
            column_config={"Telemetry_Risk_Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")},
        )

        selected_service_for_brief = st.selectbox("Generate an operational brief", services)
        op_brief = telemetry_incident_brief(telemetry_df, selected_service_for_brief)
        b1, b2 = st.columns(2)
        with b1:
            st.markdown(f'<div class="callout-blue"><b>Calculated summary</b><br>{op_brief["summary"]}</div>', unsafe_allow_html=True)
        with b2:
            st.markdown("**Investigation questions**")
            render_checklist(op_brief["questions"], style="amber")

        st.markdown("### Transferability map")
        operational_mapping = pd.DataFrame(
            [
                ["Service / device", "Region, sales team, account, product, or process"],
                ["Latency / packet loss / reconnects", "Cycle time, response time, activity, conversion, or pipeline movement"],
                ["Operational attention score", "Attention score for analyst prioritization"],
                ["Incident queue", "Regional KPI review queue"],
                ["Owner validation", "Business stakeholder review and next action"],
            ],
            columns=["Operational concept", "Business / GTM equivalent"],
        )
        st.dataframe(operational_mapping, hide_index=True, use_container_width=True)

# =====================================================================
# 7. AI ASSURANCE & EVIDENCE
# =====================================================================
with TABS[6]:
    st.subheader("AI-use evidence and human validation")
    st.markdown(
        """
        <div class="hero-purple">
        <span class="badge">AUDITABLE</span>
        <span class="badge">HUMAN-VALIDATED</span>
        <span class="badge">REUSABLE</span>
        <span class="badge">PRIVACY-BOUND</span><br><br>
        <b>Operating principle:</b> AI proposes; the human owner reviews, tests, documents, and owns the final analytical or technical decision.<br><br>
        <b>Evidence standard:</b> every showcased AI contribution includes the problem, bounded prompt, suggestion, human decision, verification method, artifact, and impact.
        </div>
        """,
        unsafe_allow_html=True,
    )

    records = ai_evidence.get("records", [])
    verified_records = [record for record in records if record.get("status") == "Verified"]
    validation_checks = sum(len(record.get("verification", [])) for record in records)
    unique_artifacts = {artifact for record in records for artifact in record.get("artifacts", [])}
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("Documented tasks", len(records))
    a2.metric("Verified records", len(verified_records))
    a3.metric("Human checks", validation_checks)
    a4.metric("Referenced artifacts", len(unique_artifacts))
    a5.metric("Embedded secrets", "0")

    st.markdown("### Human-in-the-loop lifecycle")
    flow = [
        ("Define", "Business goal, approved inputs, scope, and constraints"),
        ("Prompt", "Request a bounded proposal and verification plan"),
        ("Review", "Accept, modify, or reject every suggestion"),
        ("Verify", "Run tests, inspect data, recalculate claims, check privacy"),
        ("Document", "Record evidence, impact, limitations, and owner"),
    ]
    flow_cols = st.columns(5)
    for idx, (title, desc) in enumerate(flow, start=1):
        flow_cols[idx - 1].markdown(render_step(idx, title, desc), unsafe_allow_html=True)

    st.markdown("### Evidence explorer")
    if records:
        record_names = [f"{record['id']} · {record['title']}" for record in records]
        selected_record_name = st.selectbox("Evidence record", record_names)
        record = records[record_names.index(selected_record_name)]
        st.caption(f"Tool: {record['tool']} · Date: {record['date']} · Status: {record['status']}")
        e1, e2 = st.columns([1.15, 1])
        with e1:
            st.markdown("**Problem**")
            st.write(record["problem"])
            st.markdown("**Bounded prompt excerpt**")
            st.markdown(f'<div class="callout-blue">{record["prompt_excerpt"]}</div>', unsafe_allow_html=True)
            st.markdown("**AI contribution**")
            for point in record.get("ai_contribution", []):
                st.write(f"• {point}")
        with e2:
            st.markdown("**Human decisions**")
            for point in record.get("human_decisions", []):
                st.write(f"• {point}")
            st.markdown("**Verification gate**")
            render_checklist(record.get("verification", []), style="green")
            st.markdown("**Verified impact**")
            st.success(record["impact"])
        if record.get("code_before") and record.get("code_after"):
            before, after = st.columns(2)
            before.code(record["code_before"], language="text")
            after.code(record["code_after"], language="text")
        st.caption("Evidence artifacts: " + " · ".join(f"`{item}`" for item in record.get("artifacts", [])))
    else:
        st.warning("AI evidence file is missing.")

    if show_advanced:
        st.markdown("### Decision discipline: accept, modify, or reject")
        decision_examples = pd.DataFrame(
            [
                ["Accept", "Add the missing tabulate dependency", "Traceback confirmed the exact optional dependency; full pipeline passed afterward"],
                ["Modify", "Use AI-generated stakeholder language", "Keep structure, replace unsupported causality, and verify every number against source data"],
                ["Reject", "Store credentials in a local config file for convenience", "Violates secret-management and repository-safety rules"],
            ],
            columns=["Decision", "Example", "Reason / control"],
        )
        st.dataframe(decision_examples, hide_index=True, use_container_width=True)

        st.markdown("### AI risk and control matrix")
        risk_matrix = pd.DataFrame(
            [
                ["Unsupported claims / hallucination", "Separate facts from interpretation; require source-grounded evidence and human sign-off"],
                ["Sensitive-data exposure", "Approved non-sensitive inputs only; no secrets; synthetic GTM data"],
                ["Code regression", "Plan before edits, line-by-line diff review, tests, and full-pipeline rerun"],
                ["Incorrect SQL or high query cost", "Read-only defaults, reviewed filters/partitions, bounded test scope, Snowflake query tagging"],
                ["Over-reliance on one tool", "Tool-by-task selection, manual fallback, documented limitations and escalation paths"],
            ],
            columns=["Risk", "Control"],
        )
        st.dataframe(risk_matrix, hide_index=True, use_container_width=True)

    with st.expander("Prompt library and audit appendix", expanded=show_advanced):
        st.markdown("#### Reusable prompt library")
        prompt_library = ai_evidence.get("prompt_library", [])
        if prompt_library:
            prompt_tabs = st.tabs([item["name"] for item in prompt_library])
            for tab, item in zip(prompt_tabs, prompt_library):
                with tab:
                    render_prompt(item["prompt"])
                    st.caption("Bounded, reviewable, and human-owned by design.")

        st.markdown("#### Evidence downloads")
        d1, d2, d3 = st.columns(3)
        if AI_LOG_PATH.exists():
            d1.download_button("Download evidence log", AI_LOG_PATH.read_bytes(), "ai_assistance_log.json", "application/json", use_container_width=True)
        if AI_EVIDENCE_PATH.exists():
            d2.download_button("Download evidence report", AI_EVIDENCE_PATH.read_bytes(), AI_EVIDENCE_PATH.name, "text/markdown", use_container_width=True)
        if AI_PLAYBOOK_PATH.exists():
            d3.download_button("Download adoption playbook", AI_PLAYBOOK_PATH.read_bytes(), AI_PLAYBOOK_PATH.name, "text/markdown", use_container_width=True)
        with st.expander("Evidence integrity details"):
            st.code(file_sha256(AI_LOG_PATH), language="text")
            st.caption("SHA-256 fingerprint of the local evidence log. This supports change detection; it is not a substitute for independent validation.")

# =====================================================================
# 8. GTM AI ADOPTION STUDIO
# =====================================================================
with TABS[7]:
    st.subheader("Synthetic GTM use case — Snowflake + Cursor + governed AI-assisted workflows")
    st.markdown(
        """
        <div class="hero-blue">
        <span class="badge-blue">SYNTHETIC EMEA GTM</span>
        <span class="badge-blue">SNOWFLAKE-READY</span>
        <span class="badge-blue">CURSOR-ASSISTED</span>
        <span class="badge-blue">TEAM ENABLEMENT</span><br><br>
        <b>Purpose:</b> combine regional decision support with governed AI adoption, reusable prompts, onboarding, skill-gap identification, and human verification.<br><br>
        <b>Data boundary:</b> no Red Hat, customer, or confidential data is used or implied. All GTM metrics are deterministic synthetic data.
        </div>
        """,
        unsafe_allow_html=True,
    )

    latest_week = gtm_df["Week_Start"].max()
    latest_rows = gtm_df[gtm_df["Week_Start"] == latest_week]
    latest_summary = latest_region_summary(gtm_df)
    g1, g2, g3, g4, g5, g6 = st.columns(6)
    g1.metric("Synthetic records", f"{len(gtm_df):,}")
    g2.metric("EMEA regions", gtm_df["Region"].nunique())
    g3.metric("Latest pipeline", eur_m(latest_rows["Pipeline_Value_EUR"].sum()))
    g4.metric("Latest bookings", eur_m(latest_rows["Bookings_EUR"].sum()))
    g5.metric("Average win rate", pct(latest_rows["Win_Rate"].mean()))
    g6.metric("Review items", int(latest_rows["Requires_Review"].sum()))

    st.markdown("### Regional decision-support workspace")
    f1, f2, f3 = st.columns([1.2, 1, 1])
    selected_regions = f1.multiselect("Regions", sorted(gtm_df["Region"].unique()), default=sorted(gtm_df["Region"].unique()), key="gtm_regions_final")
    metric_choice = f2.selectbox(
        "KPI",
        ["Pipeline_Value_EUR", "Bookings_EUR", "Win_Rate", "Conversion_Rate", "Activity_Count", "Attention_Score"],
        format_func=lambda value: value.replace("_", " ").title(),
    )
    segment_choice = f3.multiselect("Segments", sorted(gtm_df["Segment"].unique()), default=sorted(gtm_df["Segment"].unique()))
    filtered_gtm = gtm_df[gtm_df["Region"].isin(selected_regions) & gtm_df["Segment"].isin(segment_choice)].copy()
    weekly = (
        filtered_gtm.groupby(["Week_Start", "Region"], as_index=False)
        .agg(
            Pipeline_Value_EUR=("Pipeline_Value_EUR", "sum"),
            Bookings_EUR=("Bookings_EUR", "sum"),
            Win_Rate=("Win_Rate", "mean"),
            Conversion_Rate=("Conversion_Rate", "mean"),
            Activity_Count=("Activity_Count", "sum"),
            Attention_Score=("Attention_Score", "mean"),
        )
    )
    gtm_fig = px.line(weekly, x="Week_Start", y=metric_choice, color="Region", title="Synthetic regional KPI movement", markers=False)
    if metric_choice in {"Win_Rate", "Conversion_Rate"}:
        gtm_fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(polish(gtm_fig, 450), use_container_width=True)

    snap, brief_col = st.columns([1.15, 1])
    with snap:
        st.markdown("#### Latest regional snapshot")
        display_summary = latest_summary.copy()
        display_summary["Pipeline_Value_EUR"] = display_summary["Pipeline_Value_EUR"].map(eur_m)
        display_summary["Bookings_EUR"] = display_summary["Bookings_EUR"].map(eur_m)
        display_summary["Win_Rate"] = display_summary["Win_Rate"].map(lambda x: f"{x:.1%}")
        st.dataframe(display_summary, hide_index=True, use_container_width=True, column_config={"Attention_Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")})
    with brief_col:
        brief_region = st.selectbox("Stakeholder brief region", sorted(gtm_df["Region"].unique()))
        gtm_brief = deterministic_stakeholder_brief(gtm_df, brief_region)
        st.markdown("#### Analyst-validated draft")
        st.info(gtm_brief["summary"])
        st.markdown("**Mandatory human review before use**")
        render_checklist(
            [
                "Match every figure to the validated query output",
                "Confirm period, segment, and regional definitions",
                "Separate observed facts from possible explanations",
                "Add the responsible owner and next decision",
            ],
            style="amber",
        )

    st.markdown("#### Explainable regional review queue")
    review = gtm_df[gtm_df["Requires_Review"]].sort_values(["Week_Start", "Attention_Score"], ascending=[False, False]).head(30).copy()
    review["Pipeline_Change_4W"] = review["Pipeline_Change_4W"].map(lambda x: "N/A" if pd.isna(x) else f"{x:+.1%}")
    review["Win_Rate_Change_4W"] = review["Win_Rate_Change_4W"].map(lambda x: "N/A" if pd.isna(x) else f"{x:+.1%}")
    st.dataframe(
        review[["Week_Start", "Region", "Segment", "Product_Family", "Pipeline_Change_4W", "Win_Rate_Change_4W", "Event_Label", "Event_Driver", "Attention_Score"]],
        hide_index=True,
        use_container_width=True,
        column_config={"Attention_Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f")},
    )

    st.markdown("### AI use-case builder")
    use_cases = {
        "Investigate a regional KPI decline": {
            "tools": "Snowflake + Cursor + Gemini",
            "workflow": "Query governed KPI views in Snowflake → use Cursor to review SQL with repository rules → use Gemini to structure a first draft → analyst validates data, interpretation, and next action.",
            "prompt": "Using only the supplied validated KPI extract, identify the three largest material changes. Separate observed facts, possible interpretations, uncertainty, and analyst follow-up questions. Do not infer causality or invent context.",
            "checks": ["Recalculate KPI deltas", "Check filter and date scope", "Review outliers and missing values", "Remove unsupported causal language", "Confirm action owner"],
            "output": "A structured investigation brief and prioritized analyst questions.",
        },
        "Prepare a weekly executive performance brief": {
            "tools": "Snowflake + Gemini or NotebookLM",
            "workflow": "Run an approved Snowflake summary query → provide validated output and approved reference documents → draft a concise brief → analyst verifies every number and recommendation.",
            "prompt": "Create a concise executive brief from the supplied validated metrics. Use sections: headline, evidence, risks, questions, and next actions. Quote every number exactly and state when evidence is insufficient.",
            "checks": ["Match figures to query output", "Confirm week and regional definitions", "Distinguish fact from interpretation", "Remove sensitive details", "Confirm audience"],
            "output": "A consistent stakeholder-ready first draft with explicit evidence and uncertainty.",
        },
        "Develop and review Snowflake SQL": {
            "tools": "Cursor + Snowflake",
            "workflow": "Give Cursor explicit repository context → request a plan before edits → review the SQL diff → run a read-only validation query → document assumptions and query scope.",
            "prompt": "Review @sql/snowflake_gtm_analysis.sql for Snowflake compatibility, analytical assumptions, window partitions, privacy boundaries, and query cost. Propose the smallest patch and a read-only verification plan. Do not execute SQL or expose credentials.",
            "checks": ["Inspect tables and columns", "Review window partitions", "Test on synthetic data", "Check filters and expected scan", "Approve diff line by line"],
            "output": "A reviewable SQL improvement with explicit validation steps.",
        },
        "Onboard analysts to governed AI-assisted workflows": {
            "tools": "Cursor Rules + NotebookLM + Gemini",
            "workflow": "Encode persistent project rules → publish approved use-case cards → practice with synthetic data → identify skill gaps → provide office hours and escalation paths.",
            "prompt": "Turn this approved workflow into a 15-minute onboarding exercise with the business goal, approved inputs, prompt, human checks, expected output, limitations, and escalation conditions.",
            "checks": ["Approved tools only", "Non-sensitive training data", "Verification steps included", "Assess understanding", "Provide escalation route"],
            "output": "A repeatable enablement exercise rather than one-off prompting tips.",
        },
    }
    chosen_use_case = st.selectbox("Business use case", list(use_cases))
    case = use_cases[chosen_use_case]
    u1, u2 = st.columns([1.15, 1])
    with u1:
        st.markdown(f"**Recommended tools:** {case['tools']}")
        st.markdown("**Team workflow**")
        st.write(case["workflow"])
        st.markdown("**Bounded reusable prompt**")
        render_prompt(case["prompt"])
    with u2:
        st.markdown("**Human verification gate**")
        render_checklist(case["checks"], style="green")
        st.markdown("**Expected output**")
        st.success(case["output"])

    st.markdown("### Team adoption plan: 30–60–90 days")
    plan_cols = st.columns(3)
    adoption_plan = [
        ("First 30 days — Discover", ["Interview analysts and map recurring tasks", "Identify approved tools and data boundaries", "Create a baseline skills / confidence matrix", "Select 2 low-risk, high-frequency use cases"]),
        ("Days 31–60 — Pilot", ["Run onboarding sessions with synthetic data", "Publish bounded prompts and verification checklists", "Hold office hours and collect failure examples", "Measure quality, rework, and adoption signals"]),
        ("Days 61–90 — Scale", ["Standardize approved workflows", "Create champions and escalation paths", "Add governance reviews and reusable templates", "Report outcomes, limitations, and next use cases"]),
    ]
    for col, (title, items) in zip(plan_cols, adoption_plan):
        content = "<br>".join(f"• {item}" for item in items)
        col.markdown(f'<div class="card"><b>{title}</b><br><br><span class="muted">{content}</span></div>', unsafe_allow_html=True)

    if show_advanced:
        st.markdown("### Skill-gap and enablement matrix")
        skill_matrix = pd.DataFrame(
            [
                ["Prompt framing", "Can state goal but omits constraints", "Use-case card + good/bad prompt comparison", "Produces a bounded prompt with verification steps"],
                ["Source grounding", "May mix source facts with assumptions", "NotebookLM / reference-only exercise", "Every claim is traceable or marked uncertain"],
                ["Cursor workflow", "Accepts edits without review", "Plan → diff → test exercise", "Explains accepted, modified, and rejected changes"],
                ["Snowflake analysis", "Writes queries but misses scope/cost checks", "Reviewed SQL template + read-only validation", "Uses correct filters, windows, and assumptions"],
                ["Stakeholder communication", "Reports metrics without decision context", "Headline/evidence/risk/action template", "Delivers a concise decision-ready brief"],
            ],
            columns=["Capability", "Typical gap", "Enablement activity", "Evidence of proficiency"],
        )
        st.dataframe(skill_matrix, hide_index=True, use_container_width=True)

        st.markdown("### Illustrative capacity scenario — not a measured project result")
        c1, c2, c3 = st.columns(3)
        analysts = c1.slider("Analysts in pilot", 2, 20, 6)
        recurring_tasks = c2.slider("Recurring tasks per analyst / month", 2, 30, 10)
        minutes_saved = c3.slider("Hypothetical minutes saved per task", 2, 30, 8)
        monthly_hours = analysts * recurring_tasks * minutes_saved / 60
        st.info(f"Illustrative capacity released: **{monthly_hours:.1f} hours/month**. This is a scenario for prioritization, not a claimed or measured outcome. A real pilot would measure baseline time, output quality, rework, and adoption before reporting impact.")

    st.markdown("### Snowflake + Cursor operating model")
    model_cols = st.columns(5)
    model_steps = [
        ("1. Governed data", "Validated Snowflake views and approved extracts"),
        ("2. Cursor context", "Explicit files, project rules, and bounded task"),
        ("3. Human review", "Approve plan and inspect the proposed diff"),
        ("4. Verification", "Read-only query, tests, and analytical checks"),
        ("5. Communication", "Evidence-grounded stakeholder output"),
    ]
    for idx, (title, desc) in enumerate(model_steps, start=1):
        model_cols[idx - 1].markdown(render_step(idx, title, desc, blue=True), unsafe_allow_html=True)

    sf_col, cursor_col = st.columns(2)
    readiness = connection_readiness()
    with sf_col:
        st.markdown("#### Snowflake readiness")
        st.markdown(f'<div class="callout-blue"><b>Execution mode:</b> local deterministic<br><b>Snowflake assets:</b> schema, analytical SQL, connector adapter, and environment-only credential handling<br><b>Live readiness:</b> {"configured" if readiness.live_ready else "not configured in local mode"}</div>', unsafe_allow_html=True)
        if show_advanced or readiness.live_ready:
            upload_confirm = st.checkbox("Synthetic-data write permission confirmed", disabled=not readiness.live_ready)
            if st.button("Upload synthetic GTM table", disabled=not (readiness.live_ready and upload_confirm), use_container_width=True):
                try:
                    result = upload_demo_dataframe(gtm_df)
                    st.success(f"Uploaded {result['rows']:,} rows to {result['table']}.")
                except Exception as exc:
                    st.error(f"Upload failed: {exc}")
        with st.expander("Show Snowflake-native analysis SQL"):
            st.code(SNOWFLAKE_ANALYSIS_PATH.read_text(encoding="utf-8"), language="sql")
    with cursor_col:
        st.markdown("#### Cursor repository governance")
        cursor_prompt = """Review @src/gtm_demo.py, @src/snowflake_adapter.py, and @sql/snowflake_gtm_analysis.sql.
Explain the data flow, identify one low-risk improvement, and propose the smallest patch.
Follow @Cursor Rules: use synthetic data only, never expose credentials, never execute destructive SQL, and provide verification steps. Do not change files until I approve the plan."""
        render_prompt(cursor_prompt)
        render_checklist(
            [
                "Explicit repository context",
                "Plan before edits",
                "Line-by-line diff review",
                "Tests and analytical validation",
                "Document accepted, modified, and rejected suggestions",
            ],
            style="green",
        )
        with st.expander("Show version-controlled Cursor rule"):
            st.code(CURSOR_RULE_PATH.read_text(encoding="utf-8"), language="markdown")

    st.markdown("### Operating model summary")
    st.success(
        "The operating model combines governed data, bounded AI assistance, human verification, reusable enablement material, and measurable adoption criteria."
    )

st.divider()
st.caption("Public and synthetic data only · No financial advice · No company or customer data · Human-reviewed outputs · Snowflake-ready architecture · Local execution")
