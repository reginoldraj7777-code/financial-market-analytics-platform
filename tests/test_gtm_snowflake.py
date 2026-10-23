from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]

from src.gtm_demo import (
    GTMDemoConfig,
    deterministic_stakeholder_brief,
    generate_synthetic_gtm_data,
    latest_region_summary,
)
from src.snowflake_adapter import (
    _validated_identifier,
    connection_readiness,
    run_readonly_query,
    safe_connection_summary,
)


def test_synthetic_gtm_data_is_deterministic_and_safe():
    cfg = GTMDemoConfig(start_date="2026-01-05", end_date="2026-06-29", seed=1234)
    first = generate_synthetic_gtm_data(cfg)
    second = generate_synthetic_gtm_data(cfg)
    pd.testing.assert_frame_equal(first, second)
    required = {
        "Week_Start",
        "Region",
        "Segment",
        "Product_Family",
        "Pipeline_Value_EUR",
        "Bookings_EUR",
        "Win_Rate",
        "Event_Label",
        "Attention_Score",
        "Requires_Review",
        "Data_Classification",
    }
    assert required.issubset(first.columns)
    assert (first["Pipeline_Value_EUR"] > 0).all()
    assert first["Win_Rate"].between(0, 1).all()
    assert set(first["Data_Classification"]) == {"SYNTHETIC_DEMO_ONLY"}


def test_gtm_summary_and_brief_are_grounded():
    df = generate_synthetic_gtm_data()
    summary = latest_region_summary(df)
    assert len(summary) == df["Region"].nunique()
    brief = deterministic_stakeholder_brief(df, "DACH")
    assert brief["pipeline"] > 0
    assert brief["bookings"] > 0
    assert "DACH" in brief["summary"]
    assert "synthetic" in brief["summary"].lower()


def test_cursor_rule_and_docs_exist_with_guardrails():
    rule = ROOT / ".cursor" / "rules" / "analytics-quality.mdc"
    workflow = ROOT / "docs" / "CURSOR_WORKFLOW.md"
    agents = ROOT / "AGENTS.md"
    assert rule.exists() and workflow.exists() and agents.exists()
    text = rule.read_text(encoding="utf-8").lower()
    for phrase in ["synthetic", "never add secrets", "snowflake", "tests", "human owner"]:
        assert phrase in text


def test_snowflake_assets_show_native_sql_and_safe_configuration():
    schema_sql = (ROOT / "sql" / "snowflake_gtm_schema.sql").read_text(encoding="utf-8").upper()
    analysis_sql = (ROOT / "sql" / "snowflake_gtm_analysis.sql").read_text(encoding="utf-8").upper()
    assert "CREATE OR REPLACE VIEW" in schema_sql
    for token in ["QUALIFY", "COUNT_IF", "DIV0", "LAG("]:
        assert token in analysis_sql

    readiness = connection_readiness()
    assert isinstance(readiness.connector_installed, bool)
    summary = safe_connection_summary()
    sensitive_values = [
        os.getenv("SNOWFLAKE_PASSWORD"),
        os.getenv("SNOWFLAKE_TOKEN"),
    ]
    rendered = " ".join(summary.values())
    for value in sensitive_values:
        if value:
            assert value not in rendered


def test_snowflake_identifier_validation():
    assert _validated_identifier("gtm_metrics_demo") == "GTM_METRICS_DEMO"
    for bad in ["bad-name", "1table", "table;drop", "", "has space"]:
        with pytest.raises(ValueError):
            _validated_identifier(bad)


def test_readonly_query_rejects_writes_before_connection_attempt():
    with pytest.raises(ValueError, match="SELECT or WITH"):
        run_readonly_query("DELETE FROM GTM_METRICS_DEMO")
