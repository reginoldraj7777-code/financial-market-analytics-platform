from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Time-Series Analytics Platform",
    page_icon="📊",
    layout="wide",
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

CSS = """
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1280px;}
.card {border: 1px solid rgba(120,120,120,.25); border-radius: 14px; padding: 1rem; background: rgba(127,127,127,.06); min-height: 110px;}
.pipeline-step {border: 1px solid rgba(120,120,120,.25); border-radius: 12px; padding: .8rem; background: rgba(127,127,127,.05); min-height: 108px;}
.small-muted {font-size: .9rem; color: #8b95a7;}
.warning-box {border-left: 4px solid #f0ad4e; padding: .8rem 1rem; background: rgba(240,173,78,.08); border-radius: 8px;}
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

    telemetry = pd.read_csv(TELEMETRY_PATH) if TELEMETRY_PATH.exists() else pd.DataFrame()
    if not telemetry.empty:
        telemetry["Timestamp"] = pd.to_datetime(telemetry["Timestamp"])

    stream = pd.read_csv(STREAM_PATH) if STREAM_PATH.exists() else pd.DataFrame()
    return stock, telemetry, stream

@st.cache_data(show_spinner=False)
def run_query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)


def pct(value: float | int | None, digits: int = 2) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:.{digits}f}%"


def render_pipeline_step(number: int, title: str, desc: str) -> str:
    return f"""
    <div class="pipeline-step">
      <b>{number}. {title}</b><br>
      <span class="small-muted">{desc}</span>
    </div>
    """

stock_df, telemetry_df, stream_df = load_data()

st.title("📊 Time-Series Analytics Platform")
st.caption("End-to-end analytics system: ingest → validate → engineer features → detect events → export SQL-ready data → report insights")

if stock_df.empty:
    st.error("Processed data not found. Run the pipeline first.")
    st.code("python src/main.py\nstreamlit run app.py", language="bash")
    st.stop()

symbols = sorted(stock_df["Symbol"].unique())
default_symbol = symbols.index("TSLA") if "TSLA" in symbols else 0
selected_symbol = st.sidebar.selectbox("Entity / symbol", symbols, index=default_symbol)
stock = stock_df[stock_df["Symbol"] == selected_symbol].sort_values("Date").copy()
latest = stock.dropna(subset=["Close"]).iloc[-1]
previous = stock.dropna(subset=["Close"]).iloc[-2] if len(stock.dropna(subset=["Close"])) > 1 else latest

st.sidebar.markdown("### Local project structure")
st.sidebar.code("src/main.py  → pipeline\napp.py       → dashboard\noutputs/     → CSV, SQLite, reports", language="text")
st.sidebar.markdown("### Designed for")
st.sidebar.write("Python scripts • SQL-ready outputs • event detection • automated reports • engineering dashboards")

tabs = st.tabs([
    "1 Executive Overview",
    "2 Time-Series Analysis",
    "3 Event Detection",
    "4 SQL + Reports",
    "5 Pipeline Monitoring",
    "6 Telemetry Extension",
])

with tabs[0]:
    st.subheader("Executive overview")
    st.markdown(
        """
        <div class="card">
        <b>Goal:</b> convert raw multi-entity time-series records into validated data, engineered metrics, explainable event flags, SQL-ready tables, and decision-focused dashboards.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Rows processed", f"{len(stock_df):,}")
    k2.metric("Entities", stock_df["Symbol"].nunique())
    k3.metric("Selected", selected_symbol)
    k4.metric("Latest close", f"{latest['Close']:.2f}", delta=f"{latest['Close'] - previous['Close']:.2f}")
    k5.metric("Latest return", pct(latest["Daily_Return"]))
    k6.metric("Risk score", f"{latest['Risk_Score']:.1f}/100")

    st.markdown("### Architecture")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    steps = [
        ("Ingest", "Load public time-series data with offline fallback"),
        ("Validate", "Check schema, nulls, duplicate entity-time keys"),
        ("Engineer", "Returns, moving averages, volatility, drawdown, risk"),
        ("Detect", "Explainable rules for abnormal returns and spikes"),
        ("Store", "CSV + SQLite tables for SQL/reporting"),
        ("Report", "Dashboard, SQL queries, summary report, run log"),
    ]
    for i, (col, (title, desc)) in enumerate(zip([c1, c2, c3, c4, c5, c6], steps), start=1):
        col.markdown(render_pipeline_step(i, title, desc), unsafe_allow_html=True)

    st.markdown(f"### Latest processed records for {selected_symbol}")
    cols = ["Date", "Symbol", "Close", "Daily_Return", "SMA_20", "SMA_50", "SMA_200", "Volatility_20", "Trend_Signal", "Risk_Score", "Event_Label"]
    st.dataframe(stock[cols].tail(12), hide_index=True, use_container_width=True)

with tabs[1]:
    st.subheader(f"{selected_symbol}: trend, risk, and volatility")
    a, b, c, d = st.columns(4)
    a.metric("Trend", latest["Trend_Signal"])
    b.metric("Long-term trend", latest["Long_Term_Trend"])
    c.metric("20-day volatility", pct(latest["Volatility_20"]))
    d.metric("Drawdown", pct(latest["Drawdown"]))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock["Date"], y=stock["Close"], name="Close", mode="lines"))
    fig.add_trace(go.Scatter(x=stock["Date"], y=stock["SMA_20"], name="SMA 20", mode="lines"))
    fig.add_trace(go.Scatter(x=stock["Date"], y=stock["SMA_50"], name="SMA 50", mode="lines"))
    fig.add_trace(go.Scatter(x=stock["Date"], y=stock["SMA_200"], name="SMA 200", mode="lines"))
    anomaly_rows = stock[stock["Return_Anomaly"]]
    fig.add_trace(go.Scatter(x=anomaly_rows["Date"], y=anomaly_rows["Close"], mode="markers", name="return anomaly", marker=dict(size=9, symbol="x")))
    fig.update_layout(height=520, xaxis_title="Date", yaxis_title="Value", legend_title_text="Series")
    st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        vol_fig = px.line(stock, x="Date", y="Volatility_20", title="20-day rolling volatility")
        vol_fig.update_layout(height=380, yaxis_title="Volatility")
        st.plotly_chart(vol_fig, use_container_width=True)
    with col_right:
        risk_fig = px.line(stock, x="Date", y="Risk_Score", title="Composite risk score")
        risk_fig.update_layout(height=380, yaxis_title="Risk score")
        st.plotly_chart(risk_fig, use_container_width=True)

with tabs[2]:
    st.subheader("Explainable event detection")
    st.write("The rules are intentionally transparent, so a stakeholder can verify why an event was flagged.")

    summary = stock_df.groupby("Symbol").agg(
        Rows=("Date", "count"),
        Return_Anomalies=("Return_Anomaly", "sum"),
        Volatility_Spikes=("Volatility_Spike", "sum"),
        High_Volume_Events=("High_Volume_Event", "sum"),
        Avg_Risk_Score=("Risk_Score", "mean"),
        Max_Risk_Score=("Risk_Score", "max"),
    ).reset_index()
    for col in ["Return_Anomalies", "Volatility_Spikes", "High_Volume_Events"]:
        summary[col] = summary[col].astype(int)
    summary["Avg_Risk_Score"] = summary["Avg_Risk_Score"].round(1)
    summary["Max_Risk_Score"] = summary["Max_Risk_Score"].round(1)

    l, r = st.columns([1.05, 1.55])
    with l:
        st.markdown("### Rules")
        st.markdown(
            """
            - **Return anomaly:** rolling 60-day return z-score ≥ 2.5  
            - **Volatility spike:** 20-day volatility above entity-specific 90th percentile  
            - **High-volume event:** volume above entity-specific 90th percentile  
            - **Risk score:** volatility rank + drawdown severity + return anomaly intensity
            """
        )
        st.markdown("### Summary table")
        st.dataframe(summary, hide_index=True, use_container_width=True)
    with r:
        event_fig = px.bar(
            summary,
            x="Symbol",
            y=["Return_Anomalies", "Volatility_Spikes", "High_Volume_Events"],
            barmode="group",
            title="Flagged event counts by entity",
        )
        event_fig.update_layout(height=460, yaxis_title="Event count", legend_title_text="Event")
        st.plotly_chart(event_fig, use_container_width=True)

    flagged = stock[stock[["Return_Anomaly", "Volatility_Spike", "High_Volume_Event"]].any(axis=1)]
    st.markdown(f"### Recent flagged events for {selected_symbol}")
    st.dataframe(
        flagged[["Date", "Symbol", "Close", "Daily_Return", "Return_ZScore", "Volatility_20", "Risk_Score", "Event_Label"]].tail(20),
        hide_index=True,
        use_container_width=True,
    )

with tabs[3]:
    st.subheader("SQL-ready storage and automated reports")
    st.write("The pipeline exports both files and database tables so the same output can support dashboarding, SQL analysis, and downstream reporting.")

    files_col, report_col = st.columns([1, 1.5])
    with files_col:
        st.markdown("### Generated outputs")
        generated = [
            "processed_stock_metrics.csv",
            "simulated_system_telemetry.csv",
            "event_stream_log.csv",
            "analytics_pipeline.db",
            "automated_summary_report.md",
            "data_quality_report.md",
            "sql_analysis_queries.sql",
        ]
        for fname in generated:
            st.write(f"✅ `{fname}`" if (OUTPUT_DIR / fname).exists() else f"⚠️ `{fname}`")

        st.markdown("### SQL examples")
        if SQL_PATH.exists():
            st.code(SQL_PATH.read_text(encoding="utf-8"), language="sql")
    with report_col:
        st.markdown("### Automated summary report")
        if REPORT_PATH.exists():
            st.markdown(REPORT_PATH.read_text(encoding="utf-8"))
        else:
            st.info("Run python src/main.py to generate the report.")

    if DB_PATH.exists():
        st.markdown("### Live SQL query runner")
        default_query = """SELECT Symbol, COUNT(*) AS rows_processed,
       SUM(CASE WHEN Return_Anomaly = 1 THEN 1 ELSE 0 END) AS return_anomalies,
       ROUND(AVG(Risk_Score), 1) AS avg_risk_score
FROM stock_metrics
GROUP BY Symbol
ORDER BY avg_risk_score DESC;"""
        query = st.text_area("SQL query", default_query, height=140)
        if st.button("Run SQL query"):
            try:
                st.dataframe(run_query(query), hide_index=True, use_container_width=True)
            except Exception as exc:
                st.error(f"SQL error: {exc}")

with tabs[4]:
    st.subheader("Pipeline monitoring and data quality")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Stream batches", len(stream_df) if not stream_df.empty else 0)
    m2.metric("Rows per batch", int(stream_df["Rows_Processed"].mean()) if not stream_df.empty else 0)
    m3.metric("Total stream events", int(stream_df[["Return_Anomalies", "Volatility_Spikes", "High_Volume_Events"]].sum().sum()) if not stream_df.empty else 0)
    m4.metric("Max batch risk", f"{stream_df['Max_Risk_Score'].max():.1f}" if not stream_df.empty else "N/A")

    if not stream_df.empty:
        st.markdown("### Batch processing log")
        st.dataframe(stream_df, hide_index=True, use_container_width=True)
        batch_fig = px.line(stream_df, x="Batch_Number", y=["Return_Anomalies", "Volatility_Spikes", "High_Volume_Events"], title="Detected events per processing batch")
        batch_fig.update_layout(height=420, yaxis_title="Event count")
        st.plotly_chart(batch_fig, use_container_width=True)

    st.markdown("### Data quality report")
    if QUALITY_PATH.exists():
        st.markdown(QUALITY_PATH.read_text(encoding="utf-8"))
    else:
        st.info("Run python src/main.py to generate the data quality report.")

with tabs[5]:
    st.subheader("Telemetry extension: from public time-series data to engineering telemetry")
    st.markdown(
        """
        <div class="warning-box">
        This section uses <b>synthetic telemetry-style data</b>. It is not real sample data. It shows how the same architecture can reuse from public financial time-series data to engineering signals.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if telemetry_df.empty:
        st.info("Run python src/main.py to generate the synthetic reuse dataset.")
    else:
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Telemetry rows", f"{len(telemetry_df):,}")
        t2.metric("Devices", telemetry_df["Device_ID"].nunique())
        t3.metric("Services", telemetry_df["Service"].nunique())
        t4.metric("Anomalies", int(telemetry_df["Telemetry_Anomaly"].sum()))

        ecu_summary = telemetry_df.groupby("Service").agg(
            Rows=("Timestamp", "count"),
            Avg_Latency_ms=("Signal_Latency_ms", "mean"),
            Avg_Packet_Loss=("Packet_Loss_Rate", "mean"),
            Reconnects=("Reconnect_Count", "sum"),
            Anomalies=("Telemetry_Anomaly", "sum"),
            Avg_Risk=("Telemetry_Risk_Score", "mean"),
        ).reset_index()
        ecu_summary["Avg_Latency_ms"] = ecu_summary["Avg_Latency_ms"].round(2)
        ecu_summary["Avg_Packet_Loss"] = ecu_summary["Avg_Packet_Loss"].round(4)
        ecu_summary["Avg_Risk"] = ecu_summary["Avg_Risk"].round(1)

        left, right = st.columns([1, 1.45])
        with left:
            st.markdown("### Service summary")
            st.dataframe(ecu_summary, hide_index=True, use_container_width=True)
        with right:
            tele_fig = px.line(
                telemetry_df.sort_values("Timestamp"),
                x="Timestamp",
                y="Telemetry_Risk_Score",
                color="Service",
                title="Synthetic telemetry risk over time",
            )
            tele_fig.update_layout(height=460, yaxis_title="Risk score")
            st.plotly_chart(tele_fig, use_container_width=True)

        st.markdown("### Concept mapping")
        st.dataframe(
            pd.DataFrame(
                {
                    "Analytics concept": ["Entity", "Timestamp", "Raw signal", "Feature engineering", "Pattern detection", "Report output"],
                    "Financial project": ["Stock symbol", "Trading date", "OHLCV", "returns / moving averages / volatility", "abnormal returns / volatility spikes", "dashboard + SQL report"],
                    "Engineering telemetry": ["Device / Service / software version", "operation timestamp", "latency / packet loss / reconnects", "rolling latency / risk scores / KPIs", "signal drops / high-risk windows", "engineering dashboard + automated report"],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
