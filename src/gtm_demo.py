from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


REGIONS = ["DACH", "UKI", "France", "Benelux", "Nordics", "Iberia"]
SEGMENTS = ["Enterprise", "Commercial"]
PRODUCT_FAMILIES = ["Platform", "Automation", "Cloud", "AI"]


@dataclass(frozen=True)
class GTMDemoConfig:
    start_date: str = "2025-01-06"
    end_date: str = "2026-07-27"
    seed: int = 20260801


def generate_synthetic_gtm_data(config: GTMDemoConfig | None = None) -> pd.DataFrame:
    """Create deterministic, synthetic GTM metrics for a safe interview demo.

    The data is intentionally fictional and does not represent Red Hat, customers,
    or any real company. Controlled events are inserted so that the dashboard can
    demonstrate explainable anomaly detection and stakeholder reporting.
    """
    cfg = config or GTMDemoConfig()
    rng = np.random.default_rng(cfg.seed)
    weeks = pd.date_range(cfg.start_date, cfg.end_date, freq="W-MON")

    region_factor = {
        "DACH": 1.25,
        "UKI": 1.10,
        "France": 0.92,
        "Benelux": 0.78,
        "Nordics": 0.84,
        "Iberia": 0.72,
    }
    segment_factor = {"Enterprise": 1.35, "Commercial": 0.82}
    product_factor = {"Platform": 1.20, "Automation": 0.94, "Cloud": 1.08, "AI": 0.76}

    rows: list[dict[str, object]] = []
    for week_index, date in enumerate(weeks):
        seasonal = 1 + 0.08 * np.sin(2 * np.pi * week_index / 52)
        trend = 1 + 0.0035 * week_index

        for region in REGIONS:
            for segment in SEGMENTS:
                for product in PRODUCT_FAMILIES:
                    base = 245_000 * region_factor[region] * segment_factor[segment] * product_factor[product]
                    noise = rng.normal(1.0, 0.055)
                    pipeline = max(35_000, base * seasonal * trend * noise)

                    event_label = "normal"
                    event_driver = "No material exception"

                    # Controlled, explainable demo events.
                    if region == "France" and product == "Cloud" and pd.Timestamp("2026-03-02") <= date <= pd.Timestamp("2026-04-27"):
                        pipeline *= 0.62
                        event_label = "pipeline_drop"
                        event_driver = "Synthetic Cloud pipeline contraction"
                    elif region == "DACH" and product == "AI" and pd.Timestamp("2026-05-04") <= date <= pd.Timestamp("2026-06-29"):
                        pipeline *= 1.48
                        event_label = "pipeline_surge"
                        event_driver = "Synthetic AI opportunity surge"
                    elif region == "UKI" and product == "Automation" and pd.Timestamp("2026-01-05") <= date <= pd.Timestamp("2026-02-23"):
                        pipeline *= 0.82
                        event_label = "stalled_pipeline"
                        event_driver = "Synthetic late-stage progression slowdown"

                    win_rate = np.clip(
                        0.22
                        + 0.035 * (region_factor[region] - 0.7)
                        + 0.025 * (segment == "Enterprise")
                        + 0.018 * (product == "Platform")
                        + rng.normal(0, 0.022),
                        0.10,
                        0.48,
                    )
                    if event_label == "pipeline_drop":
                        win_rate *= 0.78
                    if event_label == "pipeline_surge":
                        win_rate *= 1.08

                    conversion_rate = np.clip(win_rate * rng.normal(0.56, 0.045), 0.05, 0.30)
                    bookings = pipeline * win_rate * rng.normal(0.88, 0.055)
                    activity = int(max(20, pipeline / 1_550 + rng.normal(0, 13)))
                    new_opportunities = int(max(4, activity * rng.normal(0.19, 0.025)))
                    forecast_coverage = np.clip(pipeline / max(bookings, 1), 1.2, 8.0)

                    rows.append(
                        {
                            "Week_Start": date,
                            "Region": region,
                            "Segment": segment,
                            "Product_Family": product,
                            "Pipeline_Value_EUR": round(pipeline, 2),
                            "Bookings_EUR": round(bookings, 2),
                            "Win_Rate": round(float(win_rate), 4),
                            "Conversion_Rate": round(float(conversion_rate), 4),
                            "Activity_Count": activity,
                            "New_Opportunities": new_opportunities,
                            "Forecast_Coverage": round(float(forecast_coverage), 2),
                            "Event_Label": event_label,
                            "Event_Driver": event_driver,
                            "Data_Classification": "SYNTHETIC_DEMO_ONLY",
                        }
                    )

    df = pd.DataFrame(rows).sort_values(
        ["Week_Start", "Region", "Segment", "Product_Family"]
    ).reset_index(drop=True)

    group_cols = ["Region", "Segment", "Product_Family"]
    df["Pipeline_Change_4W"] = (
        df.groupby(group_cols, sort=False)["Pipeline_Value_EUR"].pct_change(4)
    )
    df["Bookings_Change_4W"] = (
        df.groupby(group_cols, sort=False)["Bookings_EUR"].pct_change(4)
    )
    df["Win_Rate_Change_4W"] = (
        df.groupby(group_cols, sort=False)["Win_Rate"].diff(4)
    )

    change_abs = df["Pipeline_Change_4W"].abs().fillna(0).clip(upper=1)
    win_change_abs = df["Win_Rate_Change_4W"].abs().fillna(0).clip(upper=0.25) / 0.25
    event_weight = (df["Event_Label"] != "normal").astype(float)
    df["Attention_Score"] = (55 * change_abs + 25 * win_change_abs + 20 * event_weight).round(1)
    df["Requires_Review"] = (df["Attention_Score"] >= 35) | (df["Event_Label"] != "normal")
    return df


def save_synthetic_gtm_data(output_path: Path, config: GTMDemoConfig | None = None) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_gtm_data(config)
    df.to_csv(output_path, index=False)
    return df


def latest_region_summary(df: pd.DataFrame) -> pd.DataFrame:
    latest_week = pd.to_datetime(df["Week_Start"]).max()
    latest = df[pd.to_datetime(df["Week_Start"]) == latest_week]
    summary = (
        latest.groupby("Region", as_index=False)
        .agg(
            Pipeline_Value_EUR=("Pipeline_Value_EUR", "sum"),
            Bookings_EUR=("Bookings_EUR", "sum"),
            Win_Rate=("Win_Rate", "mean"),
            Activity_Count=("Activity_Count", "sum"),
            New_Opportunities=("New_Opportunities", "sum"),
            Attention_Score=("Attention_Score", "mean"),
            Review_Items=("Requires_Review", "sum"),
        )
        .sort_values("Pipeline_Value_EUR", ascending=False)
    )
    summary["Win_Rate"] = summary["Win_Rate"].round(4)
    summary["Attention_Score"] = summary["Attention_Score"].round(1)
    return summary


def deterministic_stakeholder_brief(df: pd.DataFrame, selected_region: str) -> dict[str, object]:
    region = df[df["Region"] == selected_region].copy()
    latest_week = pd.to_datetime(region["Week_Start"]).max()
    current = region[pd.to_datetime(region["Week_Start"]) == latest_week]
    prior_cutoff = latest_week - pd.Timedelta(weeks=4)
    prior = region[pd.to_datetime(region["Week_Start"]) == prior_cutoff]

    current_pipeline = float(current["Pipeline_Value_EUR"].sum())
    prior_pipeline = float(prior["Pipeline_Value_EUR"].sum()) if not prior.empty else np.nan
    pipeline_change = current_pipeline / prior_pipeline - 1 if prior_pipeline and not np.isnan(prior_pipeline) else np.nan
    current_bookings = float(current["Bookings_EUR"].sum())
    current_win_rate = float(current["Win_Rate"].mean())
    review_rows = region[region["Requires_Review"]].sort_values("Week_Start").tail(8)

    if pd.isna(pipeline_change):
        direction = "not yet comparable"
    elif pipeline_change >= 0.03:
        direction = f"up {pipeline_change:.1%} versus four weeks earlier"
    elif pipeline_change <= -0.03:
        direction = f"down {abs(pipeline_change):.1%} versus four weeks earlier"
    else:
        direction = f"broadly stable ({pipeline_change:+.1%}) versus four weeks earlier"

    top_product = (
        current.groupby("Product_Family")["Pipeline_Value_EUR"].sum().sort_values(ascending=False).index[0]
    )
    active_events = review_rows["Event_Label"].value_counts().to_dict()

    return {
        "latest_week": latest_week,
        "pipeline": current_pipeline,
        "bookings": current_bookings,
        "win_rate": current_win_rate,
        "direction": direction,
        "top_product": top_product,
        "review_count": int(current["Requires_Review"].sum()),
        "active_events": active_events,
        "summary": (
            f"{selected_region} latest synthetic pipeline is €{current_pipeline/1_000_000:.2f}M, "
            f"{direction}. Bookings are €{current_bookings/1_000_000:.2f}M with an average "
            f"win rate of {current_win_rate:.1%}. {top_product} is the largest pipeline contributor. "
            f"Analyst review should focus on {int(current['Requires_Review'].sum())} currently flagged slices."
        ),
    }
