from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


READ_ONLY_SQL_PREFIXES = ("SELECT", "WITH", "PRAGMA")
BLOCKED_SQL_TOKENS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "VACUUM",
}


def safe_readonly_sql(sql: str) -> str:
    """Validate a local demo SQL statement before execution.

    The function is deliberately conservative. It accepts a single read-only
    SELECT/WITH/PRAGMA statement and blocks common write/DDL tokens.
    """
    candidate = sql.strip()
    if not candidate:
        raise ValueError("Enter a SQL query.")
    if ";" in candidate.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")
    normalized = re.sub(r"/\*.*?\*/|--[^\n]*", " ", candidate, flags=re.S).upper()
    normalized = re.sub(r"\s+", " ", normalized).strip().rstrip(";")
    if not normalized.startswith(READ_ONLY_SQL_PREFIXES):
        raise ValueError("Only SELECT, WITH, or PRAGMA statements are allowed.")
    tokens = set(re.findall(r"\b[A-Z_]+\b", normalized))
    blocked = sorted(tokens & BLOCKED_SQL_TOKENS)
    if blocked:
        raise ValueError(f"Write or DDL operations are blocked: {', '.join(blocked)}")
    return candidate


def file_sha256(path: Path) -> str:
    if not path.exists():
        return "N/A"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data_quality_checks(stock_df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "Date",
        "Symbol",
        "Close",
        "Volume",
        "Daily_Return",
        "Volatility_20",
        "Risk_Score",
    }
    missing = sorted(required - set(stock_df.columns))
    duplicate_keys = int(stock_df.duplicated(subset=["Date", "Symbol"]).sum()) if {"Date", "Symbol"}.issubset(stock_df) else len(stock_df)
    invalid_prices = int((pd.to_numeric(stock_df.get("Close"), errors="coerce") <= 0).sum()) if "Close" in stock_df else len(stock_df)
    invalid_risk = int((~pd.to_numeric(stock_df.get("Risk_Score"), errors="coerce").between(0, 100)).sum()) if "Risk_Score" in stock_df else len(stock_df)
    hard_required = [col for col in ["Date", "Symbol", "Close", "Volume", "Risk_Score"] if col in stock_df.columns]
    null_core = int(stock_df[hard_required].isna().sum().sum()) if hard_required else len(stock_df)
    checks = [
        ("Required schema", len(missing) == 0, "All required analytical columns are present" if not missing else f"Missing: {', '.join(missing)}"),
        ("Unique entity-time keys", duplicate_keys == 0, f"{duplicate_keys} duplicate Date/Symbol rows"),
        ("Valid close values", invalid_prices == 0, f"{invalid_prices} non-positive close values"),
        ("Risk score bounds", invalid_risk == 0, f"{invalid_risk} values outside 0–100"),
        ("Core field completeness", null_core == 0, f"{null_core} null cells in non-rolling core fields"),
    ]
    return pd.DataFrame(checks, columns=["Check", "Passed", "Detail"])


def quality_score(stock_df: pd.DataFrame) -> float:
    checks = data_quality_checks(stock_df)
    weights = np.array([30, 25, 20, 15, 10], dtype=float)
    passed = checks["Passed"].astype(float).to_numpy()
    return float(np.dot(weights, passed))


def entity_period_summary(stock_df: pd.DataFrame) -> pd.DataFrame:
    ordered = stock_df.sort_values(["Symbol", "Date"]).copy()
    records: list[dict[str, object]] = []
    for symbol, group in ordered.groupby("Symbol", sort=True):
        valid = group.dropna(subset=["Close"])
        first = valid.iloc[0]
        latest = valid.iloc[-1]
        total_return = latest["Close"] / first["Close"] - 1 if first["Close"] else np.nan
        records.append(
            {
                "Symbol": symbol,
                "Start": pd.to_datetime(first["Date"]).date(),
                "End": pd.to_datetime(latest["Date"]).date(),
                "Total_Return": total_return,
                "Latest_Close": latest["Close"],
                "Volatility_20": latest.get("Volatility_20", np.nan),
                "Drawdown": latest.get("Drawdown", np.nan),
                "Risk_Score": latest.get("Risk_Score", np.nan),
                "Return_Anomalies": int(group.get("Return_Anomaly", pd.Series(False, index=group.index)).sum()),
                "Review_Events": int(group[["Return_Anomaly", "Volatility_Spike", "High_Volume_Event"]].any(axis=1).sum()),
            }
        )
    return pd.DataFrame(records)


def risk_driver_breakdown(stock: pd.DataFrame) -> dict[str, float]:
    latest = stock.sort_values("Date").iloc[-1]
    vol_rank = float(stock["Volatility_20"].rank(pct=True).iloc[-1]) if latest.get("Volatility_20") == latest.get("Volatility_20") else 0.0
    drawdown_rank = float((-stock["Drawdown"]).rank(pct=True).iloc[-1]) if latest.get("Drawdown") == latest.get("Drawdown") else 0.0
    anomaly_rank = float(stock["Return_ZScore"].abs().rank(pct=True).iloc[-1]) if latest.get("Return_ZScore") == latest.get("Return_ZScore") else 0.0
    return {
        "Volatility component": round(50 * vol_rank, 1),
        "Drawdown component": round(30 * drawdown_rank, 1),
        "Anomaly component": round(20 * anomaly_rank, 1),
    }


def market_decision_brief(stock: pd.DataFrame, symbol: str) -> dict[str, object]:
    ordered = stock.sort_values("Date").dropna(subset=["Close"])
    latest = ordered.iloc[-1]
    prior_20 = ordered.iloc[-21] if len(ordered) > 21 else ordered.iloc[0]
    change_20 = latest["Close"] / prior_20["Close"] - 1 if prior_20["Close"] else np.nan
    recent_flags = ordered.tail(20)[["Return_Anomaly", "Volatility_Spike", "High_Volume_Event"]].any(axis=1).sum()
    direction = "increased" if change_20 >= 0 else "decreased"
    trend = str(latest.get("Trend_Signal", "Neutral"))
    risk = float(latest.get("Risk_Score", np.nan))
    attention_label = "high" if risk >= 70 else "moderate" if risk >= 40 else "low"
    headline = (
        f"{symbol} {direction} {abs(change_20):.1%} over the latest 20-session comparison window; "
        f"the current trend is {trend.lower()} with {attention_label} analytical attention ({risk:.1f}/100)."
    )
    evidence = [
        f"Latest close: {latest['Close']:.2f}",
        f"20-day volatility: {latest.get('Volatility_20', np.nan):.2%}",
        f"Current drawdown: {latest.get('Drawdown', np.nan):.2%}",
        f"Recent flagged observations: {int(recent_flags)}",
    ]
    questions = [
        "Is the movement broad-based or concentrated in a short event window?",
        "Do volatility and volume signals confirm the same direction?",
        "What external or domain context is required before recommending action?",
    ]
    return {"headline": headline, "evidence": evidence, "questions": questions}


def event_severity_frame(stock_df: pd.DataFrame) -> pd.DataFrame:
    df = stock_df.copy()
    event_mask = df[["Return_Anomaly", "Volatility_Spike", "High_Volume_Event"]].any(axis=1)
    df = df[event_mask].copy()
    if df.empty:
        df["Severity"] = []
        return df
    df["Severity"] = pd.cut(
        df["Risk_Score"],
        bins=[-np.inf, 45, 65, 80, np.inf],
        labels=["Low", "Medium", "High", "Critical"],
    ).astype(str)
    df["Event_Count"] = df[["Return_Anomaly", "Volatility_Spike", "High_Volume_Event"]].sum(axis=1)
    df["Investigation_Priority"] = (df["Risk_Score"] + 8 * (df["Event_Count"] - 1)).clip(upper=100).round(1)
    return df.sort_values(["Date", "Investigation_Priority"], ascending=[False, False])


def event_investigation_brief(row: pd.Series) -> dict[str, list[str] | str]:
    observed: list[str] = [
        f"Entity: {row['Symbol']} on {pd.to_datetime(row['Date']).date()}",
        f"Daily return: {row.get('Daily_Return', np.nan):+.2%}",
        f"20-day volatility: {row.get('Volatility_20', np.nan):.2%}",
        f"Attention score: {row.get('Risk_Score', np.nan):.1f}/100",
    ]
    flags = []
    if bool(row.get("Return_Anomaly", False)):
        flags.append("return anomaly")
    if bool(row.get("Volatility_Spike", False)):
        flags.append("volatility spike")
    if bool(row.get("High_Volume_Event", False)):
        flags.append("high-volume event")
    observed.append("Triggered rules: " + ", ".join(flags))
    questions = [
        "Does the source data contain a quality issue or duplicate observation?",
        "Is the event isolated or part of a sustained pattern?",
        "What business/domain context could explain the movement?",
        "Should the event be escalated, monitored, or closed with documentation?",
    ]
    severity = str(row.get("Severity", "Medium"))
    headlines = {
        "Low": "Low-priority review flag — monitor unless additional context increases concern.",
        "Medium": "Medium-priority review flag — validate scope and supporting signals.",
        "High": "High-priority review flag — investigate the metrics and domain context.",
        "Critical": "Critical review flag — validate promptly and escalate to the appropriate owner if confirmed.",
    }
    return {
        "headline": headlines.get(severity, f"{severity} review flag requiring analyst validation."),
        "observed": observed,
        "questions": questions,
    }


def telemetry_service_summary(telemetry_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        telemetry_df.groupby(["Service", "Software_Version"], as_index=False)
        .agg(
            Rows=("Timestamp", "count"),
            Avg_Latency_ms=("Signal_Latency_ms", "mean"),
            P95_Latency_ms=("Signal_Latency_ms", lambda s: s.quantile(0.95)),
            Avg_Packet_Loss=("Packet_Loss_Rate", "mean"),
            Reconnects=("Reconnect_Count", "sum"),
            Anomalies=("Telemetry_Anomaly", "sum"),
            Avg_Risk=("Telemetry_Risk_Score", "mean"),
        )
        .sort_values(["Anomalies", "Avg_Risk"], ascending=False)
    )
    for col in ["Avg_Latency_ms", "P95_Latency_ms", "Avg_Risk"]:
        summary[col] = summary[col].round(1)
    summary["Avg_Packet_Loss"] = summary["Avg_Packet_Loss"].round(4)
    return summary


def telemetry_incident_brief(telemetry_df: pd.DataFrame, service: str) -> dict[str, object]:
    scope = telemetry_df[telemetry_df["Service"] == service].sort_values("Timestamp")
    anomalies = scope[scope["Telemetry_Anomaly"]]
    latest = scope.iloc[-1]
    return {
        "summary": (
            f"{service} contains {len(scope):,} synthetic observations and {len(anomalies):,} flagged records. "
            f"Latest attention score is {latest['Telemetry_Risk_Score']:.1f}/100 with latency {latest['Signal_Latency_ms']:.1f} ms."
        ),
        "questions": [
            "Is the issue concentrated in a software version or time window?",
            "Do latency, packet loss, and reconnects rise together?",
            "Which owner should validate impact and define the next action?",
        ],
    }


def latest_file_timestamp(paths: Iterable[Path]) -> pd.Timestamp | None:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None
    return pd.Timestamp(max(path.stat().st_mtime for path in existing), unit="s")
