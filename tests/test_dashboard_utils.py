from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dashboard_utils import (
    data_quality_checks,
    event_investigation_brief,
    event_severity_frame,
    quality_score,
    safe_readonly_sql,
)
from main import PipelineConfig, engineer_features, offline_stock_data


def sample_processed() -> pd.DataFrame:
    cfg = PipelineConfig(symbols=["TSLA"], start_date="2022-01-01", end_date="2022-08-01")
    raw = offline_stock_data("TSLA", cfg.start_date, cfg.end_date)
    raw["Symbol"] = "TSLA"
    return engineer_features(raw, cfg)


def test_local_sql_guard_accepts_reads_and_blocks_writes():
    assert safe_readonly_sql("SELECT * FROM stock_metrics")
    assert safe_readonly_sql("WITH x AS (SELECT 1) SELECT * FROM x")
    for sql in ["DELETE FROM stock_metrics", "DROP TABLE stock_metrics", "SELECT 1; DELETE FROM stock_metrics"]:
        with pytest.raises(ValueError):
            safe_readonly_sql(sql)


def test_quality_score_and_checks_are_bounded():
    df = sample_processed()
    checks = data_quality_checks(df)
    score = quality_score(df)
    assert len(checks) == 5
    assert 0 <= score <= 100
    assert checks["Passed"].sum() >= 4


def test_event_brief_is_explainable():
    events = event_severity_frame(sample_processed())
    assert not events.empty
    brief = event_investigation_brief(events.iloc[0])
    assert "review flag" in brief["headline"]
    assert len(brief["observed"]) >= 4
    assert len(brief["questions"]) >= 3
