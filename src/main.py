from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from gtm_demo import save_synthetic_gtm_data

try:
    import yfinance as yf
except Exception:  # keeps the project runnable without internet/dependency issues
    yf = None

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
SYMBOLS = ["AAPL", "MSFT", "TSLA", "NVDA"]

STABLE_SEEDS = {
    "AAPL": 101,
    "MSFT": 202,
    "TSLA": 303,
    "NVDA": 404,
}
BASE_PRICES = {
    "AAPL": 170,
    "MSFT": 290,
    "TSLA": 230,
    "NVDA": 180,
}

@dataclass(frozen=True)
class PipelineConfig:
    symbols: list[str]
    start_date: str
    end_date: str
    return_z_threshold: float = 2.5
    volatility_quantile: float = 0.90
    volume_quantile: float = 0.90
    force_offline: bool = False


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize yfinance output across versions."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df


def offline_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Stable offline fallback so the project always runs without an internet connection."""
    dates = pd.date_range(start_date, end_date, freq="B")
    rng = np.random.default_rng(STABLE_SEEDS.get(symbol, 999))
    returns = rng.normal(loc=0.00055, scale=0.018, size=len(dates))

    # Controlled abnormal windows to make event detection visible and explainable.
    for start in [120, 310, 560]:
        if start >= len(returns):
            continue
        end = min(start + 24, len(returns))
        returns[start:end] += rng.normal(0, 0.040, end - start)

    close = BASE_PRICES.get(symbol, 150) * (1 + returns).cumprod()
    open_ = close * (1 + rng.normal(0, 0.005, len(dates)))
    high = np.maximum(open_, close) * (1 + rng.uniform(0.001, 0.022, len(dates)))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.001, 0.022, len(dates)))
    volume = rng.integers(2_000_000, 140_000_000, len(dates))

    return pd.DataFrame(
        {
            "Date": dates,
            "Open": open_.round(4),
            "High": high.round(4),
            "Low": low.round(4),
            "Close": close.round(4),
            "Volume": volume,
            "Data_Source": "offline_fallback",
        }
    )


def load_raw_stock(symbol: str, config: PipelineConfig) -> pd.DataFrame:
    """Load market time-series data; use offline fallback when internet/API fails."""
    print(f"Loading {symbol}...")
    try:
        if config.force_offline:
            raise RuntimeError("deterministic offline mode requested")
        if yf is None:
            raise RuntimeError("yfinance unavailable")
        df = yf.download(
            symbol,
            start=config.start_date,
            end=config.end_date,
            auto_adjust=False,
            progress=False,
        )
        df = flatten_columns(df)
        if df.empty:
            raise ValueError("No data returned")
        df = df.reset_index()
        df["Data_Source"] = "yfinance"
    except Exception as exc:
        print(f"Using offline fallback for {symbol}: {exc}")
        df = offline_stock_data(symbol, config.start_date, config.end_date)

    df["Date"] = pd.to_datetime(df["Date"])
    df["Symbol"] = symbol
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Date", "Open", "High", "Low", "Close", "Volume"])
    return df.sort_values("Date").reset_index(drop=True)


def engineer_features(df: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
    """Feature engineering and explainable event detection."""
    df = df.copy()
    df["Daily_Return"] = df["Close"].pct_change()
    df["SMA_20"] = df["Close"].rolling(20, min_periods=1).mean()
    df["SMA_50"] = df["Close"].rolling(50, min_periods=1).mean()
    df["SMA_200"] = df["Close"].rolling(200, min_periods=1).mean()
    df["Rolling_Volume_20"] = df["Volume"].rolling(20, min_periods=1).mean()
    df["Volatility_20"] = df["Daily_Return"].rolling(20, min_periods=5).std()
    df["Drawdown"] = df["Close"] / df["Close"].cummax() - 1
    df["Trend_Signal"] = np.select(
        [df["SMA_20"] > df["SMA_50"], df["SMA_20"] < df["SMA_50"]],
        ["Short-term upward", "Short-term downward"],
        default="Neutral",
    )
    df["Long_Term_Trend"] = np.where(df["SMA_50"] >= df["SMA_200"], "Above long MA", "Below long MA")

    rolling_mean = df["Daily_Return"].rolling(60, min_periods=20).mean()
    rolling_std = df["Daily_Return"].rolling(60, min_periods=20).std().replace(0, np.nan)
    df["Return_ZScore"] = (df["Daily_Return"] - rolling_mean) / rolling_std
    df["Return_Anomaly"] = df["Return_ZScore"].abs() >= config.return_z_threshold

    vol_threshold = df["Volatility_20"].quantile(config.volatility_quantile)
    volume_threshold = df["Volume"].quantile(config.volume_quantile)
    df["Volatility_Spike"] = df["Volatility_20"] >= vol_threshold
    df["High_Volume_Event"] = df["Volume"] >= volume_threshold

    # Clear 0-100 attention score: 50% volatility rank, 30% drawdown severity, 20% anomaly intensity.
    vol_rank = df["Volatility_20"].rank(pct=True).fillna(0)
    drawdown_rank = (-df["Drawdown"]).rank(pct=True).fillna(0)
    anomaly_rank = df["Return_ZScore"].abs().rank(pct=True).fillna(0)
    df["Risk_Score"] = (50 * vol_rank + 30 * drawdown_rank + 20 * anomaly_rank).round(1)

    df["Event_Label"] = np.select(
        [df["Return_Anomaly"], df["Volatility_Spike"], df["High_Volume_Event"]],
        ["abnormal_return", "volatility_spike", "high_volume"],
        default="normal",
    )

    ordered_cols = [
        "Date",
        "Symbol",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Data_Source",
        "Daily_Return",
        "SMA_20",
        "SMA_50",
        "SMA_200",
        "Rolling_Volume_20",
        "Volatility_20",
        "Drawdown",
        "Trend_Signal",
        "Long_Term_Trend",
        "Return_ZScore",
        "Return_Anomaly",
        "Volatility_Spike",
        "High_Volume_Event",
        "Risk_Score",
        "Event_Label",
    ]
    return df[ordered_cols]


def validate_dataframe(df: pd.DataFrame) -> dict[str, object]:
    required = {
        "Date",
        "Symbol",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Daily_Return",
        "Volatility_20",
        "Risk_Score",
    }
    missing = sorted(required - set(df.columns))
    duplicate_keys = int(df.duplicated(subset=["Date", "Symbol"]).sum())
    nulls = df[list(required & set(df.columns))].isna().sum().to_dict()
    return {
        "required_columns_present": not missing,
        "missing_columns": missing,
        "duplicate_date_symbol_rows": duplicate_keys,
        "rows": int(len(df)),
        "symbols": int(df["Symbol"].nunique()) if "Symbol" in df else 0,
        "nulls_in_core_columns": {k: int(v) for k, v in nulls.items()},
    }


def create_system_telemetry_data() -> pd.DataFrame:
    """Simulated engineering telemetry data to show reuse potential of the same pipeline pattern.

    This is not external data. It is a synthetic dataset that demonstrates how the same
    analytics design can apply to device-telemetry signals such as latency, packet loss,
    reconnects, Service type, and software version.
    """
    rng = np.random.default_rng(42)
    timestamps = pd.date_range("2024-01-01", periods=1_200, freq="h")
    devices = [f"DEV-{i:04d}" for i in range(1, 51)]
    services = ["API-Gateway", "Data-Ingestion", "Notification-Service", "Reporting-Service"]
    software_versions = ["v1.4", "v1.5", "v2.0"]

    rows = []
    for ts in timestamps:
        for _ in range(rng.integers(1, 5)):
            ecu = rng.choice(services)
            latency = rng.normal(82, 18)
            packet_loss = max(0, rng.normal(0.012, 0.008))
            reconnects = rng.poisson(0.25)

            # Inject explainable abnormal windows.
            if ts.day in [12, 13] and ecu in ["Data-Ingestion", "API-Gateway"]:
                latency += rng.normal(80, 22)
                packet_loss += rng.uniform(0.04, 0.12)
                reconnects += rng.integers(2, 7)

            rows.append(
                {
                    "Timestamp": ts,
                    "Device_ID": rng.choice(devices),
                    "Service": ecu,
                    "Software_Version": rng.choice(software_versions, p=[0.25, 0.45, 0.30]),
                    "Signal_Latency_ms": round(max(4, latency), 3),
                    "Packet_Loss_Rate": round(min(packet_loss, 0.45), 5),
                    "Reconnect_Count": int(reconnects),
                }
            )

    df = pd.DataFrame(rows).sort_values(["Service", "Timestamp"]).reset_index(drop=True)
    df["Latency_Rolling_24h"] = df.groupby("Service")["Signal_Latency_ms"].transform(
        lambda s: s.rolling(24, min_periods=4).mean()
    )
    df["Telemetry_Risk_Score"] = (
        0.45 * df["Signal_Latency_ms"].rank(pct=True)
        + 0.35 * df["Packet_Loss_Rate"].rank(pct=True)
        + 0.20 * df["Reconnect_Count"].rank(pct=True)
    ).mul(100).round(1)
    df["Telemetry_Anomaly"] = df["Telemetry_Risk_Score"] >= 90
    return df.sort_values("Timestamp").reset_index(drop=True)


def simulate_event_stream(stock_df: pd.DataFrame, batch_size: int = 250) -> pd.DataFrame:
    """Simulate batch/stream processing for large-data pipeline discussion."""
    batches = []
    ordered = stock_df.sort_values(["Date", "Symbol"]).reset_index(drop=True)
    for batch_number, start in enumerate(range(0, len(ordered), batch_size), start=1):
        batch = ordered.iloc[start : start + batch_size]
        batches.append(
            {
                "Batch_Number": batch_number,
                "Rows_Processed": int(len(batch)),
                "Start_Date": str(batch["Date"].min().date()),
                "End_Date": str(batch["Date"].max().date()),
                "Return_Anomalies": int(batch["Return_Anomaly"].sum()),
                "Volatility_Spikes": int(batch["Volatility_Spike"].sum()),
                "High_Volume_Events": int(batch["High_Volume_Event"].sum()),
                "Max_Risk_Score": float(batch["Risk_Score"].max()),
                "Processed_At": datetime.now().isoformat(timespec="seconds"),
            }
        )
    return pd.DataFrame(batches)


def save_sqlite(stock_df: pd.DataFrame, telemetry_df: pd.DataFrame, stream_df: pd.DataFrame, gtm_df: pd.DataFrame) -> None:
    db_path = OUTPUT_DIR / "analytics_pipeline.db"
    with sqlite3.connect(db_path) as conn:
        stock_df.to_sql("stock_metrics", conn, if_exists="replace", index=False)
        telemetry_df.to_sql("telemetry_metrics_simulated", conn, if_exists="replace", index=False)
        stream_df.to_sql("pipeline_batch_log", conn, if_exists="replace", index=False)
        gtm_df.to_sql("gtm_metrics_synthetic", conn, if_exists="replace", index=False)

        summary = pd.DataFrame(
            {
                "metric": [
                    "stock_rows",
                    "stock_symbols",
                    "return_anomalies",
                    "volatility_spikes",
                    "high_volume_events",
                    "stream_batches",
                    "simulated_telemetry_rows",
                    "simulated_telemetry_anomalies",
                    "synthetic_gtm_rows",
                    "synthetic_gtm_review_items",
                ],
                "value": [
                    len(stock_df),
                    stock_df["Symbol"].nunique(),
                    int(stock_df["Return_Anomaly"].sum()),
                    int(stock_df["Volatility_Spike"].sum()),
                    int(stock_df["High_Volume_Event"].sum()),
                    len(stream_df),
                    len(telemetry_df),
                    int(telemetry_df["Telemetry_Anomaly"].sum()),
                    len(gtm_df),
                    int(gtm_df["Requires_Review"].sum()),
                ],
            }
        )
        summary.to_sql("pipeline_summary", conn, if_exists="replace", index=False)


def save_sql_examples() -> None:
    sql = """-- SQL examples for the analytics pipeline

-- 1) Latest KPI snapshot per entity
WITH latest AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY Symbol ORDER BY Date DESC) AS rn
    FROM stock_metrics
)
SELECT Symbol, Date AS latest_date,
       ROUND(Close, 2) AS close_price,
       ROUND(Daily_Return, 4) AS daily_return,
       ROUND(Volatility_20, 4) AS volatility_20,
       ROUND(Risk_Score, 1) AS risk_score,
       Trend_Signal, Long_Term_Trend
FROM latest
WHERE rn = 1
ORDER BY risk_score DESC;

-- 2) Explainable event counts by symbol
SELECT Symbol,
       COUNT(*) AS rows_processed,
       SUM(CASE WHEN Return_Anomaly = 1 THEN 1 ELSE 0 END) AS return_anomalies,
       SUM(CASE WHEN Volatility_Spike = 1 THEN 1 ELSE 0 END) AS volatility_spikes,
       SUM(CASE WHEN High_Volume_Event = 1 THEN 1 ELSE 0 END) AS high_volume_events,
       ROUND(AVG(Risk_Score), 1) AS avg_risk_score
FROM stock_metrics
GROUP BY Symbol
ORDER BY volatility_spikes DESC, avg_risk_score DESC;

-- 3) Simulated device-telemetry reuse example
SELECT Service, Software_Version,
       COUNT(*) AS rows_analyzed,
       ROUND(AVG(Signal_Latency_ms), 2) AS avg_latency_ms,
       ROUND(AVG(Packet_Loss_Rate), 4) AS avg_packet_loss,
       SUM(Reconnect_Count) AS reconnect_count,
       SUM(CASE WHEN Telemetry_Anomaly = 1 THEN 1 ELSE 0 END) AS anomalies
FROM telemetry_metrics_simulated
GROUP BY Service, Software_Version
ORDER BY anomalies DESC, avg_latency_ms DESC;

-- 4) Batch pipeline monitoring
SELECT Batch_Number, Rows_Processed, Start_Date, End_Date,
       Return_Anomalies, Volatility_Spikes, High_Volume_Events, Max_Risk_Score
FROM pipeline_batch_log
ORDER BY Batch_Number;
"""
    (OUTPUT_DIR / "sql_analysis_queries.sql").write_text(sql, encoding="utf-8")


def save_reports(stock_df: pd.DataFrame, telemetry_df: pd.DataFrame, stream_df: pd.DataFrame, gtm_df: pd.DataFrame, dq: dict[str, object]) -> None:
    latest = stock_df.sort_values("Date").groupby("Symbol").tail(1)
    top_risk = latest.sort_values("Risk_Score", ascending=False).iloc[0]
    event_summary = stock_df.groupby("Symbol")[["Return_Anomaly", "Volatility_Spike", "High_Volume_Event"]].sum()

    report = f"""# Automated Analytics Summary Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Pipeline Summary

- Stock rows processed: {len(stock_df):,}
- Symbols/entities processed: {stock_df['Symbol'].nunique()}
- Simulated stream batches: {len(stream_df)}
- Return anomalies detected: {int(stock_df['Return_Anomaly'].sum())}
- Volatility spikes detected: {int(stock_df['Volatility_Spike'].sum())}
- High-volume events detected: {int(stock_df['High_Volume_Event'].sum())}

## Highest Latest Risk

- Symbol: {top_risk['Symbol']}
- Latest date: {pd.to_datetime(top_risk['Date']).date()}
- Latest close: {top_risk['Close']:.2f}
- Attention score: {top_risk['Risk_Score']:.1f}/100
- Trend signal: {top_risk['Trend_Signal']} / {top_risk['Long_Term_Trend']}

## Event Summary by Symbol

{event_summary.to_markdown()}

## Data Quality

- Required columns present: {dq['required_columns_present']}
- Duplicate Date/Symbol rows: {dq['duplicate_date_symbol_rows']}
- Missing columns: {dq['missing_columns']}

## Extension Note

The financial dataset is public and time-series based. The same governed pipeline pattern is demonstrated again with synthetic operational telemetry and synthetic EMEA GTM metrics: entities, timestamps, KPIs, explainable review flags, SQL-ready outputs, stakeholder summaries, and dashboards.
"""
    (OUTPUT_DIR / "automated_summary_report.md").write_text(report, encoding="utf-8")

    quality_report = "# Data Quality Report\n\n```json\n" + json.dumps(dq, indent=2, default=str) + "\n```\n"
    (OUTPUT_DIR / "data_quality_report.md").write_text(quality_report, encoding="utf-8")

    run_log = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "stock_rows": int(len(stock_df)),
        "symbols": sorted(stock_df["Symbol"].unique().tolist()),
        "data_sources": sorted(stock_df["Data_Source"].dropna().unique().tolist()),
        "telemetry_rows_simulated": int(len(telemetry_df)),
        "stream_batches": int(len(stream_df)),
        "synthetic_gtm_rows": int(len(gtm_df)),
        "synthetic_gtm_review_items": int(gtm_df["Requires_Review"].sum()),
        "outputs": [
            "processed_stock_metrics.csv",
            "simulated_system_telemetry.csv",
            "event_stream_log.csv",
            "analytics_pipeline.db",
            "automated_summary_report.md",
            "data_quality_report.md",
            "sql_analysis_queries.sql",
            "synthetic_gtm_metrics.csv",
        ],
    }
    (OUTPUT_DIR / "pipeline_run_log.json").write_text(json.dumps(run_log, indent=2), encoding="utf-8")


def run_pipeline(config: PipelineConfig) -> None:
    stock_frames = []
    for symbol in config.symbols:
        raw = load_raw_stock(symbol, config)
        stock_frames.append(engineer_features(raw, config))
    stock_df = pd.concat(stock_frames, ignore_index=True)

    dq = validate_dataframe(stock_df)
    if not dq["required_columns_present"]:
        raise ValueError(f"Missing required columns: {dq['missing_columns']}")

    telemetry_df = create_system_telemetry_data()
    stream_df = simulate_event_stream(stock_df)
    gtm_df = save_synthetic_gtm_data(OUTPUT_DIR / "synthetic_gtm_metrics.csv")

    stock_df.to_csv(OUTPUT_DIR / "processed_stock_metrics.csv", index=False)
    # Compatibility alias for older app versions.
    stock_df.to_csv(OUTPUT_DIR / "processed_data.csv", index=False)
    telemetry_df.to_csv(OUTPUT_DIR / "simulated_system_telemetry.csv", index=False)
    stream_df.to_csv(OUTPUT_DIR / "event_stream_log.csv", index=False)
    save_sqlite(stock_df, telemetry_df, stream_df, gtm_df)
    save_sql_examples()
    save_reports(stock_df, telemetry_df, stream_df, gtm_df, dq)

    print("Pipeline finished successfully.")
    print(f"Stock rows: {len(stock_df):,}")
    print(f"Telemetry rows simulated: {len(telemetry_df):,}")
    print(f"Synthetic GTM rows: {len(gtm_df):,}")
    print(f"Outputs written to: {OUTPUT_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the analytics pipeline.")
    parser.add_argument("--symbols", nargs="*", default=SYMBOLS, help="Symbols to process")
    parser.add_argument("--start", default=START_DATE, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=END_DATE, help="End date YYYY-MM-DD")
    parser.add_argument("--offline", action="store_true", help="Use deterministic offline data for a stable demo")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(PipelineConfig(symbols=args.symbols, start_date=args.start, end_date=args.end, force_offline=args.offline))
